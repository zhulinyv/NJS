import re
import random
from typing import Dict, List, Tuple
from asyncio import sleep

from nonebot import on_regex, on_command, on_message
from nonebot.params import CommandArg, RegexGroup
from nonebot.typing import T_State, T_Handler
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import (
    GROUP_ADMIN,
    GROUP_OWNER,
    PRIVATE_FRIEND,
)

from .util import to_json, parse_msg, save_and_convert_img
from .models import MatchType, IncludeCQCodeError
from .data_source import word_bank as wb

reply_type = "random"


def get_session_id(event: MessageEvent) -> str:
    if isinstance(event, GroupMessageEvent):
        return f"group_{event.group_id}"
    else:
        return f"private_{event.user_id}"


def wb_match_rule(event: MessageEvent, state: T_State) -> bool:
    msgs = wb.match(get_session_id(event), event.get_message(), to_me=event.is_tome())
    if not msgs:
        return False
    if reply_type == "random":
        msgs = [random.choice(msgs)]
    state["replies"] = msgs
    return True


wb_matcher = on_message(wb_match_rule, priority=99)


@wb_matcher.handle()
async def handle_wb(event: MessageEvent, state: T_State):
    msgs: List[Message] = state["replies"]
    for msg in msgs:
        await wb_matcher.finish(
            Message.template(msg).format(
                nickname=event.sender.card or event.sender.nickname,
                sender_id=event.sender.user_id,
            )
        )


PERM_EDIT = GROUP_ADMIN | GROUP_OWNER | PRIVATE_FRIEND | SUPERUSER
PERM_GLOBAL = SUPERUSER


wb_set_cmd = on_regex(
    r"^((?:模糊|正则|@)*)\s*问\s*(\S+.*?)\s*答\s*(\S+.*?)\s*$",
    flags=re.S,
    block=True,
    priority=11,
    permission=PERM_EDIT,
)

wb_set_cmd_gl = on_regex(
    r"^((?:全局|模糊|正则|@)*)\s*问\s*(\S+.*?)\s*答\s*(\S+.*?)\s*$",
    flags=re.S,
    block=True,
    priority=10,
    permission=PERM_GLOBAL,
)


@wb_set_cmd.handle()
@wb_set_cmd_gl.handle()
async def wb_set(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    matched: Tuple[str, ...] = RegexGroup(),
):
    flag, key, value = matched
    type_ = (
        MatchType.regex
        if "正则" in flag
        else MatchType.include
        if "模糊" in flag
        else MatchType.congruence
    )
    require_to_me: bool = False
    if "@" in flag:  # @问需要to_me才会触发
        require_to_me = True
    else:
        # 以昵称开头的词条视为需要to_me
        for name in bot.config.nickname:
            if key.startswith(name):
                key = key.replace(name, "", 1)
                require_to_me = True
                break

    value = Message(parse_msg(value))  # 替换/at, /self, /atself
    await save_and_convert_img(value, wb.img_dir)  # 保存回答中的图片

    index = get_session_id(event)
    index = "0" if "全局" in flag else index
    try:
        wb.set(index, type_, Message(key), value, require_to_me)
        await matcher.finish(message="我记住了~")
    except IncludeCQCodeError:
        await matcher.finish("正则匹配中不允许带有CQ码")


wb_del_cmd = on_regex(
    r"^删除\s*((?:模糊|正则|@)*)\s*词条\s*(\S+.*?)\s*$",
    flags=re.S,
    block=True,
    priority=11,
    permission=PERM_EDIT,
)

wb_del_cmd_gl = on_regex(
    r"^删除\s*((?:全局|模糊|正则|@)*)\s*词条\s*(\S+.*?)\s*$",
    flags=re.S,
    block=True,
    priority=10,
    permission=PERM_GLOBAL,
)


@wb_del_cmd.handle()
@wb_del_cmd_gl.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    matched: Tuple[str, ...] = RegexGroup(),
):
    flag, key = matched
    type_ = (
        MatchType.regex
        if "正则" in flag
        else MatchType.include
        if "模糊" in flag
        else MatchType.congruence
    )
    require_to_me: bool = False
    if "@" in flag:
        require_to_me = True
    else:
        for name in bot.config.nickname:
            if key.startswith(name):
                key = key.replace(name, "", 1)
                require_to_me = True
                break

    index = get_session_id(event)
    index = "0" if "全局" in flag else index
    res = wb.delete(index, type_, Message(key), require_to_me)
    if res:
        await matcher.finish("删除成功~")


def wb_clear(type_: str = "") -> T_Handler:
    async def wb_clear_(
        event: MessageEvent, state: T_State, arg: Message = CommandArg()
    ):
        msg = arg.extract_plain_text().strip()
        if msg:
            state["is_sure"] = msg

        if not type_:
            index = get_session_id(event)
            keyword = "群聊" if isinstance(event, GroupMessageEvent) else "个人"
        else:
            index = "0" if type_ == "全局" else None
            keyword = type_
        state["index"] = index  # 为 "0" 表示全局词库, 为 None 表示全部词库
        state["keyword"] = keyword  # 群聊/个人/全局/全部

    return wb_clear_


wb_clear_cmd = on_command(
    "删除词库",
    block=True,
    priority=10,
    permission=PERM_EDIT,
    handlers=[wb_clear()],
)
wb_clear_cmd_gl = on_command(
    "删除全局词库", block=True, priority=10, permission=PERM_GLOBAL, handlers=[wb_clear("全局")]
)
wb_clear_bank = on_command(
    "删除全部词库", block=True, priority=10, permission=PERM_GLOBAL, handlers=[wb_clear("全部")]
)


prompt_clear = Message.template("此命令将会清空您的{keyword}词库，确定请发送 yes")


@wb_clear_cmd.got("is_sure", prompt=prompt_clear)
@wb_clear_cmd_gl.got("is_sure", prompt=prompt_clear)
@wb_clear_bank.got("is_sure", prompt=prompt_clear)
async def _(matcher: Matcher, state: T_State):
    is_sure = str(state["is_sure"]).strip()
    index = state["index"]
    if is_sure == "yes":
        res = wb.clear(index)
        if res:
            await matcher.finish(Message.template("删除{keyword}词库成功~"))
    else:
        await matcher.finish("命令取消")


wb_search_cmd = on_regex(
    r"^查询\s*((?:群|用户)*)\s*(\d*)\s*((?:全局)?(?:模糊|正则)?@?)\s*词库\s*(.*?)\s*$",
    flags=re.S,
    block=True,
    priority=10,
    permission=PERM_GLOBAL,
)
wb_search_cmd_user = on_regex(
    r"^查询\s*((?:模糊|正则)?@?)\s*词库\s*(.*?)\s*$",
    flags=re.S,
    block=True,
    priority=11,
    permission=PERM_EDIT,
)


@wb_search_cmd_user.handle()
@wb_search_cmd.handle()
async def wb_search(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    matched: Tuple[str, ...] = RegexGroup(),
):
    if len(matched) == 2:
        type = "群" if isinstance(event, GroupMessageEvent) else "用户"
        id = event.group_id if isinstance(event, GroupMessageEvent) else event.user_id
        flag, key = matched
    else:
        type, id, flag, key = matched

    nickname = event.sender.card or event.sender.nickname

    if type and not id:
        await matcher.finish(f"请填写{type}ID")

    index = (
        "0"
        if "全局" in flag
        else get_session_id(event)
        if not type
        else {"群": "group", "用户": "private"}[type] + f"_{id}"
    )
    type_ = (
        MatchType.regex
        if "正则" in flag
        else MatchType.include
        if "模糊" in flag
        else MatchType.congruence
    )
    if not (require_to_me := "@" in flag):
        for name in bot.config.nickname:
            if key.startswith(name):
                key = key.replace(name, "", 1)
                require_to_me = True
                break

    entrys = wb.select(index, type_, Message(key), require_to_me)

    if not entrys:
        await matcher.finish("词库中未找到词条~")

    if isinstance(event, GroupMessageEvent):
        forward_msg: List[Dict] = []
        for entry in entrys:
            forward_msg.append(
                to_json(
                    "问: " + entry.key, nickname or "user" + " 答:", str(event.user_id)
                )
            )
            for value in entry.values:
                forward_msg.append(
                    to_json(
                        value,
                        "bot回复",
                        str(bot.self_id),
                    )
                )
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=forward_msg
        )
    else:
        for entry in entrys:
            msg_temp = "问: " + Message(entry.key) + " 答:"
            for value in entry.values:
                msg_temp += "\n" + Message.template("{value}").format(value=value)
            await matcher.send(msg_temp)
            await sleep(1)
