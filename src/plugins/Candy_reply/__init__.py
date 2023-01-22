from nonebot.adapters.onebot.v11 import Message, MessageSegment, Event
from nonebot.params import EventMessage
from nonebot.plugin.on import on_message
from pathlib import Path
import os
import random

from .utils import *


# 棒棒糖
async def candy_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(147) in message
candy = on_message(rule = candy_checker)
@candy.handle()
async def candy_handle(event: Event):
    dks1 = Path(os.path.join(os.path.dirname(__file__), "resource")) / "dks1.jpg"
    dks2 = Path(os.path.join(os.path.dirname(__file__), "resource")) / "dks2.jpg"
    face_ids = [seg.data["id"] for seg in event.get_message()["face"]]
    if face_ids.count('147') == 1:
        await candy.finish(Message("一根棒棒糖也想骗走人家？不可能！"))
    elif face_ids.count('147') <= 3:
        await candy.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"就算是{face_ids.count('147')}根，也别想骗走人家（掉口水）" + MessageSegment.image(dks1))
    else:
        await candy.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(candy_reply)}" + MessageSegment.image(dks2))

# 滑稽
async def hj_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(178))
hj = on_message(rule = hj_checker)
@hj.handle()
async def hj_handle():
    await hj.finish(Message(f"没事别老发滑稽") + MessageSegment.face(178))

# 狗头
async def gt_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(277) in message
gt = on_message(rule = gt_checker)
@gt.handle()
async def gt_handle(event: Event):
    face_ids = [seg.data["id"] for seg in event.get_message()["face"]]
    num = face_ids.count('277')
    await gt.finish(f"手动狗头 x {num} " + Message(MessageSegment.face(277)))

# 微笑
async def wx_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(14))
wx = on_message(rule = wx_checker)
@wx.handle()
async def wx_handle():
    await wx.finish(f"{random.choice(wx_reply)}")

# 笑哭
async def xk_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(182) in message
xk = on_message(rule = xk_checker)
@xk.handle()
async def xk_handle():
    await xk.finish("有什么好笑的，说来听听U•ェ•U")

# 大哭
async def dk_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(5) in message
dk = on_message(rule = dk_checker)
@dk.handle()
async def dk_handle(event: Event):
    await dk.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(dk_reply)}")

# 委屈
async def wq_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(9) in message
wq = on_message(rule = wq_checker)
@wq.handle()
async def dk_handle(event: Event):
    await wq.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(dk_reply)}")

# 捂脸
async def wl_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(264) in message
wl = on_message(rule = wl_checker)
@wl.handle()
async def wl_handle(event: Event):
    await wl.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(dk_reply)}")

# 傲娇
async def aj_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(179))
aj = on_message(rule = aj_checker)
@aj.handle()
async def aj_handle():
    await aj.finish(f"{random.choice(aj_reply)}")

# 右亲亲
async def yqq_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(305))
yqq = on_message(rule = yqq_checker)
@yqq.handle()
async def yqq_handle():
    await yqq.finish(MessageSegment.face(109))

# 左亲亲
async def zqq_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(109))
zqq = on_message(rule = zqq_checker)
@zqq.handle()
async def zqq_handle():
    await zqq.finish(MessageSegment.face(305))

# 爱心
async def ax_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(66))
ax = on_message(rule = ax_checker)
@ax.handle()
async def ah_handle():
    await ax.finish(f"{random.choice(ax_r)}")


