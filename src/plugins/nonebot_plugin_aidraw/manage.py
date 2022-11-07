from argparse import Namespace
from typing import List, Literal, Set, Tuple, Union

from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.permission import SUPERUSER

from .database import setting

add_word = {"添加", "增加", "设置"}
del_word = {"删除", "移除", "解除"}
see_word = {"查看", "检查"}
change_word = {"切换", "管理"}
shield_word = {"屏蔽词", "过滤词"}


def parm_trim(parm: List[str]) -> List[str]:
    return " ".join(parm).replace("，", ",").split(",")


async def group_checker(
    bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent]
) -> bool:
    if await SUPERUSER(bot, event) or isinstance(event, PrivateMessageEvent):
        return True
    group_list: Set[int] = getattr(setting, setting.type)
    check = event.group_id in group_list
    return check if setting.type == "whitelist" else not check


def handle_namelist(
    action: Literal["add", "del"],
    type_: Literal["blacklist", "whitelist"],
    groups: Set[int],
) -> str:
    group_list: Set[int] = getattr(setting, type_)
    if action == "add":
        group_list.update(groups)
        _mode = "添加"
    elif action == "del":
        group_list.difference_update(groups)
        _mode = "删除"
    setattr(setting, type_, group_list)
    setting.save()
    _type = "黑" if type_ == "blacklist" else "白"
    return f"已{_mode} {len(groups)} 个{_type}名单: {','.join(map(str, groups))}"


async def group_manager(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    args: Namespace = ShellCommandArgs(),
):
    if not await SUPERUSER(bot, event):
        matcher.skip()

    manage_type, *groups = args.tags
    action, class_, group = manage_type[:2], manage_type[2:5], manage_type[5:]

    if class_ == "黑名单":
        type_ = "blacklist"
    elif class_ == "白名单":
        type_ = "whitelist"
    else:
        matcher.skip()

    if action in add_word:
        action = "add"
    elif action in del_word:
        action = "del"
    elif action in see_word:
        group_list = getattr(setting, type_)
        msg = (
            f"当前{class_}: {','.join(map(str, group_list))}"
            if group_list
            else f"当前没有{class_}"
        )
        await matcher.finish(msg)
    elif action in change_word:
        setting.type = type_
        setting.save()
        await matcher.finish(f"已切换为 {class_} 模式")
    else:
        matcher.skip()

    groups.insert(0, group)
    groups = parm_trim(groups)

    msg = handle_namelist(
        action, type_, {int(group) for group in groups if group.strip().isdigit()}
    )
    await matcher.finish(msg)


def shield_filter(tags: Message) -> Tuple[str, str]:
    tag_list = str(tags).lower().replace("，", ",").split(",")
    tag_set = {tag.strip() for tag in tag_list}
    filter_tags = ",".join(tag_set & setting.shield)
    safe_tags = ",".join(tag_set - setting.shield)
    return filter_tags, safe_tags


async def shield_manager(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    args: Namespace = ShellCommandArgs(),
):
    if not await SUPERUSER(bot, event):
        matcher.skip()

    manage_type, *words = args.tags
    action, class_, word = manage_type[:2], manage_type[2:5], manage_type[5:]

    if class_ not in shield_word:
        matcher.skip()

    words.insert(0, word)
    words = parm_trim(words)

    if action in add_word:
        setting.shield.update(word.strip() for word in words)
    elif action in del_word:
        setting.shield.difference_update(word.strip() for word in words)
    elif action in see_word:
        msg = f"当前屏蔽词: {','.join(setting.shield)}" if setting.shield else "当前没有设置屏蔽词"
        await matcher.finish(msg)

    setting.save()
    await matcher.finish(f"已{action}屏蔽词: {','.join(words)}")
