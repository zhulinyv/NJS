from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Message, Event

cat = on_command('来份兽耳图', aliases={'兽耳'}, priority=50, block=True)
mpwp = on_command('竖屏壁纸', aliases={'手机壁纸'}, priority=50, block=True)
pcwp = on_command('横屏壁纸', aliases={'电脑壁纸'}, priority=50, block=True)

@cat.handle()
async def goodnight_handle(event:Event):
    await cat.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(file='https://dev.iw233.cn/api.php?sort=cat'))

@mpwp.handle()
async def goodnight_handle(event:Event):
    await mpwp.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(file='https://dev.iw233.cn/api.php?sort=mp'))

@pcwp.handle()
async def goodnight_handle(event:Event):
    await pcwp.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(file='https://dev.iw233.cn/api.php?sort=pc'))