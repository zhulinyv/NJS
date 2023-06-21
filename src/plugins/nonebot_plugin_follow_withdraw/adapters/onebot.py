from typing import Any, Dict, Optional

from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot as BotV11
from nonebot.adapters.onebot.v12 import Bot as BotV12
from nonebot.adapters.onebot.v11 import ActionFailed as ActionFailedV11
from nonebot.adapters.onebot.v11 import MessageEvent as MessageEventV11
from nonebot.adapters.onebot.v12 import ActionFailed as ActionFailedV12
from nonebot.adapters.onebot.v12 import MessageEvent as MessageEventV12
from nonebot.adapters.onebot.v11 import GroupRecallNoticeEvent, FriendRecallNoticeEvent
from nonebot.adapters.onebot.v12 import (
    GroupMessageDeleteEvent,
    ChannelMessageDeleteEvent,
    PrivateMessageDeleteEvent,
)

from ..model import FollowMessage, get_follow_message
from ..adapter import (
    register_allow_apis,
    register_withdraw_func,
    register_withdraw_rule,
    register_get_origin_func,
    register_get_message_func,
)

register_allow_apis("OneBot V11", ["send_msg"])
register_allow_apis("OneBot V12", ["send_message"])


@register_withdraw_rule("OneBot V11")
async def withdraw_rule_v11(event: Event, state: T_State) -> bool:
    if isinstance(event, (GroupRecallNoticeEvent, FriendRecallNoticeEvent)):
        if follow_messages := await get_follow_message(
            "OneBot V11", str(event.message_id), None
        ):
            state["follow_messages"] = follow_messages
            return True
    return False


@register_withdraw_rule("OneBot V12")
async def withdraw_rule_v12(event: Event, state: T_State) -> bool:
    if isinstance(
        event,
        (GroupMessageDeleteEvent, ChannelMessageDeleteEvent, PrivateMessageDeleteEvent),
    ):
        if follow_messages := await get_follow_message(
            "OneBot V12",
            event.message_id,
            event.channel_id if isinstance(event, ChannelMessageDeleteEvent) else None,
        ):
            state["follow_messages"] = follow_messages
            return True
    return False


@register_get_origin_func("OneBot V11")
def get_origin_message_id_v11(event: Event) -> Optional[Dict[str, str]]:
    if isinstance(event, MessageEventV11):
        return {
            "message_id": str(event.message_id),
        }


@register_get_origin_func("OneBot V12")
def get_origin_message_id_v12(event: Event) -> Optional[Dict[str, str]]:
    if isinstance(event, MessageEventV12):
        return {
            "message_id": str(event.message_id),
        }


@register_get_message_func("OneBot V11")
@register_get_message_func("OneBot V12")
def get_message_id(result: Dict[str, Any]) -> Optional[Dict[str, str]]:
    if message_id := result.get("message_id"):
        return {
            "message_id": str(message_id),
        }


@register_withdraw_func("OneBot V11")
async def withdraw_v11(bot: BotV11, message: FollowMessage):
    try:
        await bot.delete_msg(message_id=int(message.message_id))
    except ActionFailedV11 as e:
        logger.opt(colors=True, exception=e).error(
            f"<y>OneBot V11</y> 撤回消息 <m>{message.message_id}</m> 失败"
        )


@register_withdraw_func("OneBot V12")
async def withdraw_v12(bot: BotV12, message: FollowMessage):
    try:
        if message.channel_id:
            await bot.delete_message(
                message_id=message.message_id, channel_id=int(message.channel_id)
            )
        else:
            await bot.delete_message(message_id=message.message_id)
    except ActionFailedV12 as e:
        logger.opt(colors=True, exception=e).error(
            f"<y>OneBot V12</y> 撤回消息 <m>{message.message_id}</m> 失败"
        )
