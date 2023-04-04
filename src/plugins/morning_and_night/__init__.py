import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from .utils import *

goodmorning = on_command('早安', aliases={'goodmorning'}, priority=50, block=True)
goodnight = on_command('晚安', aliases={'goodnight'}, priority=50, block=True)


@goodmorning.handle()
async def goodmorning_handle():
    await goodmorning.finish(f"{random.choice(morning_reply)}" + MessageSegment.image(file='http://pkpk.run/to_image/out_image.php'), at_sender=True)

@goodnight.handle()
async def goodnight_handle():
    await goodnight.finish(f"{random.choice(night_reply)}" + MessageSegment.image(file='http://pkpk.run/to_image/out_image.php'), at_sender=True)

