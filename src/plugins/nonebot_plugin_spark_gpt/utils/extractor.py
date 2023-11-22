from __future__ import annotations

from typing import Annotated, Tuple,  Any  # noqa: F401

from nonebot import Bot
from nonebot.internal.params import Depends
from nonebot.params import Event
from nonebot_plugin_alconna import UniMsg, Reply
from nonebot_plugin_bind.utils import get_user
from nonebot.exception import SkippedException
from ..type_store.msgs_link import msg_links
from ..type_store.user_chat import users, User, public_user




async def extract_image(event, bot):
    messages = event.get_message()
    adapter_name = bot.adapter.get_name()

    image = ""
    if adapter_name == 'OneBot V11':
        for message in messages:
            if message.type == 'image':
                image = message.data.get("url")
                break
    elif adapter_name == 'Telegram':
        for message in messages:
            if message.type == "photo":
                image_data = await bot.call_api("get_file", file_id=message.data.get("file"))
                image = f"https://api.telegram.org/file/bot{bot.bot_config.token}/{image_data.file_path}"
                break

    elif adapter_name == "Discord":
        if event.attachments:
            for attachment in event.attachments:
                if attachment.content_type.startswith("image"):
                    image = attachment.proxy_url or attachment.url
                    break
    elif adapter_name == 'QQ Guild':
        for message in messages:
            if message.type == 'attachment':
                image = message.data.get('url')
                break
    return image

def GetUser():
    async def dependency(bot: Bot, event: Event):
        bind_user = await get_user(bot, event, auto_create=True)
        return users[bind_user.id]

    return Depends(dependency)


A_User = Annotated[User, GetUser()]

def GetUser():
    async def dependency(bot: Bot, event: Event):
        bind_user = await get_user(bot, event, auto_create=True)
        return users[bind_user.id]

    return Depends(dependency)


A_User = Annotated[User, GetUser()]


def GetQuestionChatUser():
    async def dependency(bot: Bot, event: Event, unimsg: UniMsg):
        from ..type_store.web_config import common_config
        user = None
        msg = event.get_plaintext()
        common_config = common_config()
        if msg.startswith(common_config.private_command):
            bind_user = await get_user(bot, event, auto_create=True)
            user = users[bind_user.id]
            prefix = common_config.private_command
        elif msg.startswith(common_config.public_command):
            user = public_user
            prefix = common_config.public_command
        else:
            try:
                bind_user = await get_user(bot, event, auto_create=True)
                user = users[bind_user.id]
                prefix = common_config.private_command
                message_id = unimsg[Reply][0].id
                chat = msg_links.get_chatbot(user.user_id, message_id)
                return event.get_plaintext(), chat, user
            except Exception:
                try:
                    message_id = unimsg[Reply][0].id
                    chat = msg_links.get_chatbot(public_user.user_id, message_id)
                    return event.get_plaintext(), chat, public_user
                except Exception:
                    pass
        if user:
            for _, chat in user.bots.items():
                full_prefix = f"{prefix}{chat.name}"
                if msg.startswith(full_prefix):
                    return msg[len(full_prefix):], chat, user
        raise SkippedException
    return Depends(dependency)


QCU = Annotated[Tuple[str, Any, User], GetQuestionChatUser()]
