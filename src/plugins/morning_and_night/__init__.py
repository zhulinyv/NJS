import time
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment

from .utils import *

goodmorning = on_command('早安', aliases={'goodmorning'}, priority=50, block=True)
goodnight = on_command('晚安', aliases={'goodnight'}, priority=50, block=True)


@goodmorning.handle()
async def goodmorning_handle():
    hour = time.localtime().tm_hour
    msg = f"{random.choice(morning_reply)}" + MessageSegment.image(file='http://pkpk.run/to_image/out_image.php')
    if hour > 10 and hour < 12:
        await goodmorning.send("大懒猪, 已经不早啦! ", at_sender=True)
        await goodmorning.send(msg, at_sender=True)
    elif hour >= 12:
        await goodmorning.finish("康康都几点了...", at_sender=True)
    else:
        await goodmorning.finish(msg, at_sender=True)
    

@goodnight.handle()
async def goodnight_handle():
    hour = time.localtime().tm_hour
    msg = f"{random.choice(night_reply)}" + MessageSegment.image(file='http://pkpk.run/to_image/out_image.php')
    if hour >= 12 and hour < 16:
        await goodmorning.send("现在还很早哦~", at_sender=True)
        await goodmorning.send(msg, at_sender=True)
    elif hour <= 12:
        await goodmorning.finish("康康现在是几点...", at_sender=True)
    else:
        await goodnight.finish(msg, at_sender=True)

