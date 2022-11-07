from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import EventMessage
from .data_source import extract_member_at


async def message_at_rule(event: GroupMessageEvent, message: Message = EventMessage()):
    return extract_member_at(message=message) or event.reply
