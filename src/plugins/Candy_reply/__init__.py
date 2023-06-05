import os
import random

from typing import Union
from pathlib import Path

from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin.on import on_message
from nonebot.params import EventMessage

from nonebot import require
require("nonebot_plugin_guild_patch")
from nonebot_plugin_guild_patch import GuildMessageEvent

from .utils import *


# 棒棒糖
async def candy_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(147) in message
candy = on_message(rule = candy_checker)
@candy.handle()
async def candy_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    dks1 = Path(os.path.join(os.path.dirname(__file__), "resource")) / "dks1.jpg"
    dks2 = Path(os.path.join(os.path.dirname(__file__), "resource")) / "dks2.jpg"
    face_ids = [seg.data["id"] for seg in event.get_message()["face"]]
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        if face_ids.count('147') == 1:
            await candy.finish(Message("一根棒棒糖也想骗走人家？不可能！"))
        elif face_ids.count('147') <= 3:
            await candy.finish(f"就算是{face_ids.count('147')}根，也别想骗走人家（掉口水）" + MessageSegment.image(dks1), at_sender=True)
        else:
            await candy.finish(f"{random.choice(candy_reply)}" + MessageSegment.image(dks2), at_sender=True)

# 滑稽
async def hj_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(178))
hj = on_message(rule = hj_checker)
@hj.handle()
async def hj_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await hj.finish(Message(f"没事别老发滑稽") + MessageSegment.face(178))

# 狗头
async def gt_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(277) in message
gt = on_message(rule = gt_checker)
@gt.handle()
async def gt_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    face_ids = [seg.data["id"] for seg in event.get_message()["face"]]
    num = face_ids.count('277')
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await gt.finish(f"手动狗头 x {num} " + Message(MessageSegment.face(277)))

# 微笑
async def wx_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(14))
wx = on_message(rule = wx_checker)
@wx.handle()
async def wx_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await wx.finish(f"{random.choice(wx_reply)}")

# 笑哭
async def xk_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(182) in message
xk = on_message(rule = xk_checker)
@xk.handle()
async def xk_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await xk.finish("有什么好笑的，说来听听U•ェ•U")

# 大哭
async def dk_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(5) in message
dk = on_message(rule = dk_checker)
@dk.handle()
async def dk_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await dk.finish(f"{random.choice(dk_reply)}", at_sender=True)

# 委屈
async def wq_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(9) in message
wq = on_message(rule = wq_checker)
@wq.handle()
async def dk_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await wq.finish(f"{random.choice(dk_reply)}", at_sender=True)

# 捂脸
async def wl_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(264) in message
wl = on_message(rule = wl_checker)
@wl.handle()
async def wl_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await wl.finish(f"{random.choice(dk_reply)}", at_sender=True)

# 傲娇
async def aj_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(179))
aj = on_message(rule = aj_checker)
@aj.handle()
async def aj_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await aj.finish(f"{random.choice(aj_reply)}")

# 右亲亲
async def yqq_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(305))
yqq = on_message(rule = yqq_checker)
@yqq.handle()
async def yqq_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await yqq.finish(MessageSegment.face(109))

# 左亲亲
async def zqq_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(109))
zqq = on_message(rule = zqq_checker)
@zqq.handle()
async def zqq_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await zqq.finish(MessageSegment.face(305))

# 爱心
async def ax_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(66))
ax = on_message(rule = ax_checker)
@ax.handle()
async def ah_handle(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    if gid in candy_group:
        await ax.finish(f"{random.choice(ax_r)}")


