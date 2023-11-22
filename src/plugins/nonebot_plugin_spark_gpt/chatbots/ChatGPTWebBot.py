import asyncio
import json
import uuid
from urllib.parse import urljoin

import aiohttp

from . import register_chatbot
from .BaseChatBot import BaseChatBot, Permission
from ..type_store.web_config import chatgptweb_config

AccessToken = ""
SESSION_TOKEN_KEY = "__Secure-next-auth.session-token"
SessionToken = chatgptweb_config().session_token
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"

LOCKS = {}


class ChatGPTWebBot(BaseChatBot):
    conversation_id: str = None
    parent_message_id: str = str(uuid.uuid4)

    @classmethod
    @property
    def able(cls):
        config = chatgptweb_config()
        return bool(config.api_url and config.session_token)

    async def ask(self, question):
        if (not self.conversation_id) and self.prompt:
            await self.refresh()
        else:
            await self.ensure()

        question = self.process_question(question)

        async with LOCKS[self.__hash__()]:
            async for text in self.base_ask(question):
                yield text
            self.save()

    async def refresh(self):
        await self.ensure()

        async with LOCKS[self.__hash__()]:
            self.conversation_id = None
            self.parent_message_id = str(uuid.uuid4())

            if self.prompt:
                async for text in self.base_ask(
                    self.prompt + "\n首次回复,请只回复'我知道了',请只回复'我知道了'"
                ):
                    pass
            self.save()

    async def ensure(self):
        global SessionToken, LOCKS
        config = chatgptweb_config()
        if not bool(config.session_token and config.api_url):
            raise Exception("模型 ChatGPTWeb 已被禁用,目前无法使用")
        session_token = config.session_token
        if (SessionToken != session_token) or not AccessToken:
            SessionToken = session_token
            await self.refresh_access_token()
        if self.__hash__() not in LOCKS.keys():
            LOCKS[self.__hash__()] = asyncio.Lock()

    async def base_ask(self, question: str):
        async with aiohttp.ClientSession(
            headers={"User-Agent": UA},
        ) as session:
            async with session.post(
                urljoin(chatgptweb_config().api_url, "backend-api/conversation"),
                headers=self.ask_header,
                json=self.build_ask_data(question=question),
                proxy=chatgptweb_config().proxy,
            ) as response:
                if response.status == 429:
                    msg = ""
                    _buffer = bytearray()
                    async for chunk in response.content.iter_any():
                        _buffer.extend(chunk)
                    resp = json.loads(_buffer.decode())
                    if detail := resp.get("detail"):
                        if isinstance(detail, str):
                            msg += "\n" + detail
                    raise Exception("请求过多,请放慢速度" + msg)

                if response.status == 401:
                    raise Exception("token失效,请重新设置token")

                if response.status == 403:
                    raise Exception("API错误,请联系开发者修复")

                if response.status == 404:
                    await self.refresh()
                    raise Exception("会话不存在")

                if response.status >= 400:
                    _buffer = bytearray()
                    async for chunk in response.content.iter_any():
                        _buffer.extend(chunk)
                    resp_text = _buffer.decode()
                    raise Exception(
                        f"ChatGPT 服务器返回了非预期的内容: HTTP{response.status}\n{resp_text[:256]}"
                    )
                saved = False
                last_text = ""
                yield_text = ""
                async for line in response.content:
                    if "internal server error" in str(line):
                        raise Exception("Internal Server Error: ChatGPT服务器内部错误")

                    try:
                        str_data = str(line).strip("b'data: ").rstrip("\\n")
                        if str_data.startswith("{"):
                            data = json.loads(
                                str_data.replace("\\\\", "\\"),
                            )
                            message = data.get("message", {})
                            if (message.get("author", {})).get("role") == "assistant":
                                if not saved:
                                    self.parent_message_id = message.get("id")
                                    self.conversation_id = data.get("conversation_id")
                                    saved = True
                                answer_text = message.get("content", {}).get(
                                    "parts", [""]
                                )[0]
                                yield_text = answer_text[len(last_text) :]
                                last_text = answer_text
                                yield yield_text
                        else:
                            continue
                    except:
                        pass
                if not saved:
                    raise Exception("获取ChatGPTWeb会话和回答失败")

    async def refresh_access_token(self):
        global AccessToken, SessionToken
        async with aiohttp.ClientSession(
            cookies={
                SESSION_TOKEN_KEY: SessionToken,
            },
            connector=aiohttp.TCPConnector(ssl=False),
        ) as session:
            async with session.get(
                urljoin(chatgptweb_config().api_url, "api/auth/session"),
                headers={
                    "User-Agent": UA,
                },
                proxy=chatgptweb_config().proxy,
            ) as response:
                try:
                    resp_json = await response.json()
                    SessionToken = (
                        response.cookies.get(SESSION_TOKEN_KEY) or SessionToken
                    )
                    AccessToken = resp_json["accessToken"]
                except Exception as e:
                    raise Exception(
                        f"ChatGPTWeb在刷新AccessToken时出错:\n 错误信息:{await response.text()} \n 错误原因:{e} "
                    )

    @property
    def ask_header(self):
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {AccessToken}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
            "X-Openai-Assistant-App-Id": "",
            "Connection": "close",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://chat.openai.com/chat",
        }

    def build_ask_data(self, question: str):
        return {
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "author": {"role": "user"},
                    "role": "user",
                    "content": {
                        "content_type": "text",
                        "parts": [question],
                    },
                }
            ],
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_message_id,
            "model": self.basemodel,
            "timezone_offset_min": -480,
        }


@register_chatbot
class GPT35WebBot(ChatGPTWebBot):
    model = "GPT35Web"
    basemodel = "text-davinci-002-render-sha"
    permission = Permission.common

    @classmethod
    @property
    def desc(cls):
        return "ChatGPT Web网页版的默认模型,GPT3.5"


@register_chatbot
class GPT4WebBot(ChatGPTWebBot):
    model = "GPT4Web"
    basemodel = "gpt-4"
    permission = Permission.paid

    @classmethod
    @property
    def able(cls):
        config = chatgptweb_config()
        return bool(config.api_url and config.session_token and config.enable_GPT_4)

    @classmethod
    @property
    def desc(cls):
        return "ChatGPT Web网页版的付费订阅模型,只有订阅plus才可以使用"
