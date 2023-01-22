from nonebot import on_regex
from pathlib import Path
import os
import random
from nonebot.adapters.onebot.v11 import MessageSegment

what_eat=on_regex(r"(今?(天|晚)|早上|晚上|中午|夜宵)?吃什么",priority=5)
what_drink=on_regex(r"(今?(天|晚)|早上|晚上|中午|夜宵)?喝什么",priority=5)

#今天吃什么路劲
img_eat_path = Path(os.path.join(os.path.dirname(__file__), "eat_pic"))
all_file_eat_name = os.listdir(str(img_eat_path))

#今天喝什么路劲
img_drink_path = Path(os.path.join(os.path.dirname(__file__), "drink_pic"))
all_file_drink_name= os.listdir(str(img_drink_path))

@what_drink.handle()
async def wtd():
    img_name=random.choice(all_file_drink_name)
    img=img_drink_path / img_name
    msg=(
        f"脑积水建议你吃: {img.stem}\n"
        +MessageSegment.image(img)
    )
    try:
        await what_drink.send(message='脑积水正在为你找好喝的……')
        await what_drink.send(msg, at_sender=True)
    except:
        await what_drink.finish(message="脑积水出错啦！没有找到好喝的~")



@what_eat.handle()
async def wte():
    img_name = random.choice(all_file_eat_name)
    img = img_eat_path / img_name
    msg=(
        f"脑积水建议你吃: {img.stem}\n"
        +MessageSegment.image(img)
    )
    try:
        await what_eat.send(message='脑积水正在为你找好吃的……')
        await what_eat.send(msg, at_sender=True)
    except:
        await what_eat.finish(message="脑积水出错啦！没有找到好吃的~")