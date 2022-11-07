from nonebot.adapters.onebot.v11 import Message, MessageSegment, Event
from nonebot.params import EventMessage
from nonebot.plugin.on import on_message
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
    elif face_ids.count('147') <= 4:
        await candy.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"就算是{face_ids.count('147')}根，也别想骗走人家（掉口水）" + MessageSegment.image(dks1))
    else:
        await candy.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(candy_reply)}" + MessageSegment.image(dks2))

# 滑稽
async def hj_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(178))
hj_checker = on_message(rule = hj_checker)
@hj_checker.handle()
async def hj_handle(event: Event):
    face_ids = [seg.data["id"] for seg in event.get_message()["face"]]
    if face_ids.count('178') == 1:
        await candy.finish(Message(f"没事别老发滑稽`(*>﹏<*)′") + MessageSegment.face(178))

# 粑粑
async def bb_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(59))
bb_checker = on_message(rule = bb_checker)
@bb_checker.handle()
async def bb_handle(event: Event):
    face_ids = [seg.data["id"] for seg in event.get_message()["face"]]
    if face_ids.count('59') == 1:
        await candy.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(bb_reply)}")

# 狗头
async def gt_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(277))
gt_checker = on_message(rule = gt_checker)
@gt_checker.handle()
async def gt_handle(event: Event):
    face_ids = [seg.data["id"] for seg in event.get_message()["face"]]
    if face_ids.count('277') == 1:
        await candy.finish(Message("手动狗头（"))

# 微笑
async def wx_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(14))
wx_checker = on_message(rule = wx_checker)
@wx_checker.handle()
async def wx_handle(event: Event):
    await candy.finish(f"{random.choice(wx_reply)}")

# 笑哭
async def xk_checker(message: Message = EventMessage()) -> bool:
    return message == Message(MessageSegment.face(182))
xk_checker = on_message(rule = xk_checker)
@xk_checker.handle()
async def xk_handle(event: Event):
    await candy.finish(Message("有什么好笑的，说来听听U•ェ•U"))

# 大哭
async def dk_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(5) in message
dk = on_message(rule = dk_checker)
@dk.handle()
async def dk_handle(event: Event):
    await candy.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(dk_reply)}")

# 委屈
async def dk_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(9) in message
dk = on_message(rule = dk_checker)
@dk.handle()
async def dk_handle(event: Event):
    await candy.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(dk_reply)}")

# 捂脸
async def dk_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(264) in message
dk = on_message(rule = dk_checker)
@dk.handle()
async def dk_handle(event: Event):
    await candy.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(dk_reply)}")

# 傲娇
async def dk_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(179) in message
dk = on_message(rule = dk_checker)
@dk.handle()
async def dk_handle(event: Event):
    await candy.finish(f"{random.choice(aj_reply)}")

# 右亲亲
async def yqq_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(305) in message
yqq = on_message(rule = yqq_checker)
@yqq.handle()
async def yqq_handle(event: Event):
    await candy.finish(MessageSegment.face(109))

# 左亲亲
async def yqq_checker(message: Message = EventMessage()) -> bool:
    return MessageSegment.face(109) in message
yqq = on_message(rule = yqq_checker)
@yqq.handle()
async def yqq_handle(event: Event):
    await candy.finish(MessageSegment.face(305))