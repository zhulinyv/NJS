import time, datetime, random, json
from typing import Any, Dict, List, Tuple, Optional

from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot import get_driver, on_command, on_notice
from nonebot import on_command, on_fullmatch, on_keyword, on_message
from nonebot.log import logger
from nonebot.internal.adapter import Bot as BaseBot
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    Event,
    MessageEvent,
    GroupMessageEvent,
    GroupRecallNoticeEvent,
    PrivateMessageEvent,
)
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER, GROUP_MEMBER
from nonebot.params import Command, CommandArg, RawCommand, ArgStr

from pathlib import Path
from typing import Literal

superusers = get_driver().config.superusers
file_path = Path() / 'data' / 'enablelist' / 'enablelist.json'
file_path.parent.mkdir(parents = True, exist_ok = True)

enablelist = (
    json.loads(file_path.read_text('utf-8'))
    if file_path.is_file()
    else {'grouplist': [], 'userlist': []}
)

def save_enablelist() -> None:
    file_path.write_text(json.dumps(enablelist), encoding='utf-8')

bypass_admin_list_path = Path() / 'data' / 'enablelist' / 'bypass_admin.json'
bypass_admin_list_path.parent.mkdir(parents = True, exist_ok = True)

bypass_admin_list = (
    json.loads(bypass_admin_list_path.read_text('utf-8'))
    if bypass_admin_list_path.is_file()
    else {}
)

def save_bypass_admin_list() -> None:
    bypass_admin_list_path.write_text(json.dumps(bypass_admin_list), encoding='utf-8')

def testfor_bypass_admin_list(gid) -> bool:
    if gid in bypass_admin_list.keys():
        return True
    return False

private_msg_list_path = Path() / 'data' / 'enablelist' / 'private_msg_list.json'
private_msg_list_path.parent.mkdir(parents = True, exist_ok = True)

private_msg_list = (
    json.loads(private_msg_list_path.read_text('utf-8'))
    if private_msg_list_path.is_file()
    else {}
)

def save_private_msg_list() -> None:
    private_msg_list_path.write_text(json.dumps(private_msg_list), encoding='utf-8')

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

def handle_msg(
    arg,
    mode: Literal['add', 'del'],
    type_: Literal['userlist', 'grouplist'],
) -> str:
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        return '用法: \n添加/删除群 gid1 gid2 gid3 ...'
    for uid in uids:
        if not is_number(uid):
            return '参数错误, id必须是数字..'
    msg = handle_enablelist(uids, mode, type_)
    return msg

def handle_enablelist(
    uids: list,
    mode: Literal['add', 'del'],
    type_: Literal['userlist', 'grouplist'],
) -> str:
    if mode == 'add':
        enablelist[type_].extend(uids)
        enablelist[type_] = list(set(enablelist[type_]))
        _mode = '添加'
    elif mode == 'del':
        enablelist[type_] = [uid for uid in enablelist[type_] if uid not in uids]
        _mode = '删除'
    save_enablelist()
    _type = '用户' if type_ == 'userlist' else '群聊'
    return f"已{_mode} {len(uids)} 个{_type}: {', '.join(uids)}"

add_grouplist = on_command('开启防撤回', aliases = {'添加防撤回', 'enable'}, permission = SUPERUSER, block = True)

@add_grouplist.handle()
async def add_group_list(arg: Message = CommandArg()):
    msg = handle_msg(arg, 'add', 'grouplist')
    await add_grouplist.finish(msg)
    await add_grouplist.send('操作成功!')

del_grouplist = on_command('关闭防撤回', aliases = {'删除防撤回', 'disable'}, permission = SUPERUSER, block = True)

@del_grouplist.handle()
async def del_group_list(arg: Message = CommandArg()):
    msg = handle_msg(arg, 'del', 'grouplist')
    await del_grouplist.finish(msg)
    await del_grouplist.send('操作成功!')

check_grouplist = on_command('查看防撤回群聊', permission = SUPERUSER, block = True)

@check_grouplist.handle()
async def check_group_list():
    await check_grouplist.finish(f"当前开启 {len(enablelist['grouplist'])} 个群聊的防撤回: {', '.join(enablelist['grouplist'])}")

add_group = on_command('开启当前防撤回', aliases = {'添加当前防撤回', 'enable here', '开启本群防撤回', '添加本群防撤回'}, permission = SUPERUSER | GROUP_OWNER, block=True)

@add_group.handle()
async def add_group_(event: GroupMessageEvent):
    handle_enablelist([f'{event.group_id}'], 'add', 'grouplist')
    await add_group.finish('哈哈哈,我能偷听你们的聊天啦...')

del_group = on_command('关闭当前防撤回', aliases = {'删除当前防撤回', 'disable here', '关闭本群防撤回', '删除本群防撤回'}, permission = SUPERUSER | GROUP_OWNER, block=True)

@del_group.handle()
async def del_group_(event: GroupMessageEvent):
    handle_enablelist([f'{event.group_id}'], 'del', 'grouplist')
    await del_group.finish('噢不,我管不着你们的聊天了...')


enable_bypass_admin = on_command('开启绕过管理层', aliases = {'bypass here'}, permission = SUPERUSER | GROUP_OWNER, block = True)

@enable_bypass_admin.handle()
async def enable_bypass_admin_(event: GroupMessageEvent):
    bypass_admin_list[str(event.group_id)] = True
    save_bypass_admin_list()
    await add_group.finish('本群管理层不怕防撤回了...真不公平')

disable_bypass_admin = on_command('关闭绕过管理层', aliases = {'no bypass here'}, permission = SUPERUSER | GROUP_OWNER, block = True)

@disable_bypass_admin.handle()
async def disable_bypass_admin_(event: GroupMessageEvent):
    bypass_admin_list[str(event.group_id)] = False
    save_bypass_admin_list()
    await add_group.finish('本群管理层也会防撤回...挺公平的...')

reset_enablelist = on_command('重置开启名单', aliases = {'清空开启名单'}, permission = SUPERUSER, priority = 1, block = True)

@reset_enablelist.got('flag', prompt='确定重置开启名单? (Y/n)')
async def reset_list(flag: str = ArgStr('flag')):
    if flag in ['Y', 'Yes', 'True']:
        enablelist['userlist'].clear()
        enablelist['grouplist'].clear()
        save_enablelist()
        await reset_enablelist.finish('开启名单已重置')
    else:
        await reset_enablelist.finish('操作已取消')

# 主体
recall = on_notice(priority = 60, block = False)

@recall.handle()

async def recall_handle(bot:Bot, event: GroupRecallNoticeEvent):
    if str(event.user_id) != str(bot.self_id):
        mid = event.message_id
        gid = event.group_id
        uid = event.user_id
        tid = datetime.datetime.fromtimestamp(event.time)
        time = tid.strftime('%Y-%m-%d %H:%M:%S')
        # await recall.send(str(enablelist['grouplist']))
        response = await bot.get_msg(message_id = mid)
        if str(gid) in enablelist['grouplist']:
            # await bot.send_group_msg(group_id = gid, message = time + '\n触发反撤回功能')
            if testfor_bypass_admin_list(str(gid)) and bypass_admin_list[str(gid)]:
                info = await bot.get_group_member_info(group_id = gid, user_id = uid)
                if info['role'] == 'member':
                    await bot.send_group_msg(group_id = gid, message = response['message'], auto_escape = False)
                    if str(gid) in private_msg_list.keys():
                        for i in private_msg_list[str(gid)]:
                            group_info = await bot.get_group_info(group_id = gid)
                            await bot.send_private_msg(user_id = int(i), message = time + '\n' + group_info['group_name'] + '(' + str(gid) + ') 内 ' + info['nickname'] + '(' + str(uid) + ') 撤回消息如下:' )
                            await bot.send_private_msg(user_id = int(i), message = response['message'], auto_escape = False)
                else:
                    logger.debug('忽略管理层消息成功')
            else:
                await bot.send_group_msg(group_id = gid, message = response['message'], auto_escape = False)
                if str(gid) in private_msg_list.keys():
                    for i in private_msg_list[str(gid)]:
                        group_info = await bot.get_group_info(group_id = gid)
                        await bot.send_private_msg(user_id = int(i), message = time + '\n' + group_info['group_name'] + '(' + str(gid) + ') 内 ' + info['nickname'] + '(' + str(uid) + ') 撤回消息如下:' )
                        await bot.send_private_msg(user_id = int(i), message = response['message'], auto_escape = False)

use_help = on_command('防撤回管理', aliases = {'防撤回菜单', 'anti recall menu'}, priority=50, block = True)

@use_help.handle()

async def use_help_handle(bot: Bot, event: Event):
    await use_help.send('开启/添加防撤回, enable\n关闭/删除防撤回, disable\n查看防撤回群聊\n开启/添加当前/本群防撤回, enable here\n关闭/删除当前/本群防撤回, disable here\n重置/清空开启名单\n开启/关闭绕过管理层, bypass/no bypass here\n开启/关闭防撤回私聊[gid] [qq] : 私聊使用,仅限一个群号和一个私聊的qq\n查看防撤回私聊, list private msg : 私聊使用,返回一个json数据\n不建议使用私聊,容易风控')

enable_private_msg = on_command('开启防撤回私聊', aliases = {'enable private msg', '启用防撤回私聊'}, permission = SUPERUSER, priority = 1, block = True)

@enable_private_msg.handle()

async def enable_private_msg_handle(bot: Bot, event: PrivateMessageEvent, arg: Message = CommandArg()):
    #try:
    data = arg.extract_plain_text().strip().split(' ')
    if data[0] in private_msg_list.keys():
        private_msg_list[data[0]].append(data[1])
        save_private_msg_list()
        await enable_private_msg.send('操作成功!')
    else:
        private_msg_list[data[0]] = []
        private_msg_list[data[0]].append(data[1])
        await enable_private_msg.send('操作成功!')
        save_private_msg_list()

disable_private_msg = on_command('关闭防撤回私聊', aliases = {'disable private msg', '停用防撤回私聊'}, permission = SUPERUSER, priority = 1, block = True)

@disable_private_msg.handle()

async def disable_private_msg_handle(bot: Bot, event: PrivateMessageEvent, arg: Message = CommandArg()):
    #try:
    data = arg.extract_plain_text().strip().split(' ')
    try:
        private_msg_list[data[0]].remove(data[1])
        save_private_msg_list()
        await enable_private_msg.send('操作成功!')
    except:
        await enable_private_msg.send('你好像没有启用该qq群/qq的防撤回私聊,你没启用干嘛要关闭?')

    #except:
     #   await enable_private_msg.send('命令参数错误,正确应该是:开启防撤回私聊[群号] [要私聊的QQ]')
    # await enable_private_msg.send(str(data))


view_private_msg = on_command('查看防撤回私聊', aliases = {'list private msg'}, permission = SUPERUSER, priority = 1, block = True)

@view_private_msg.handle()

async def view_private_msg_handle(bot: Bot, event: PrivateMessageEvent):
    await view_private_msg.send(str(private_msg_list))
