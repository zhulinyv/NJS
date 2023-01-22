from .utils import *


goodmorning = on_command('早安', aliases={'goodmorning'}, priority=50, block=True)
goodnight = on_command('晚安', aliases={'goodnight'}, priority=50, block=True)


@goodmorning.handle()
async def goodmorning_handle(event:Event):
    await goodmorning.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(morning_reply)}" + MessageSegment.image(file='http://pkpk.run/to_image/out_image.php'))

@goodnight.handle()
async def goodnight_handle(event:Event):
    await goodnight.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + f"{random.choice(night_reply)}" + MessageSegment.image(file='http://pkpk.run/to_image/out_image.php'))

