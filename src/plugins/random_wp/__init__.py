from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Message, Event

cat = on_command('兽耳图', aliases={'兽耳'}, priority=50, block=True)
mpwp = on_command('竖屏壁纸', aliases={'手机壁纸'}, priority=50, block=True)
pcwp = on_command('横屏壁纸', aliases={'电脑壁纸'}, priority=50, block=True)
bztj = on_command('推荐壁纸', priority=50, block=True)
bm = on_command('来点白毛', priority=50, block=True)
xk = on_command('星空', priority=50, block=True)

@cat.handle()
async def cat_handle(event:Event):
    await cat.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(file='https://iw233.cn/api.php?sort=cat'))

@mpwp.handle()
async def mpwp_handle(event:Event):
    await mpwp.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(file='https://iw233.cn/api.php?sort=mp'))

@pcwp.handle()
async def pcwp_handle(event:Event):
    await pcwp.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(file='https://iw233.cn/api.php?sort=pc'))

@bztj.handle()
async def bztj_handle(event:Event):
    await bztj.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(file='https://iw233.cn/api.php?sort=top'))

@bm.handle()
async def bm_handle(event:Event):
    await bm.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(file='https://iw233.cn/api.php?sort=yin'))

@xk.handle()
async def xk_handle(event:Event):
    await xk.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(file='https://iw233.cn/api.php?sort=xing'))
