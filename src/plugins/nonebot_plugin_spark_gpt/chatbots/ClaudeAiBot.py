import asyncio
from typing import AsyncGenerator

from . import register_chatbot
from .BaseChatBot import BaseChatBot, Permission
from ..type_store.web_config import claude_ai_config
from async_claude_client import ClaudeAiClient

config = claude_ai_config()
client: ClaudeAiClient = None
cookie: dict = {}
locks = {}


@register_chatbot
class Claude_AiBot(BaseChatBot):
    model = "Claude_Ai"
    permission = Permission.paid
    chat: dict = {}

    async def ensure(self):
        global client, cookie, locks
        if self.__hash__() not in locks.keys():
            locks[self.__hash__()] = asyncio.Lock()
        config = claude_ai_config()
        if not client or cookie != config.cookie:
            cookie = config.cookie
            client = await ClaudeAiClient(cookie).init()

    @classmethod
    @property
    def desc(self) -> str:
        return "Claude.ai网站的claude2模型, 有每日免费额度上限"

    @classmethod
    @property
    def able(cls) -> bool:
        config = claude_ai_config()
        return bool(config.cookie)

    async def refresh(self):
        await self.ensure()
        async with locks[self.__hash__()]:
            self.chat = await client.create_new_chat()
            self.save()
        if self.prompt:
            async for text in self.ask(self.prompt + "\n第一次回复只需要回复'我明白了',只需要回复'我明白了'"):
                pass

    async def ask(self, question: str) -> AsyncGenerator:
        await self.ensure()
        if not self.chat:
            await self.refresh()
        async with locks[self.__hash__()]:
            question = self.process_question(question)
            if not self.chat:
                await self.refresh()
            async for text in client.ask_stream(
                question=question, chat_id=self.chat["uuid"]
            ):
                yield text
