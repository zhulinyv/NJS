from typing import Any, Dict, Optional

from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.typing import T_State
from nonebot.adapters.qqguild.api.model import Message
from nonebot.adapters.qqguild.exception import ActionFailed
from nonebot.adapters.qqguild import (
    Bot,
    MessageCreateEvent,
    MessageDeleteEvent,
    AtMessageCreateEvent,
)

from ..model import FollowMessage, get_follow_message
from ..adapter import (
    register_allow_apis,
    register_withdraw_func,
    register_withdraw_rule,
    register_get_origin_func,
    register_get_message_func,
)

register_allow_apis("QQ Guild", ["post_messages", "post_messages"])


@register_withdraw_rule("QQ Guild")
async def check_event(event: Event, state: T_State) -> bool:
    if isinstance(event, MessageDeleteEvent) and event.message is not None:
        if follow_messages := await get_follow_message(
            "QQ Guild", str(event.message.id), str(event.message.channel_id)
        ):
            state["follow_messages"] = follow_messages
            return True
    return False


@register_get_origin_func("QQ Guild")
def get_origin_message_id_v11(event: Event) -> Optional[Dict[str, str]]:
    if isinstance(event, (MessageCreateEvent, AtMessageCreateEvent)):
        return {
            "message_id": str(event.id),
            "channel_id": str(event.channel_id),
        }


@register_get_message_func("QQ Guild")
def get_message_id_v12(result: Any) -> Optional[Dict[str, str]]:
    if isinstance(result, Message):
        return {
            "message_id": str(result.id),
            "channel_id": str(result.channel_id),
        }


@register_withdraw_func("QQ Guild")
async def withdraw_v11(bot: Bot, message: FollowMessage):
    assert message.channel_id is not None, "channel_id is None"
    try:
        await bot.delete_message(
            message_id=message.message_id, channel_id=int(message.channel_id)
        )
    except ActionFailed as e:
        logger.opt(colors=True, exception=e).error(
            f"<y>QQ Guild</y> 撤回消息 <m>{message.message_id}</m> 失败"
        )
