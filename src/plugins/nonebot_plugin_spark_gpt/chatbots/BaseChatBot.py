import asyncio
from enum import Enum
from typing import Optional, AsyncGenerator

from nonebot_plugin_saa_cx import MessageFactory, Text, Image
from pydantic import BaseModel

from ..type_store.web_config import common_config
from ..utils.pastebin import get_url
from ..utils.render import md_to_pic
from ..type_store.msgs_link import msg_links


class Permission(str, Enum):
    black = "black"
    common = "common"
    paid = "paid"


class RateLimit(BaseModel):
    type: str
    limit: int


class BaseChatBot(BaseModel):
    name: str
    owner_id: str
    model: str
    permission: Permission
    prompt_name: Optional[str]
    prompt: Optional[str]
    command_name: Optional[str]
    command: Optional[str]
    stream: Optional[bool] = False
    url: Optional[bool] = False
    pic: Optional[bool] = False
    auto_pic: Optional[bool] = True
    num_limit: Optional[int] = 500

    def __hash__(self):
        return hash(str(self.owner_id) + self.name)

    @classmethod
    @property
    def desc(self) -> str:
        raise NotImplementedError

    @classmethod
    @property
    def able(cls) -> bool:
        raise NotImplementedError

    def process_question(self, question):
        if self.command:
            return self.command + "\n" + question
        else:
            return question

    async def ask_plain(self, *args, **kwargs):
        full_answer = ""
        async for text in self.ask(*args, **kwargs):
            full_answer += text

        message = []
        pic_bool = bool(
            (self.auto_pic and len(full_answer) > self.num_limit) or self.pic
        )

        async def md_to_pic_task(s, width=common_config().pic_width):
            if pic_bool:
                pic = await md_to_pic(s, width)
                return Image(pic)
            else:
                return Text(s)

        async def get_url_task(s):
            if pic_bool and self.url:
                url = await get_url(s)
                return Text(url)

        tasks = []
        tasks.append(asyncio.create_task(md_to_pic_task(full_answer)))
        tasks.append(asyncio.create_task(get_url_task(full_answer)))

        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                message.append(result)

        receipt = await MessageFactory(message).send(at_sender=True)
        msg_links.add_msglink(self.owner_id, receipt.message_id, self)

    async def ask_stream(self, *args, **kwargs):
        full_answer = ""
        answer = ""
        receipt = None
        async for text in self.ask(*args, **kwargs):
            full_answer += text
            answer += text
            times = 0
            if "\n" in answer:
                answer_slice = answer.rsplit("\n", 1)
                if len(answer_slice[0].replace(" ", "").replace("\n", "")) > 80:
                    if receipt and receipt.edit_able:
                        await receipt.edit(Text(full_answer), at_sender=True)
                    else:
                        receipt = await MessageFactory(Text(answer_slice[0])).send(
                            at_sender=True
                        )
                        msg_links.add_msglink(self.owner_id, receipt.message_id, self)
                    times += 1
                    answer = answer_slice[1]
        if answer:
            times += 1
            if receipt and receipt.edit_able:
                await receipt.edit(Text(full_answer), at_sender=True)
            else:
                receipt = await MessageFactory(Text(answer)).send(at_sender=True)
                msg_links.add_msglink(self.owner_id, receipt.message_id, self)

        if times > 1 and self.url:
            url = await get_url(full_answer)
            if receipt and receipt.edit_able:
                await receipt.edit(Text(full_answer), at_sender=True)
            else:
                receipt = await MessageFactory(Text(url)).send(at_sender=True)
                msg_links.add_msglink(self.owner_id, receipt.message_id, self)

    async def ask(self, *args, **kwargs) -> AsyncGenerator:
        raise NotImplementedError

    async def refresh(self, *args, **kwargs):
        raise NotImplementedError

    def save(self):
        from ..type_store.user_chat import users

        users[self.owner_id].save()
