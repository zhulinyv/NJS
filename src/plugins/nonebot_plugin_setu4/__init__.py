import time
import asyncio
import random
import nonebot
from re import I, sub
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot import on_command, on_regex
from nonebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import (GROUP, PRIVATE_FRIEND, Bot,
                                         GroupMessageEvent, Message,
                                         MessageEvent, MessageSegment,
                                         PrivateMessageEvent)

from .get_data import get_setu
from .fetch_resources import DownloadDatabase
from .permission_manager import PermissionManager
from .resource.setu_message import setu_sendmessage


# ⡆⣐⢕⢕⢕⢕⢕⢕⢕⢕⠅⢗⢕⢕⢕⢕⢕⢕⢕⠕⠕⢕⢕⢕⢕⢕⢕⢕⢕⢕
# ⢐⢕⢕⢕⢕⢕⣕⢕⢕⠕⠁⢕⢕⢕⢕⢕⢕⢕⢕⠅⡄⢕⢕⢕⢕⢕⢕⢕⢕⢕
# ⢕⢕⢕⢕⢕⠅⢗⢕⠕⣠⠄⣗⢕⢕⠕⢕⢕⢕⠕⢠⣿⠐⢕⢕⢕⠑⢕⢕⠵⢕
# ⢕⢕⢕⢕⠁⢜⠕⢁⣴⣿⡇⢓⢕⢵⢐⢕⢕⠕⢁⣾⢿⣧⠑⢕⢕⠄⢑⢕⠅⢕
# ⢕⢕⠵⢁⠔⢁⣤⣤⣶⣶⣶⡐⣕⢽⠐⢕⠕⣡⣾⣶⣶⣶⣤⡁⢓⢕⠄⢑⢅⢑
# ⠍⣧⠄⣶⣾⣿⣿⣿⣿⣿⣿⣷⣔⢕⢄⢡⣾⣿⣿⣿⣿⣿⣿⣿⣦⡑⢕⢤⠱⢐
# ⢠⢕⠅⣾⣿⠋⢿⣿⣿⣿⠉⣿⣿⣷⣦⣶⣽⣿⣿⠈⣿⣿⣿⣿⠏⢹⣷⣷⡅⢐
# ⣔⢕⢥⢻⣿⡀⠈⠛⠛⠁⢠⣿⣿⣿⣿⣿⣿⣿⣿⡀⠈⠛⠛⠁⠄⣼⣿⣿⡇⢔
# ⢕⢕⢽⢸⢟⢟⢖⢖⢤⣶⡟⢻⣿⡿⠻⣿⣿⡟⢀⣿⣦⢤⢤⢔⢞⢿⢿⣿⠁⢕
# ⢕⢕⠅⣐⢕⢕⢕⢕⢕⣿⣿⡄⠛⢀⣦⠈⠛⢁⣼⣿⢗⢕⢕⢕⢕⢕⢕⡏⣘⢕
# ⢕⢕⠅⢓⣕⣕⣕⣕⣵⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣷⣕⢕⢕⢕⢕⡵⢀⢕⢕
# ⢑⢕⠃⡈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢃⢕⢕⢕
# ⣆⢕⠄⢱⣄⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢁⢕⢕⠕⢁
# ⣿⣦⡀⣿⣿⣷⣶⣬⣍⣛⣛⣛⡛⠿⠿⠿⠛⠛⢛⣛⣉⣭⣤⣂⢜⠕⢑⣡⣴⣿


# --------------- 初始化变量 ---------------
# 实例化权限管理
pm = PermissionManager()

# 读取setu的正则表达式
try:
    setu_regex: str = repr(nonebot.get_driver().config.setu_regex)
except:
    setu_regex: str = r"^(setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?(.*)?"

# --------------- 一些需要复用的功能 ---------------
# 根据会话类型生成sessionId


def sessionId(event: MessageEvent) -> str:
    if isinstance(event, PrivateMessageEvent):
        sessionId = 'user_' + str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        sessionId = 'group_' + str(event.group_id)
    return sessionId


def verifySid(sid: str) -> bool:
    try:
        sType, sId = sid.split('_')
        if sType in ['group', 'user']:
            if sId.isdigit():
                return True
        return False
    except:
        return False


# --------------- 发送setu的部分 ---------------
# 正则部分
setu = on_regex(
    setu_regex,
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
    priority=20,
    block=True
)

# 响应器处理操作


@setu.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    # 获取用户输入的参数
    args = list(state["_matched_groups"])
    r18flag = args[2]
    key = sub('[\'\"]', '', args[3])  # 去掉引号防止sql注入
    num = int(sub(r"[张|个|份|x|✖️|×|X|*]", "", args[1])) if args[1] else 1

    # 根据会话类型生成sessionId
    if isinstance(event, PrivateMessageEvent):
        sessionId = 'user_' + str(event.user_id)
        userType = 'private'
    if isinstance(event, GroupMessageEvent):
        sessionId = 'group_' + str(event.group_id)
        userType = 'group'
    # 权限检查
    try:
        userType = 'SU' if (
            str(event.user_id) in nonebot.get_driver().config.superusers) else userType
        r18, num, withdraw_time = pm.CheckPermission(
            sessionId, r18flag, num, userType)
    except PermissionError as e:
        await setu.finish(str(e), at_sender=True)

    # 色图图片质量, 如果num为3-6质量为70,如果num为7-max质量为50,其余为95(图片质量太高发起来太费时间了)
    # quality = 95就是原图
    if num >= 3 and num <= 6:
        quality = 70
    elif num >= 7:
        quality = 50
    else:
        quality = 95
    if num >= 3:
        await setu.send(f"由于数量过多请等待\n当前图片质量为{quality}\n3-6:quality = 70\n7+:quality = 50")

    # key按照空格切割为数组, 用于多关键词搜索, 并且把数组中的空元素去掉
    key = key.split(" ")
    key = [word.strip() for word in key if word.strip()]

    flagLog = f"\nR18 == {str(r18)}\nkeyword == {key}\nnum == {num}\n"
    logger.info(f"key = {key}\tr18 = {r18}\tnum = {num}")
    # 记录时间, 计算CD用
    pm.UpdateLastSend(sessionId)

    # data是数组套娃, 数组中的每个元素内容为: [图片, 信息, True/False, url]
    try:
        data = await get_setu(key, r18, num, quality)
    except Exception as e:
        await setu.finish(str(e), at_sender=True)

    # 发送的消息列表
    message_list = []
    for pic in data:
        # 如果状态为True,说明图片拿到了
        if pic[2]:
            message = f"{random.choice(setu_sendmessage)}{flagLog}" + \
                Message(pic[1]) + MessageSegment.image(pic[0])
            message_list.append(message)
            flagLog = ''
        # 状态为false的消息,图片没拿到
        else:
            message = pic[0] + pic[1]
            message_list.append(message)

    # 为后面撤回消息做准备
    setu_msg_id = []
    # 尝试发送
    try:
        startTime = time.time()  # 记录开始发送的时间
        if isinstance(event, PrivateMessageEvent):
            # 私聊直接发送
            for msg in message_list:
                setu_msg_id.append((await setu.send(msg))['message_id'])
                await asyncio.sleep(0.5)
        elif isinstance(event, GroupMessageEvent):
            # 群聊以转发消息的方式发送
            msgs = []
            for msg in message_list:
                msgs.append({
                    'type': 'node',
                    'data': {
                        'name': "setu-bot",
                        'uin': bot.self_id,
                        'content': msg
                    }
                })
            setu_msg_id.append((await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs))['message_id'])
    # 发送失败
    except ActionFailed as e:
        logger.warning(e)
        await setu.finish(
            message=Message(f"消息被风控了捏，图发不出来，请尽量减少发送的图片数量"),
            at_sender=True,
        )

    # 自动撤回涩图
    if withdraw_time != 0:
        try:
            timeLeft = withdraw_time + startTime - time.time()  # 计算从开始发送到目前仍剩余的保留时间
            await asyncio.sleep(1 if timeLeft <= 0 else timeLeft)
            for msg_id in setu_msg_id:
                await bot.delete_msg(message_id=msg_id)
        except:
            pass


# --------------- 权限管理部分 ---------------
# ----- 白名单添加与解除 -----
open_setu = on_command("setu_wl", permission=SUPERUSER,
                       block=True, priority=10)


# 分析是新增还是删除
@open_setu.handle()
async def cmdArg(state: T_State, cmd: Message = CommandArg()):
    if 'add' in str(cmd):
        state['add_mode'] = True
    elif 'del' in str(cmd):
        state['add_mode'] = False
    else:
        await open_setu.finish(f'无效参数: {cmd}, 请输入 add 或 del 为参数')


# 群聊部分自动获取sid
@open_setu.handle()
async def group(event: GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)


# 手动获取sid, 并调用对应的方法进行处理
@open_setu.got('sid', prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await open_setu.reject(f"无效目标对象: {sid}")
    await open_setu.finish(pm.UpdateWhiteList(sid, state['add_mode']))


# ----- r18添加与解除 -----
set_r18 = on_command("setu_r18", permission=SUPERUSER, block=True, priority=10)


# 分析是开启还是关闭
@set_r18.handle()
async def cmdArg(state: T_State, cmd: Message = CommandArg()):
    if 'on' in str(cmd):
        state['r18Mode'] = True
    elif 'off' in str(cmd):
        state['r18Mode'] = False
    else:
        await set_r18.finish(f'无效参数: {cmd}, 请输入 on 或 off 为参数')


# 群聊部分自动获取sid
@set_r18.handle()
async def group(event: GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)


# 手动获取sid, 并调用对应的方法进行处理
@set_r18.got('sid', prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await set_r18.reject(f"无效目标对象: {sid}")
    await set_r18.finish(pm.UpdateR18(sid, state['r18Mode']))

# ----- cd时间更新 -----
set_cd = on_command("setu_cd", permission=SUPERUSER, block=True, priority=10)


# 获取参数
@set_cd.handle()
async def cmdArg(state: T_State, cmd: Message = CommandArg()):
    try:
        state['cdTime'] = int(str(cmd))
    except:
        await set_cd.finish(f'无效参数: {cmd}, 请输入 正整数 或 0 为参数')


# 群聊部分自动获取sid
@set_cd.handle()
async def group(event: GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)


# 手动获取sid, 并调用对应的方法进行处理
@set_cd.got('sid', prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await set_cd.reject(f"无效目标对象: {sid}")
    await set_cd.finish(pm.UpdateCd(sid, state['cdTime']))

# ----- 撤回时间更新 -----
set_wd = on_command("setu_wd", permission=SUPERUSER, block=True, priority=10)


# 获取参数
@set_wd.handle()
async def cmdArg(state: T_State, cmd: Message = CommandArg()):
    try:
        state['withdrawTime'] = int(str(cmd))
    except:
        await set_wd.finish(f'无效参数: {cmd}, 请输入 正整数 或 0 为参数')


# 群聊部分自动获取sid
@set_wd.handle()
async def group(event: GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)


# 手动获取sid, 并调用对应的方法进行处理
@set_wd.got('sid', prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await set_wd.reject(f"无效目标对象: {sid}")
    await set_wd.finish(pm.UpdateWithdrawTime(sid, state['withdrawTime']))


# ----- 最大张数更新 -----
set_maxnum = on_command("setu_mn", permission=SUPERUSER,
                        block=True, priority=10)


# 获取参数
@set_maxnum.handle()
async def cmdArg(state: T_State, cmd: Message = CommandArg(), ):
    try:
        state['maxNum'] = int(str(cmd))
    except:
        await set_maxnum.finish(f'无效参数: {cmd}, 请输入 正整数 为参数')


# 群聊部分自动获取sid
@set_maxnum.handle()
async def group(event: GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)


# 手动获取sid, 并调用对应的方法进行处理
@set_maxnum.got('sid', prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await set_maxnum.reject(f"无效目标对象: {sid}")
    await set_maxnum.finish(pm.UpdateMaxNum(sid, state['maxNum']))

# ----- 黑名单添加与解除 -----
ban_setu = on_command("setu_ban", permission=SUPERUSER,
                      block=True, priority=10)


# 分析是新增还是删除
@ban_setu.handle()
async def cmdArg(state: T_State, cmd: Message = CommandArg()):
    if 'add' in str(cmd):
        state['add_mode'] = True
    elif 'del' in str(cmd):
        state['add_mode'] = False
    else:
        await ban_setu.finish(f'无效参数: {cmd}, 请输入 add 或 del 为参数')


# 群聊部分自动获取sid
@ban_setu.handle()
async def group(event: GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)


# 手动获取sid, 并调用对应的方法进行处理
@ban_setu.got('sid', prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await ban_setu.reject(f"无效目标对象: {sid}")
    await ban_setu.finish(pm.UpdateBanList(sid, state['add_mode']))

# --------------- 发送帮助信息 ---------------
setuhelp = on_command("setu_help", aliases={
                      "setu_帮助", "色图_help", "色图_帮助"}, block=True, priority=10)


@setuhelp.handle()
async def _():
    help_msg = """setu指令:
    ^(setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?(.*)?
   
    白名单管理：
    setu_wl add  添加会话至白名单
    setu_wl del  移出会话自白名单
    
    黑名单管理：    
    setu_ban add  添加会话至黑名单
    setu_ban del  移出会话自黑名单

    r18模式管理：
    setu_r18 on  开启会话的r18模式
    setu_r18 off 关闭会话的r18模式

    cd时间更新:
    setu_cd xxx  更新会话的冷却时间, xxx为int类型的参数

    撤回时间更新:
    setu_wd xxx  撤回前等待的时间, xxx为int类型的参数

    最大张数更新:
    setu_mn xxx  单次发送的最大图片数, xxx为int类型的参数
    
    查询黑白名单:
    setu_roster"""
    await setuhelp.finish(help_msg)


# --------------- 数据库更新 ---------------
setuupdate = on_command('setu_db', permission=SUPERUSER,
                        block=True, priority=10)


@setuupdate.handle()
async def _():
    await setuupdate.finish('目前此功能仍在实验性阶段，可能造成数据丢失或无法写入等错误\n如果执意需要使用，请手动删除代码中的对应部分以启用')
    try:
        remsg = await DownloadDatabase()
    except Exception as e:
        remsg = f'获取 lolicon.db 失败: {e}'
    await setuupdate.finish(remsg)

# --------------- 查询黑白名单 ---------------
queryBlackAndWhiteList = on_command(
    "setu_roster", aliases={"色图名单"}, permission=SUPERUSER, block=True, priority=10)


@queryBlackAndWhiteList.handle()
async def _():
    res = pm.ReadCfg()      # 读取json
    key_list = list(res.keys())  # 拿到所有的keys
    key_list.remove('ban')       # 移掉ban和last, 剩下的就是白名单了
    key_list.remove('last')
    # 黑名单内容则在res['ban']
    await queryBlackAndWhiteList.send(f"白名单: {key_list}\n\n黑名单: {res['ban']}")
