from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from async_bing_client import (
    Bing_Client,
    ConversationStyle,
    Text,
    SuggestRely,
    SourceAttribution,
    Apology,
    Image,
    Limit,
)
from nonebot_plugin_saa_cx import Image as SaaImage
from nonebot_plugin_saa_cx import MessageFactory
from nonebot_plugin_saa_cx import Text as SaaText
from ..type_store.msgs_link import msg_links

from . import register_chatbot
from .BaseChatBot import BaseChatBot, Permission
from ..type_store.web_config import bing_config, common_config
from ..utils import get_url, md_to_pic

Client: Bing_Client = None
Cookie_Hash = hash(str(bing_config().cookie))
LOCKS = {}


async def ensure_client():
    global Client, Cookie_Hash
    config = bing_config()

    if not bool(config.cookie):
        raise Exception("模型Bing 已被禁用,目前无法使用")

    cookie_hash = hash(str(config.cookie))
    if (not Client) or cookie_hash != Cookie_Hash:
        Client = await Bing_Client(cookie=config.cookie, proxy=config.proxy).init()
        Cookie_Hash = cookie_hash


@register_chatbot
class BingBot(BaseChatBot):
    model = "Bing"
    permission = Permission.common
    chat: Optional[dict] = {}
    suggestions: Optional[list[str]] = []

    async def process(self, question):
        # 确保client最新
        await ensure_client()

        # 确保有chat
        if not self.chat:
            await self.refresh()

        # 确保有锁
        if self.__hash__() not in LOCKS.keys():
            LOCKS[self.__hash__()] = asyncio.Lock()

        # 判断是不是建议回复
        if question in ["1", "2", "3"]:
            if len(self.suggestions) >= int(question):
                question = self.suggestions[int(question) - 1]

        if self.command:
            question = self.command + "\n" + question

        return question

    @classmethod
    @property
    def desc(self) -> str:
        return "微软家Bing的gpt4联网模型"

    @classmethod
    @property
    def able(cls):
        return bool(bing_config().cookie)

    async def refresh(self):
        await ensure_client()
        if self.__hash__() not in LOCKS.keys():
            LOCKS[self.__hash__()] = asyncio.Lock()

        async with LOCKS[self.__hash__()]:
            from ..type_store import users

            try:
                self.chat = await Client.create_chat()
                users[self.owner_id].save()
            except Exception as e:
                raise Exception(f"Bing在创建新会话窗口时出错:{e}")

    async def ask_plain(
        self,
        question: str,
        image: str | Path | bytes = None,
    ):
        config = bing_config()
        question = await self.process(question)
        async with LOCKS[self.__hash__()]:
            full_answer = ""
            suggest_text = "\n\n建议回复:  \n"
            suggest_index = 0
            source_text = "\n\n资源链接:  \n"
            source_index = 0
            limit_text = ""
            limit: bool = False
            images = []
            async for data in Client.ask_stream_raw(
                question=question,
                personality=self.prompt,
                conversation_style=ConversationStyle.Creative,
                image=image,
                chat=self.chat,
            ):
                if isinstance(data, Text):
                    full_answer += str(data)
                elif isinstance(data, SuggestRely) and config.suggest_able:
                    self.suggestions.append(str(data))
                    suggest_index += 1
                    suggest_text += f"{suggest_index}.{data}  \n"
                elif isinstance(data, SourceAttribution):
                    source_index += 1
                    source_text += (
                        f"{source_index}.{data.display_name}:{data.see_more_url}\n"
                    )
                elif isinstance(data, Apology):
                    receipt = await MessageFactory(SaaText("\n" + data.content)).send(
                        at_sender=True
                    )
                    msg_links.add_msglink(self.owner_id, receipt.message_id, self)

                elif isinstance(data, Image):
                    images.append(SaaImage(data.url, name=f"{len(images) + 1}.png"))
                elif isinstance(data, Limit):
                    limit_text = f"\n连续对话上限:{data.num_user_messages}/{data.max_num_user_messages}  "
                    if data.num_user_messages >= data.max_num_user_messages:
                        limit = True

                if len(images) >= 4:
                    receipt = await MessageFactory(images).send(at_sender=True)
                    msg_links.add_msglink(self.owner_id, receipt.message_id, self)
                    images = []

            if images:
                receipt = await MessageFactory(images).send(at_sender=True)
                msg_links.add_msglink(self.owner_id, receipt.message_id, self)
            if len(source_text) > 10:
                full_answer += source_text
            if len(suggest_text) > 10 and config.suggest_able:
                full_answer += suggest_text
            if limit_text:
                full_answer += limit_text
            message = []
            pic_bool = bool(
                (self.auto_pic and len(full_answer) > self.num_limit) or self.pic
            )

            # 并行来文转图并获取url
            async def md_to_pic_task(s, width=common_config().pic_width):
                if pic_bool:
                    pic = await md_to_pic(s, width)
                    return SaaImage(pic)
                else:
                    return SaaText(s)

            async def get_url_task(s):
                if pic_bool and self.url:
                    url = await get_url(s)
                    return SaaText(url)

            tasks = []
            tasks.append(asyncio.create_task(md_to_pic_task(full_answer)))
            tasks.append(asyncio.create_task(get_url_task(full_answer)))

            results = await asyncio.gather(*tasks)

            for result in results:
                if result:
                    message.append(result)

            receipt = await MessageFactory(message).send(at_sender=True)
            msg_links.add_msglink(self.owner_id, receipt.message_id, self)
        if limit:
            await self.refresh()
            receipt = await MessageFactory("聊天次数达到上限,已自动刷新对话").send(at_sender=True)
            msg_links.add_msglink(self.owner_id, receipt.message_id, self)

    async def ask_stream(self, question: str, image: str | Path | bytes = None):
        question = await self.process(question)

        async with LOCKS[self.__hash__()]:
            receipt = None
            answer = ""
            full_answer = ""
            suggest_text = "\n\n建议回复:  \n"
            suggest_index = 0
            source_text = "\n\n资源链接:  \n"
            source_index = 0
            limit_text = ""
            images = []
            limit: bool = False
            times = 0
            async for data in Client.ask_stream_raw(
                question=question,
                personality=self.prompt,
                conversation_style=ConversationStyle.Creative,
                image=image,
                chat=self.chat,
            ):
                if isinstance(data, Text):
                    answer += str(data)
                    full_answer += str(data)
                elif isinstance(data, SuggestRely):
                    self.suggestions.append(str(data))
                    suggest_index += 1
                    suggest_text += f"{suggest_index}. {data}  \n"
                elif isinstance(data, SourceAttribution):
                    source_index += 1
                    source_text += (
                        f"{source_index}.{data.display_name}:{data.see_more_url}\n"
                    )
                elif isinstance(data, Apology):
                    answer += str(data)
                    full_answer += str(data)
                elif isinstance(data, Image):
                    images.append(SaaImage(data.url, name=f"{len(images) + 1}.png"))
                elif isinstance(data, Limit):
                    limit_text = f"\n连续对话上限:{data.num_user_messages}/{data.max_num_user_messages}  "
                    if data.num_user_messages >= data.max_num_user_messages:
                        limit = True
                if "\n" in answer:
                    answer_slice = answer.rsplit("\n", 1)
                    if len(answer_slice[0].replace(" ", "").replace("\n", "")) > 80:
                        if receipt and receipt.edit_able:
                            await receipt.edit(SaaText(full_answer), at_sender=True)
                        else:
                            times += 1
                            receipt = await MessageFactory(
                                SaaText(answer_slice[0])
                            ).send(at_sender=True)
                            msg_links.add_msglink(
                                self.owner_id, receipt.message_id, self
                            )

                        answer = answer_slice[1]

                if len(images) >= 4:
                    receipt = await MessageFactory(images).send(at_sender=True)
                    msg_links.add_msglink(self.owner_id, receipt.message_id, self)
                    images = []

            next_text = ""

            if answer:
                next_text += answer
                full_answer += answer
                if receipt and receipt.edit_able:
                    await receipt.edit(SaaText(full_answer), at_sender=True)
            if images:
                receipt = await MessageFactory(images).send(at_sender=True)
                msg_links.add_msglink(self.owner_id, receipt.message_id, self)

            if len(source_text) > 10:
                full_answer += source_text
                next_text += source_text
            if len(suggest_text) > 10:
                full_answer += suggest_text
                next_text += suggest_text
            if limit_text:
                full_answer += limit_text
                next_text += limit_text
            if receipt and receipt.edit_able:
                await receipt.edit(SaaText(full_answer), at_sender=True)
            else:
                times += 1
                receipt = await MessageFactory(SaaText(next_text)).send(at_sender=True)
                msg_links.add_msglink(self.owner_id, receipt.message_id, self)

            if times > 1 and self.url:
                url = await get_url(full_answer)
                if receipt and receipt.edit_able:
                    await receipt.edit(SaaText(full_answer), at_sender=True)
                else:
                    receipt = await MessageFactory(SaaText(url)).send(at_sender=True)
                    msg_links.add_msglink(self.owner_id, receipt.message_id, self)

        if limit:
            await self.refresh()
            receipt = await MessageFactory("聊天次数达到上限,已自动刷新对话").send(at_sender=True)
            msg_links.add_msglink(self.owner_id, receipt.message_id, self)
