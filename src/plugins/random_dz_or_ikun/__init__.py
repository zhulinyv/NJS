from nonebot import on_command
from pathlib import Path
import os
import random
from nonebot.adapters.onebot.v11 import MessageSegment

img_path = Path(os.path.join(os.path.dirname(__file__), "resource"))
all_file_name = os.listdir(str(img_path))

ikun = on_command("ikun", aliases={'小黑子', '坤坤'}, priority=50, block=True)
dz = on_command('我测你们码', aliases={'随机丁真', '丁真', '一眼丁真'}, priority=50, block=True)

@dz.handle()
async def _():
    img_name = random.choice(all_file_name)
    img = img_path / img_name
    try:
        await dz.send(MessageSegment.image(img))
    except:
        await dz.send("我测你们码")

@ikun.handle()
async def ikun_handle():
    await ikun.send(MessageSegment.image(file='https://www.duxianmen.com/api/ikun/'))
