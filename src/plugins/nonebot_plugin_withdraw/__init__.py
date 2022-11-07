from typing import Any, Dict, List, Tuple, Optional

from nonebot.plugin import PluginMetadata
from nonebot import get_driver, on_command, on_notice
from nonebot.internal.adapter import Bot as BaseBot
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
    GroupRecallNoticeEvent,
)
from nonebot.params import Command, CommandArg, RawCommand

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
        "version": "0.2.3",
    },
)


msg_ids: Dict[str, List[int]] = {}
max_size = withdraw_config.withdraw_max_size


def get_key(msg_type: str, id: int):
    return f"{msg_type}_{id}"


async def save_msg_id(
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
        key = get_key(msg_type, id)
        msg_id = int(result["message_id"])

        if key not in msg_ids:
            msg_ids[key] = []
        msg_ids[key].append(msg_id)
        if len(msg_ids) > max_size:
            msg_ids[key].pop(0)
    except:
        pass


Bot.on_called_api(save_msg_id)


# 命令前缀为空则需要to_me，否则不需要
def smart_to_me(
    event: MessageEvent, cmd: Tuple[str, ...] = Command(), raw_cmd: str = RawCommand()
) -> bool:
    return not raw_cmd.startswith(cmd[0]) or event.is_tome()


withdraw = on_command("withdraw", aliases={"撤回"}, block=True, rule=smart_to_me)


@withdraw.handle()
async def _(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    if isinstance(event, GroupMessageEvent):
        msg_type = "group"
        id = event.group_id
    else:
        msg_type = "private"
        id = event.user_id
    key = get_key(msg_type, id)

    if event.reply:
        msg_id = event.reply.message_id
        try:
            await bot.delete_msg(message_id=msg_id)
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
            await bot.delete_msg(message_id=message_id)
            msg_ids[key].remove(message_id)
        except:
            if not res:
                res = "撤回失败，可能已超时"
                if end_num - start_num > 1:
                    res = "部分消息" + res
            continue
    if res:
        await withdraw.finish(res)


async def _group_recall(bot: Bot, event: GroupRecallNoticeEvent) -> bool:
    return str(event.user_id) == str(bot.self_id)


withdraw_notice = on_notice(_group_recall)


@withdraw_notice.handle()
async def _(event: GroupRecallNoticeEvent):
    msg_id = event.message_id
    id = event.group_id
    key = get_key("group", id)
    if key in msg_ids and msg_id in msg_ids[key]:
        msg_ids[key].remove(msg_id)
