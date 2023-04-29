import asyncio
import contextlib
import os
import random
import sys
from pathlib import Path

from nonebot import get_app, get_bot, on_command
from nonebot.adapters.onebot.v11 import (
    ActionFailed,
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
)
from nonebot.params import Arg, ArgPlainText, CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State

from LittlePaimon.config import config
from LittlePaimon.utils import DRIVER, NICKNAME, __version__
from LittlePaimon.utils.files import load_json, save_json
from LittlePaimon.utils.update import check_update, update
from LittlePaimon.utils.requests import aiorequests

__plugin_meta__ = PluginMetadata(
    name='脑积水管理',
    description='脑积水管理',
    usage='...',
    extra={
        'author': '惜月',
        'version': '3.0',
        'priority': 99,
    },
)

update_cmd = on_command(
    '更新',
    permission=SUPERUSER,
    rule=to_me(),
    priority=1,
    block=True,
    state={
        'pm_name': 'bot_update',
        'pm_description': '从Git中更新bot，需超级用户权限',
        'pm_usage': '@bot 更新',
        'pm_priority': 2,
    },
)
check_update_cmd = on_command(
    '检查更新',
    permission=SUPERUSER,
    rule=to_me(),
    priority=1,
    block=True,
    state={
        'pm_name': 'bot_check_update',
        'pm_description': '从Git检查bot更新情况，需超级用户权限',
        'pm_usage': '@bot 检查更新',
        'pm_priority': 1,
    },
)
update_history = on_command(
    '更新记录',
    aliases={'更新历史记录'},
    permission=SUPERUSER,
    rule=to_me(),
    priority=1,
    block=True,
    state={
        'pm_name': 'update_history',
        'pm_description': '从Git查看bot更新历史记录，需超级用户权限',
        'pm_usage': '@bot 更新历史记录',
        'pm_priority': 1,
    },
)
reboot_cmd = on_command(
    '重启',
    permission=SUPERUSER,
    rule=to_me(),
    priority=1,
    block=True,
    state={
        'pm_name': 'bot_restart',
        'pm_description': '执行重启操作，需超级用户权限',
        'pm_usage': '@bot 重启',
        'pm_priority': 3,
    },
)
run_cmd = on_command(
    'cmd',
    permission=SUPERUSER,
    rule=to_me(),
    priority=1,
    block=True,
    state={
        'pm_name': 'bot_cmd',
        'pm_description': '运行终端命令，需超级用户权限',
        'pm_usage': '@bot cmd<命令>',
        'pm_priority': 4,
    },
)
broadcast = on_command(
    '广播',
    permission=SUPERUSER,
    rule=to_me(),
    priority=1,
    block=True,
    state={
        'pm_name': 'broadcast',
        'pm_description': '向指定或所有群发送消息，需超级用户权限',
        'pm_usage': '@bot 广播<内容>',
        'pm_priority': 5,
    },
)


@update_cmd.handle()
async def _(event: MessageEvent):
    await update_cmd.send(f'{NICKNAME}开始更新', at_sender=True)
    result = await update()
    await update_cmd.finish(result, at_sender=True)


@check_update_cmd.handle()
async def _(event: MessageEvent):
    result = await check_update()
    await check_update_cmd.finish(result, at_sender=True)


@update_history.handle()
async def _():
    resp = await aiorequests.get('https://api.github.com/repos/zhulinyv/NJS/commits')
    data = resp.json()
    if not isinstance(data, list):
        await update_history.finish("获取更新历史记录失败，可能是网络问题，请稍后再试", at_sender=True)
    msg = "更新记录如下: \n"
    for i in range(10):
        msg += data[i]["commit"]["committer"]["date"] + "\n" + data[i]["commit"]["message"] + "\n----------\n"
    msg.replace(":art:","🎨").replace(":zap:","⚡️").replace(":fire:","🔥").replace(":bug:","🐛").replace(":ambulance:","🚑️").replace(":sparkles:","✨").replace(":memo:","📝").replace(":rocket:","🚀").replace(":lipstick:","💄").replace(":tada:","🎉").replace(":white_check_mark:","✅").replace(":lock:","🔒️").replace(":closed_lock_with_key:","🔐").replace(":bookmark:","🔖").replace(":rotating_light:","🚨").replace(":construction:","🚧").replace(":green_heart:","💚").replace(":arrow_down:","⬇️").replace(":arrow_up:","⬆️").replace(":pushpin:","📌").replace(":construction_worker:","👷").replace(":chart_with_upwards_trend:","📈").replace(":recycle:","♻️").replace(":heavy_plus_sign:","➕").replace(":heavy_minus_sign:","➖").replace(":wrench:","🔧").replace(":hammer:","🔨").replace(":globe_with_meridians:","🌐").replace(":pencil2:","✏️").replace(":poop:","💩").replace(":rewind:","⏪️").replace(":twisted_rightwards_arrows:","🔀").replace(":package:","📦️").replace(":alien:","👽️").replace(":truck:","🚚").replace(":page_facing_up:","📄").replace(":boom:","💥").replace(":bento:","🍱").replace(":wheelchair:","♿️").replace(":bulb:","💡").replace(":beers:","🍻").replace(":speech_balloon:","💬").replace(":card_file_box:","🗃️").replace(":loud_sound:","🔊").replace(":mute:","🔇").replace(":busts_in_silhouette:","👥").replace(":children_crossing:","🚸").replace(":building_construction:","🏗️").replace(":iphone:","📱").replace(":clown_face:","🤡").replace(":egg:","🥚").replace(":see_no_evil:","🙈").replace(":camera_flash:","📸").replace(":alembic:","⚗️").replace(":mag:","🔍️").replace(":label:","🏷️").replace(":seedling:","🌱").replace(":triangular_flag_on_post:","🚩").replace(":goal_net:","🥅").replace(":dizzy:","💫").replace(":wastebasket:","🗑️").replace(":passport_control:","🛂").replace(":adhesive_bandage:","🩹").replace(":monocle_face:","🧐").replace(":coffin:","⚰️").replace(":test_tube:","🧪").replace(":necktie:","👔").replace(":stethoscope:","🩺").replace(":bricks:","🧱").replace(":technologist:","🧑‍💻").replace(":money_with_wings:","💸").replace(":thread:","🧵").replace(":safety_vest:", "🦺")
    await update_history.finish(msg, at_sender=True)


@reboot_cmd.handle()
async def _(bot: Bot, event: MessageEvent):
    await reboot_cmd.send(f'{NICKNAME}开始执行重启，请等待{NICKNAME}的归来', at_sender=True)
    reboot_data = {
        'session_type': event.message_type,
        'session_id': event.group_id
        if isinstance(event, GroupMessageEvent)
        else event.user_id,
        'group_card': {},
    }
    group_list = await bot.get_group_list()
    group_id_list = [g['group_id'] for g in group_list]
    for group_id in group_id_list:
        if group_id not in config.reboot_card_ban:
            member_info = await bot.get_group_member_info(
                group_id=group_id, user_id=int(bot.self_id), no_cache=True
            )
            reboot_data['group_card'][str(group_id)] = member_info['card']
            await bot.set_group_card(
                group_id=group_id,
                user_id=int(bot.self_id),
                card=(member_info['card'] or member_info['nickname']) + '(重启中)',
            )
            await asyncio.sleep(0.25)
    save_json(reboot_data, Path() / 'rebooting.json')
    with contextlib.suppress(Exception):
        await get_app().router.shutdown()
    reboot_arg = (
        [sys.executable] + sys.argv
        if sys.argv[0].endswith('.py')
        else [sys.executable, 'bot.py']
    )
    os.execv(sys.executable, reboot_arg)


@run_cmd.handle()
async def _(event: MessageEvent, state: T_State, cmd: Message = CommandArg()):
    if cmd:
        state['cmd'] = cmd


@run_cmd.got('cmd', prompt='你输入你要运行的命令')
async def _(event: MessageEvent, cmd: str = ArgPlainText('cmd')):
    await run_cmd.send(f'开始执行{cmd}...', at_sender=True)
    p = await asyncio.subprocess.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await p.communicate()
    try:
        result = (stdout or stderr).decode('gb2312')
    except Exception:
        result = str(stdout or stderr)
    await run_cmd.finish(f'{cmd}\n运行结果：\n{result}')


@broadcast.handle()
async def _(event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    if msg:
        state['msg'] = msg
    else:
        await broadcast.finish('请给出要广播的消息', at_sender=True)


@broadcast.got('groups', prompt='要广播到哪些群呢？多个群以空格隔开，或发送"全部"向所有群广播')
async def _(
    event: MessageEvent,
    bot: Bot,
    msg: Message = Arg('msg'),
    groups: str = ArgPlainText('groups'),
):
    group_list = await bot.get_group_list()
    group_list = [g['group_id'] for g in group_list]
    if groups in {'全部', '所有', 'all'}:
        send_groups = group_list
    else:
        groups = groups.split(' ')
        send_groups = [
            int(group)
            for group in groups
            if group.isdigit() and int(group) in group_list
        ]
    if not send_groups:
        await broadcast.finish('要广播的群未加入或参数不对', at_sender=True)
    else:
        await broadcast.send(f'开始向{len(send_groups)}个群发送广播，每群间隔5~10秒', at_sender=True)
        for group in send_groups:
            try:
                await bot.send_group_msg(group_id=group, message=msg)
                await asyncio.sleep(random.randint(5, 10))
            except ActionFailed:
                await broadcast.send(f'群{group}发送消息失败')
        await broadcast.finish('消息广播发送完成', at_sender=True)


@DRIVER.on_bot_connect
async def _(bot: Bot):
    if not (reboot_file := (Path() / 'rebooting.json')).exists():
        return
    reboot_data = load_json(reboot_file)
    reboot_file.unlink()
    if reboot_data['session_type'] == 'group':
        await bot.send_group_msg(
            group_id=reboot_data['session_id'],
            message=f'{NICKNAME}已重启完成，当前版本为{__version__}',
        )
    else:
        await bot.send_private_msg(
            user_id=reboot_data['session_id'],
            message=f'{NICKNAME}已重启完成，当前版本为{__version__}',
        )
    if 'group_card' in reboot_data:
        for group_id, card_info in reboot_data['group_card'].items():
            await bot.set_group_card(
                group_id=int(group_id), user_id=int(bot.self_id), card=card_info
            )
            await asyncio.sleep(0.25)
