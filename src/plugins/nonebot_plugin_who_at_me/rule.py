from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import EventMessage
from .data_source import extract_member_at


async def message_at_rule(event: GroupMessageEvent, message: Message = EventMessage()):
    return await extract_member_at(event.group_id, message=message) or event.reply
