import asyncio
import json
from json import JSONDecodeError

import aiohttp
import tiktoken

from . import register_chatbot
from .BaseChatBot import BaseChatBot, Permission
from ..type_store.web_config import chatgptapi_config

LOCKS = {}
Api_Key = ""


class ChatGPTApiBot(BaseChatBot):
    messages = []

    @classmethod
    @property
    def able(self) -> bool:
        config = chatgptapi_config()
        return bool(config.api_key)

    async def refresh(self):
        self.ensure()
        async with LOCKS[self.__hash__()]:
            self.messages = [
                {
                    "role": "system",
                    "content": self.prompt
                    or "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
                }
            ]
            self.save()

    async def ask(self, question: str):
        async for text in self.base_ask(question):
            yield text

    async def base_ask(self, question: str):
        self.ensure()

        if (not self.messages) and self.prompt:
            await self.refresh()

        async with LOCKS[self.__hash__()]:
            question = self.process_question(question)

            self.messages.append({"role": "user", "content": question})

            self.__truncate_conversation()

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": self.basemodel,
                        "messages": self.messages,
                        "stream": True,
                        "temperature": 0.5,
                        "top_p": 1.0,
                        "presence_penalty": 0.0,
                        "frequency_penalty": 0.0,
                        "n": 1,
                        "user": "user",
                        "max_tokens": self.max_token,
                    },
                    headers={"Authorization": f"Bearer {Api_Key}"},
                ) as resp:
                    if resp.status != 200:
                        raise Exception(
                            f"ChatGPTApi询问时出错: status:{resp.status}, reason: {await resp.text()}"
                        )
                    else:
                        full_content = ""
                        role = ""
                        async for data in resp.content:
                            data = data.decode("utf-8")[6:].rstrip("\n")
                            if data.startswith("{"):
                                try:
                                    data_json = json.loads(data)
                                    choices = data_json.get("choices")

                                    if not choices:
                                        continue

                                    delta = choices[0].get("delta")

                                    if not delta:
                                        continue

                                    role_ = delta.get("role")
                                    if role_:
                                        role = role_

                                    if "content" in delta:
                                        content = delta["content"]
                                        full_content += content
                                        yield content
                                except JSONDecodeError:
                                    pass

                        if not bool(role and content):
                            self.messages.pop()
                        else:
                            self.messages.append({"role": role, "content": content})
                            self.save()

    def __truncate_conversation(self):
        token_count = self.token_count
        token_limit = self.truncate_limit
        while (token_count > token_limit or (token_limit - token_count < 300)) and len(
            self.messages
        ) > 1:
            del self.messages[1]
        self.save()

    @property
    def max_token(self):
        if "gpt-4-32k" == self.basemodel:
            return 31000
        elif "gpt-4" == self.basemodel:
            return 7000
        elif "gpt-3.5-turbo-16k" == self.basemodel:
            return 15000
        else:
            return 4000

    @property
    def token_count(self) -> int:
        tiktoken.model.MODEL_TO_ENCODING["gpt-4"] = "cl100k_base"

        encoding = tiktoken.encoding_for_model(self.basemodel)

        num_tokens = 0
        for message in self.messages:
            # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 5
            for key, value in message.items():
                if value:
                    num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += 5  # role is always required and always 1 token
        num_tokens += 5  # every reply is primed with <im_start>assistant
        return num_tokens

    @property
    def truncate_limit(self) -> int:
        if "gpt-4-32k" == self.basemodel:
            return 30500
        elif "gpt-4" == self.basemodel:
            return 6500
        elif "gpt-3.5-turbo-16k" == self.basemodel:
            return 14500
        else:
            return 3500

    def ensure(self):
        global Api_Key, LOCKS
        config = chatgptapi_config()
        if not bool(config.api_key):
            raise Exception("ChatGPTApi模型已被禁用,目前无法使用")
        else:
            if Api_Key != config.api_key:
                Api_Key = config.api_key
        if self.__hash__() not in LOCKS.keys():
            LOCKS[self.__hash__()] = asyncio.Lock()


@register_chatbot
class GPT3_5ApiBot(ChatGPTApiBot):
    model = "GPT3_5Api"
    basemodel = "gpt-3.5-turbo"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "ChatGPTApi的gpt 3.5 turbo模型"


@register_chatbot
class GPT_3_5_16kBot(ChatGPTApiBot):
    model = "GPT_3_5_16k"
    basemodel = "gpt-3.5-turbo-16k"
    permission = Permission.paid

    @classmethod
    @property
    def desc(self) -> str:
        return "ChatGPTApi的gpt 3.5 turbo 16K模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_3_5_turbo_16k and config.api_key)


@register_chatbot
class GPT_3_5_0301Bot(ChatGPTApiBot):
    model = "GPT_3_5_0301"
    basemodel = "gpt-3.5-turbo-0301"
    permission = Permission.paid

    @classmethod
    @property
    def desc(cls) -> str:
        return "ChatGPTApi的gpt 3.5 turbo 0301模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_3_5_turbo_0301 and config.api_key)


@register_chatbot
class GPT_3_5_0613Bot(ChatGPTApiBot):
    model = "GPT_3_5_0613"
    basemodel = "gpt-3.5-turbo-0613"
    permission = Permission.paid

    @classmethod
    @property
    def desc(cls) -> str:
        return "ChatGPTApi的gpt 3.5 turbo 0613模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_3_5_turbo_0613 and config.api_key)


@register_chatbot
class GPT_3_5_16k_0613Bot(ChatGPTApiBot):
    model = "GPT_3_5_16k_0613"
    basemodel = "gpt-3.5-turbo-16k-0613"
    permission = Permission.paid

    @classmethod
    @property
    def desc(cls) -> str:
        return "ChatGPTApi的gpt 3.5 turbo 16K 0613模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_3_5_turbo_16k_0613 and config.api_key)


@register_chatbot
class GPT_4Bot(ChatGPTApiBot):
    model = "GPT_4"
    basemodel = "gpt-4"
    permission = Permission.paid

    @classmethod
    @property
    def desc(cls) -> str:
        return "ChatGPTApi的gpt 4模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_4 and config.api_key)


@register_chatbot
class GPT_4_0314Bot(ChatGPTApiBot):
    model = "GPT_4_0314"
    basemodel = "gpt-4-0314"
    permission = Permission.paid

    @classmethod
    @property
    def desc(cls) -> str:
        return "ChatGPTApi的gpt 4 0314模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_4_0314 and config.api_key)


@register_chatbot
class GPT_4_32kBot(ChatGPTApiBot):
    model = "GPT_4_32k"
    basemodel = "gpt-4-32k"
    permission = Permission.paid

    @classmethod
    @property
    def desc(cls) -> str:
        return "ChatGPTApi的gpt 4 32K模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_4_32k and config.api_key)


@register_chatbot
class GPT_4_32k_0314Bot(ChatGPTApiBot):
    model = "GPT_4_32k_0314"
    basemodel = "gpt-4-32k-0314"
    permission = Permission.paid

    @classmethod
    @property
    def desc(cls) -> str:
        return "ChatGPTApi的gpt 4 32K 0314模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_4_32k_0314 and config.api_key)


@register_chatbot
class GPT_4_0613Bot(ChatGPTApiBot):
    model = "GPT_4_0613"
    basemodel = "gpt-4-0613"
    permission = Permission.paid

    @classmethod
    @property
    def desc(cls) -> str:
        return "ChatGPTApi的gpt 4 0613模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_4_0613 and config.api_key)


@register_chatbot
class GPT_4_32k_0613Bot(ChatGPTApiBot):
    model = "GPT_4_32k_0613"
    basemodel = "gpt-4-32k-0613"
    permission = Permission.paid

    @classmethod
    @property
    def desc(cls) -> str:
        return "ChatGPTApi的gpt 4 32K 0613模型"

    @classmethod
    @property
    def able(cls) -> bool:
        config = chatgptapi_config()
        return bool(config.enable_gpt_4_32k_0613 and config.api_key)
