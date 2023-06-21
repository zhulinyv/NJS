from typing import Any, Dict, Optional

from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.typing import T_State
from nonebot.adapters.discord.api.model import MessageGet
from nonebot.adapters.discord.exception import ActionFailed
from nonebot.adapters.discord import Bot, MessageCreateEvent, MessageDeleteEvent

from ..model import FollowMessage, get_follow_message
from ..adapter import (
    register_allow_apis,
    register_withdraw_func,
    register_withdraw_rule,
    register_get_origin_func,
    register_get_message_func,
)

register_allow_apis("Discord", ["create_message"])


@register_withdraw_rule("Discord")
async def withdraw_rule(event: Event, state: T_State) -> bool:
    if not isinstance(event, MessageDeleteEvent):
        return False
    follow_messages = await get_follow_message(
        "Discord", str(event.id), str(event.channel_id)
    )
    if follow_messages:
        state["follow_messages"] = follow_messages
        return True
    return False


@register_get_origin_func("Discord")
def get_origin_message_id(event: Event) -> Optional[Dict[str, str]]:
    if isinstance(event, MessageCreateEvent):
        return {"message_id": str(event.id), "channel_id": str(event.channel_id)}


@register_get_message_func("Discord")
def get_message_id(result: Any) -> Optional[Dict[str, str]]:
    if isinstance(result, MessageGet):
        return {"message_id": str(result.id), "channel_id": str(result.channel_id)}


@register_withdraw_func("Discord")
async def withdraw(bot: Bot, message: FollowMessage):
    assert message.channel_id is not None, "channel_id is None"
    try:
        await bot.delete_message(
            message_id=int(message.message_id), channel_id=int(message.channel_id)
        )
    except ActionFailed as e:
        logger.opt(colors=True, exception=e).error(
            f"<y>Discord</y> 撤回消息 <m>{message.message_id}</m> 失败"
        )
