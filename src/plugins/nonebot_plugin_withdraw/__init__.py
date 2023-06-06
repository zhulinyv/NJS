from typing import Any, Dict, List, Tuple, Optional, Union

from nonebot.plugin import PluginMetadata
from nonebot.adapters import Bot as BaseBot
from nonebot import get_driver, on_command, on_notice
from nonebot.params import CommandArg, CommandStart, EventToMe

from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v11 import GroupRecallNoticeEvent
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent

from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import Message as V12Msg
from nonebot.adapters.onebot.v12 import MessageEvent as V12MEvent
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GMEvent
from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12CMEvent
from nonebot.adapters.onebot.v12 import (
    GroupMessageDeleteEvent,
    ChannelMessageDeleteEvent,
)

from .config import Config

withdraw_config = Config.parse_obj(get_driver().config.dict())


__plugin_meta__ = PluginMetadata(
    name="撤回",
    description="自助撤回机器人发出的消息",
    usage="1、@我 撤回 [num1][-num2]，num 为机器人发的倒数第几条消息，从 0 开始，默认为 0\n2、回复需要撤回的消息，回复“撤回”",
    config=Config,
    extra={
        "unique_name": "withdraw",
        "example": "@小Q 撤回\n@小Q 撤回 1\n@小Q 撤回 0-3",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.3.0",
    },
)


msg_ids: Dict[str, List[str]] = {}
max_size = withdraw_config.withdraw_max_size


def get_key(bot: BaseBot, msg_type: str, id: str, sub_id: str = ""):
    key = f"{bot.self_id}_{msg_type}_{id}"
    if sub_id:
        key += f"_{sub_id}"
    return key


async def save_msg_id_v11(
    bot: BaseBot, e: Optional[Exception], api: str, data: Dict[str, Any], result: Any
):
    try:
        if api in ["send_msg", "send_forward_msg"]:
            msg_type = data["message_type"]
            id = data["group_id"] if msg_type == "group" else data["user_id"]
        elif api in ["send_private_msg", "send_private_forward_msg"]:
            msg_type = "private"
            id = data["user_id"]
        elif api in ["send_group_msg", "send_group_forward_msg"]:
            msg_type = "group"
            id = data["group_id"]
        else:
            return
        key = get_key(bot, msg_type, id)
        msg_id = str(result["message_id"])

        if key not in msg_ids:
            msg_ids[key] = []
        msg_ids[key].append(msg_id)
        if len(msg_ids) > max_size:
            msg_ids[key].pop(0)
    except:
        pass


V11Bot.on_called_api(save_msg_id_v11)


async def save_msg_id_v12(
    bot: BaseBot, e: Optional[Exception], api: str, data: Dict[str, Any], result: Any
):
    try:
        if api in ["send_message"]:
            msg_type = data["detail_type"]
            sub_id = ""
            if msg_type == "group":
                id = data["group_id"]
            elif msg_type == "channel":
                id = data["guild_id"]
                sub_id = data["channel_id"]
            else:
                id = data.get("user_id", "")
        else:
            return
        key = get_key(bot, msg_type, id, sub_id)
        msg_id = result["message_id"]

        if key not in msg_ids:
            msg_ids[key] = []
        msg_ids[key].append(msg_id)
        if len(msg_ids) > max_size:
            msg_ids[key].pop(0)
    except:
        pass


V12Bot.on_called_api(save_msg_id_v12)


def remove_msg_id(key: str, msg_id: str):
    print(msg_ids)
    if key in msg_ids and msg_id in msg_ids[key]:
        msg_ids[key].remove(msg_id)
    print(msg_ids)


# 命令前缀为空则需要to_me，否则不需要
def smart_to_me(command_start: str = CommandStart(), to_me: bool = EventToMe()) -> bool:
    return bool(command_start) or to_me


withdraw = on_command("withdraw", aliases={"撤回"}, block=True, rule=smart_to_me)


@withdraw.handle()
async def _(
    bot: Union[V11Bot, V12Bot],
    event: Union[V11MEvent, V12MEvent],
    msg: Union[V11Msg, V12Msg] = CommandArg(),
):
    sub_id = ""
    if isinstance(event, V11MEvent):
        msg_type = event.message_type
        id = str(event.group_id if isinstance(event, V11GMEvent) else event.user_id)
    else:
        msg_type = event.detail_type
        if isinstance(event, V12GMEvent):
            id = event.group_id
        elif isinstance(event, V12CMEvent):
            id = event.guild_id
            sub_id = event.channel_id
        else:
            id = event.user_id

    key = get_key(bot, msg_type, id, sub_id)

    async def delete_message(msg_id: str):
        if isinstance(bot, V11Bot):
            await bot.delete_msg(message_id=int(msg_id))
        else:
            await bot.delete_message(message_id=msg_id)

    if event.reply:
        msg_id = str(event.reply.message_id)
        try:
            await delete_message(msg_id)
            remove_msg_id(key, msg_id)
            return
        except:
            await withdraw.finish("撤回失败，可能已超时")

    def extract_num(text: str) -> Tuple[int, int]:
        if not text:
            return 0, 1

        if text.isdigit() and 0 <= int(text) < len(msg_ids[key]):
            return int(text), int(text) + 1

        nums = text.split("-")[:2]
        nums = [n.strip() for n in nums]
        if len(nums) == 2 and nums[0].isdigit() and nums[1].isdigit():
            start_num = int(nums[0])
            end_num = min(int(nums[1]), len(msg_ids[key]))
            if end_num > start_num:
                return start_num, end_num
        return 0, 1

    text = msg.extract_plain_text().strip()
    start_num, end_num = extract_num(text)

    res = ""
    message_ids = [msg_ids[key][-num - 1] for num in range(start_num, end_num)]
    for message_id in message_ids:
        try:
            await delete_message(message_id)
            msg_ids[key].remove(message_id)
        except:
            if not res:
                res = "撤回失败，可能已超时"
                if end_num - start_num > 1:
                    res = "部分消息" + res
            continue
    if res:
        await withdraw.finish(res)


withdraw_notice = on_notice()


@withdraw_notice.handle()
def _(bot: V11Bot, event: GroupRecallNoticeEvent):
    if str(event.user_id) != bot.self_id:
        return
    msg_id = str(event.message_id)
    id = str(event.group_id)
    key = get_key(bot, "group", id)
    remove_msg_id(key, msg_id)


@withdraw_notice.handle()
def _(bot: V12Bot, event: Union[GroupMessageDeleteEvent, ChannelMessageDeleteEvent]):
    msg_id = event.message_id
    if isinstance(event, GroupMessageDeleteEvent):
        msg_type = "group"
        id = event.group_id
        sub_id = ""
    else:
        msg_type = "channel"
        id = event.guild_id
        sub_id = event.channel_id
    key = get_key(bot, msg_type, id, sub_id)
    remove_msg_id(key, msg_id)
