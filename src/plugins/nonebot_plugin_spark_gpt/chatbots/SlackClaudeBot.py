import asyncio
from typing import AsyncGenerator

from async_claude_client import Slack_Claude_Client, Text, ChatUpdate

from . import register_chatbot
from .BaseChatBot import BaseChatBot, Permission
from ..type_store.web_config import slack_claude_config

config = slack_claude_config()
client: Slack_Claude_Client = None
slack_user_token = config.slack_user_token
channel_id = config.channel_id
claude_id = config.claude_id
pre_msg = config.pre_msg
locks = {}

@register_chatbot
class Slack_ClaudeBot(BaseChatBot):
    model = "Slack_Claude"
    permission = Permission.common
    chat: dict = {}

    @classmethod
    @property
    def desc(self) -> str:
        return "Slack.com 的 Claude 模型"

    @classmethod
    @property
    def able(self) -> bool:
        config = slack_claude_config()
        return bool(config.channel_id and config.claude_id and config.slack_user_token)

    async def ensure(self):
        global client, slack_user_token, channel_id, claude_id, pre_msg, locks
        config = slack_claude_config()
        if self.__hash__() not in locks.keys():
            locks[self.__hash__()] = asyncio.Lock()
        if (
            (not client)
            or config.slack_user_token != slack_user_token
            or config.channel_id != channel_id
            or config.claude_id != claude_id
            or config.pre_msg != pre_msg
        ):
            slack_user_token = config.slack_user_token
            channel_id = config.channel_id
            claude_id = config.claude_id
            pre_msg = config.pre_msg
            client = Slack_Claude_Client(
                slack_user_token, claude_id, channel_id, pre_msg
            )

    async def refresh(self):
        await self.ensure()
        async with locks[self.__hash__()]:
            self.chat = client.create_new_chat()
            self.save()
        if self.prompt:
            async for text in self.ask(self.prompt + "\n第一次回复只需要回复'我明白了',只需要回复'我明白了'"):
                pass

    async def ask(self, question: str) -> AsyncGenerator:
        question = self.process_question(question)
        await self.ensure()
        if not self.chat:
            await self.refresh()
        async with locks[self.__hash__()]:
            async for data in client.ask_stream_raw(question, self.chat):
                if isinstance(data, Text):
                    yield data.content
                elif isinstance(data, ChatUpdate):
                    self.chat = data.content
                    self.save()
