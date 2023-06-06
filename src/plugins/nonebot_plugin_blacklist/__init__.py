import asyncio, random
from pathlib import Path
from typing import Literal

from nonebot import get_driver, on_command, on_notice
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    Event,
    MessageEvent,
    GroupMessageEvent,
    GroupBanNoticeEvent,
)
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg, ArgStr

import ujson as json

superusers = get_driver().config.superusers

file_path = Path() / 'data' / 'blacklist' / 'blacklist.json'
file_path.parent.mkdir(parents=True, exist_ok=True)

blacklist = (
    json.loads(file_path.read_text('utf-8'))
    if file_path.is_file()
    else {
        'grouplist': [],
        'userlist': [],
        'ban_auto_sleep': True
    }
)


def save_blacklist() -> None:
    file_path.write_text(json.dumps(blacklist), encoding='utf-8')


if not blacklist.get('ban_auto_sleep'):
    if 'ban_auto_sleep' in blacklist['grouplist']:
        blacklist['grouplist'] = [ uid for uid in blacklist['grouplist'] if uid != 'ban_auto_sleep' ]
        blacklist.update({'ban_auto_sleep': True})
    else:
        blacklist.update({'ban_auto_sleep': False})
    save_blacklist()


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


@event_preprocessor
def blacklist_processor(event: Event):
    if (uid := str(vars(event).get('user_id', None))) in superusers:
        return
    if (gid := str(vars(event).get('group_id', None))) and gid in blacklist['grouplist']:
        logger.debug(f'群聊 {gid} 在黑名单中, 忽略本次消息')
        raise IgnoredException('黑名单群组')
    elif uid in blacklist['userlist']:
        logger.debug(f'用户 {uid} 在黑名单中, 忽略本次消息')
        raise IgnoredException('黑名单用户')


def handle_msg(
    arg,
    mode: Literal['add', 'del'],
    type_: Literal['userlist', 'grouplist'],
) -> str:
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        return '用法: \n拉黑(解禁)用户(群) qq qq1 qq2 ...'
    for uid in uids:
        if not is_number(uid):
            return '参数错误, id必须是数字..'
    msg = handle_blacklist(uids, mode, type_)
    return msg


def handle_blacklist(
    uids: list,
    mode: Literal['add', 'del'],
    type_: Literal['userlist', 'grouplist'],
) -> str:
    if mode == 'add':
        blacklist[type_].extend(uids)
        blacklist[type_] = list(set(blacklist[type_]))
        _mode = '拉黑'
    elif mode == 'del':
        blacklist[type_] = [uid for uid in blacklist[type_] if uid not in uids]
        _mode = '解禁'
    save_blacklist()
    _type = '用户' if type_ == 'userlist' else '群聊'
    return f"已{_mode} {len(uids)} 个{_type}: {', '.join(uids)}"


add_userlist = on_command('拉黑用户', aliases={'屏蔽用户'}, permission=SUPERUSER, priority=1, block=True)

@add_userlist.handle()
async def add_user_list(event: MessageEvent, arg: Message = CommandArg()):
    if uids := [at.data['qq'] for at in event.get_message()['at']]:
        msg = handle_blacklist(uids, 'add', 'userlist')
        await add_userlist.finish(msg)
    msg = handle_msg(arg, 'add', 'userlist')
    await add_userlist.finish(msg)


add_grouplist = on_command('拉黑群', aliases={'屏蔽群'}, permission=SUPERUSER, priority=1, block=True)

@add_grouplist.handle()
async def add_group_list(arg: Message = CommandArg()):
    msg = handle_msg(arg, 'add', 'grouplist')
    await add_grouplist.finish(msg)


del_userlist = on_command('解禁用户', aliases={'解封用户'}, permission=SUPERUSER, priority=1, block=True)

@del_userlist.handle()
async def del_user_list(event: MessageEvent, arg: Message = CommandArg()):
    if uids := [at.data['qq'] for at in event.get_message()['at']]:
        msg = handle_blacklist(uids, 'del', 'userlist')
        await del_userlist.finish(msg)
    msg = handle_msg(arg, 'del', 'userlist')
    await del_userlist.finish(msg)


del_grouplist = on_command('解禁群', aliases={'解封群'}, permission=SUPERUSER, priority=1, block=True)

@del_grouplist.handle()
async def del_group_list(arg: Message = CommandArg()):
    msg = handle_msg(arg, 'del', 'grouplist')
    await del_grouplist.finish(msg)


check_userlist = on_command('查看用户黑名单', permission=SUPERUSER, priority=1, block=True)

@check_userlist.handle()
async def check_user_list():
    await check_userlist.finish(f"当前已屏蔽 {len(blacklist['userlist'])} 个用户: {', '.join(blacklist['userlist'])}")


check_grouplist = on_command('查看群聊黑名单', permission=SUPERUSER, priority=1, block=True)

@check_grouplist.handle()
async def check_group_list():
    await check_grouplist.finish(f"自觉静默: {'开' if blacklist['ban_auto_sleep'] else '关'}\n当前已屏蔽 {len(blacklist['grouplist'])} 个群聊: {', '.join(blacklist['grouplist'])}")


add_group = on_command('/静默', permission=SUPERUSER, priority=1, block=True)

@add_group.handle()
async def add_group_(event: GroupMessageEvent):
    handle_blacklist([f'{event.group_id}'], 'add', 'grouplist')
    await add_group.finish('那我先去睡觉了...')


del_group = on_command('/响应', permission=SUPERUSER, priority=1, block=True)

@del_group.handle()
async def del_group_(event: GroupMessageEvent):
    handle_blacklist([f'{event.group_id}'], 'del', 'grouplist')
    await del_group.finish('呜......醒来力...')


add_all_group = on_command('拉黑所有群', aliases={'屏蔽所有群'}, permission=SUPERUSER, priority=1, block=True)

@add_all_group.handle()
async def add_all_group_(bot: Bot):
    gl = await bot.get_group_list()
    gids = ['{group_id}'.format_map(g) for g in gl]
    handle_blacklist(gids, 'add', 'grouplist')
    await add_all_group.finish(f'已拉黑 {len(gids)} 个群聊')


del_all_group = on_command('解禁所有群', aliases={'解封所有群'}, permission=SUPERUSER, priority=1, block=True)

@del_all_group.handle()
async def del_all_group_(bot: Bot):
    gl = await bot.get_group_list()
    gids = ['{group_id}'.format_map(g) for g in gl]
    handle_blacklist(gids, 'del', 'grouplist')
    await del_all_group.finish(f'已解禁 {len(gids)} 个群聊')


add_all_friend = on_command('拉黑所有好友', aliases={'屏蔽所有好友'}, permission=SUPERUSER, priority=1, block=True)

@add_all_friend.handle()
async def add_all_friend_(bot: Bot):
    gl = await bot.get_friend_list()
    uids = ['{user_id}'.format_map(g) for g in gl]
    handle_blacklist(uids, 'add', 'userlist')
    await add_all_friend.finish(f'已拉黑 {len(uids)} 个用户')


del_all_friend = on_command('解禁所有好友', aliases={'解封所有好友'}, permission=SUPERUSER, priority=1, block=True)

@del_all_friend.handle()
async def del_all_friend_(bot: Bot):
    gl = await bot.get_friend_list()
    uids = ['{user_id}'.format_map(g) for g in gl]
    handle_blacklist(uids, 'del', 'userlist')
    await del_all_friend.finish(f'已解禁 {len(uids)} 个用户')


reset_blacklist = on_command('重置黑名单', aliases={'清空黑名单'}, permission=SUPERUSER, priority=1, block=True)

@reset_blacklist.got('flag', prompt='确定重置黑名单? (Y/n)')
async def reset_list(flag: str = ArgStr('flag')):
    if flag.lower().strip() in ['y', 'yes', 'true']:
        blacklist['userlist'].clear()
        blacklist['grouplist'].clear()
        save_blacklist()
        await reset_blacklist.finish('黑名单已重置')
    else:
        await reset_blacklist.finish('操作已取消')


@on_notice(priority=2, block=False).handle()
async def _(bot: Bot, event: GroupBanNoticeEvent):
    if blacklist['ban_auto_sleep'] and event.is_tome() and event.duration:
        handle_blacklist([f'{event.group_id}'], 'add', 'grouplist')
        for superuser in bot.config.superusers:
            await bot.send_private_msg(
                user_id=int(superuser),
                message=f'ⓘ在群聊 {event.group_id} 受到禁言, 已自动拉黑该群聊.'
            )
            await asyncio.sleep(random.random()+1)


ban_auto_sleep = on_command('自觉静默', permission=SUPERUSER, priority=1, block=True)

@ban_auto_sleep.handle()
async def _(arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    if not msg or msg.startswith('开'):
        blacklist['ban_auto_sleep'] = True
        text = '自觉静默已开启.'
    elif msg.startswith('关'):
        blacklist['ban_auto_sleep'] = False
        text = '自觉静默已关闭.'
    else:
        return
    save_blacklist()
    await ban_auto_sleep.finish(text)
