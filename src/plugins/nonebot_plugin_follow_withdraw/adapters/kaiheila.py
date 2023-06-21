from typing import Any, Dict, Optional

from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.typing import T_State
from nonebot.adapters.kaiheila import Bot
from nonebot.adapters.kaiheila.exception import ActionFailed
from nonebot.adapters.kaiheila.event import (
    ChannelMessageEvent,
    ChannelDeleteMessageEvent,
)

from ..model import FollowMessage, get_follow_message
from ..adapter import (
    register_allow_apis,
    register_withdraw_func,
    register_withdraw_rule,
    register_get_origin_func,
    register_get_message_func,
)

register_allow_apis("Kaiheila", ["message/create"])


@register_withdraw_rule("Kaiheila")
async def check_event(event: Event, state: T_State) -> bool:
    if isinstance(event, ChannelDeleteMessageEvent):
        if follow_messages := await get_follow_message("Kaiheila", str(event.msg_id)):
            state["follow_messages"] = follow_messages
            return True
    return False


@register_get_origin_func("Kaiheila")
def get_origin_message(event: Event) -> Optional[Dict[str, str]]:
    if isinstance(event, ChannelMessageEvent):
        return {"message_id": str(event.msg_id)}


@register_get_message_func("Kaiheila")
def get_message(result: Dict[str, Any]) -> Optional[Dict[str, str]]:
    if msg_id := result.get("msg_id"):
        return {"message_id": msg_id}


@register_withdraw_func("Kaiheila")
async def withdraw(bot: Bot, message: FollowMessage):
    try:
        await bot.message_delete(msg_id=message.message_id)
    except ActionFailed as e:
        logger.opt(colors=True, exception=e).error(
            f"<y>Kaiheila</y> 撤回消息 <m>{message.message_id}</m> 失败"
        )
