import asyncio
from asyncio import Lock
from typing import AsyncGenerator

from async_poe_client import Poe_Client, ChatCodeUpdate, Text, SuggestRely

from . import register_chatbot
from .BaseChatBot import BaseChatBot, Permission
from ..type_store.web_config import poe_config

config = poe_config()

p_b = config.p_b
form_key = config.formkey
proxy = config.proxy
suggest_able = config.suggest_able
client: Poe_Client = None
url_botname = ["ChatGPT"]
locks = {}


class PoeBot(BaseChatBot):
    url_botname: str
    chat_code: str = None
    suggests: list = None

    async def ensure(self, chat_code: str = ""):
        global client, p_b, form_key, suggest_able, proxy, locks
        if self.__hash__() not in locks.keys():
            locks[self.__hash__()] = Lock()
        config = poe_config()
        suggest_able = config.suggest_able
        if (
            (not client)
            or (p_b != config.p_b)
            or (form_key != config.formkey)
            or (proxy != config.proxy)
        ):
            p_b = config.p_b
            form_key = config.formkey
            proxy = config.proxy
            client = await Poe_Client(p_b=p_b, formkey=form_key, proxy=proxy).create()

    async def refresh(self):
        await self.ensure(self.chat_code)
        if self.chat_code:
            async with locks[self.__hash__()]:
                await client.send_chat_break(
                    url_botname=self.url_botname, chat_code=self.chat_code
                )
        if self.prompt:
            async for data in client.ask_stream_raw(
                url_botname=self.url_botname,
                question=self.prompt + "\n首次回复,只需要回复'我知道了',只需要回复'我知道了'",
                suggest_able=False,
                chat_code=self.chat_code,
            ):
                if isinstance(data, ChatCodeUpdate):
                    self.chat_code = data.content
                    self.save()

    async def ask(self, question: str) -> AsyncGenerator:
        await self.ensure(self.chat_code)
        if (not self.chat_code) and self.prompt:
            await self.refresh()
        if question.isdigit():
            if int(question) <= len(self.suggests):
                question = self.suggests[int(question) - 1]
                
        question = self.process_question(question)
        
        suggests = []
        if self.chat_code:
            while locks[self.__hash__()].locked():
                await asyncio.sleep(1)
        async for data in client.ask_stream_raw(
            url_botname=self.url_botname,
            chat_code=self.chat_code,
            question=question,
            suggest_able=suggest_able,
        ):
            if isinstance(data, Text):
                yield data.content
            elif suggest_able:
                if isinstance(data, SuggestRely):
                    suggests.append(data.content)
            if isinstance(data, ChatCodeUpdate):
                self.chat_code = data.content
                self.save()
        suggest_str = ""
        if suggests:
            suggest_str += "\n\nSuggest Replys:\n"
            index = 1
            for suggest in suggests:
                suggest_str += f"{index}: {suggest}\n"
                index += 1
            yield suggest_str
        self.suggests = suggests


@register_chatbot
class PoeChatGPTBot(PoeBot):
    model = "PoeChatGPT"
    url_botname = "ChatGPT"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的ChatGPT模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey)


@register_chatbot
class PoeClaudeBot(PoeBot):
    model = "PoeClaude"
    url_botname = "Claude-instant"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的Claude-instant模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey)


@register_chatbot
class PoeAssistantBot(PoeBot):
    model = "PoeAssistant"
    url_botname = "Assistant"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于ChatGPT的Assistant模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Assistant)


@register_chatbot
class PoeLlama_2_7bBot(PoeBot):
    model = "PoeLlama_2_7b"
    url_botname = "Llama-2-7b"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Llama-2-7b模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Llama_2_7b)


@register_chatbot
class PoeLlama_2_13bBot(PoeBot):
    model = "PoeLlama_2_13b"
    url_botname = "Llama-2-13b"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Llama-2-13b模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Llama_2_13b)


@register_chatbot
class PoeLlama_2_70bBot(PoeBot):
    model = "PoeLlama_2_70b"
    url_botname = "Llama-2-70b"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Llama-2-70b模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Llama_2_70b)


@register_chatbot
class PoeCode_Llama_7bBot(PoeBot):
    model = "PoeCode_Llama_7b"
    url_botname = "Code-Llama-7b"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Code-Llama-7b模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Code_Llama_7b)


@register_chatbot
class PoeCode_Llama_13bBot(PoeBot):
    model = "PoeCode_Llama_13b"
    url_botname = "Code-Llama-13b"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Code-Llama-13b模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Code_Llama_13b)


@register_chatbot
class PoeCode_Llama_34bBot(PoeBot):
    model = "PoeCode_Llama_34b"
    url_botname = "Code-Llama-34b"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Code-Llama-34b模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Code_Llama_34b)


@register_chatbot
class PoeGoogle_PaLMBot(PoeBot):
    model = "PoeGoogle_PaLM"
    url_botname = "Google-PaLM"
    permission = Permission.common

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Google-PaLM模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Google_PaLM)


@register_chatbot
class PoeChatGPT_16kBot(PoeBot):
    model = "PoeChatGPT_16k"
    url_botname = "ChatGPT-16k"
    permission = Permission.paid

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Google-PaLM模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_ChatGPT_16k)


@register_chatbot
class PoeGPT_4Bot(PoeBot):
    model = "PoeGPT_4"
    url_botname = "GPT-4"
    permission = Permission.paid

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于GPT-4模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_GPT_4)


@register_chatbot
class PoeGPT_4_32kBot(PoeBot):
    model = "PoeGPT_4_32k"
    url_botname = "GPT-4-32k"
    permission = Permission.paid

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于GPT-4-32k模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_GPT_4_32k)


@register_chatbot
class PoeClaude_instant_100kBot(PoeBot):
    model = "PoeClaude_instant_100k"
    url_botname = "Claude-instant-100k"
    permission = Permission.paid

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Claude-instant-100k模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Claude_instant_100k)


@register_chatbot
class PoeClaude_2_100kBot(PoeBot):
    model = "PoeClaude_2_100k"
    url_botname = "Claude-2-100k"
    permission = Permission.paid

    @classmethod
    @property
    def desc(self) -> str:
        return "Poe的免费的无限制的基于Claude_2_100k模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = poe_config()
        return bool(config.p_b and config.formkey and config.enable_Claude_2_100k)
