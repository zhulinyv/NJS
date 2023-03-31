import os
import random
from nonebot import on_command
from pathlib import Path
from nonebot.adapters.onebot.v11 import MessageSegment

randomnana= on_command('狗妈', aliases={'随机狗妈'}, priority=10, block=True)

img_path = os.path.join(os.path.dirname(__file__), "resource")

all_file_name = os.listdir(img_path)

@randomnana.handle()
async def _():
    img_name = random.choice(all_file_name)
    img = Path(img_path) / img_name
    try:
        await randomnana.send(MessageSegment.image(img))
    except:
        await randomnana.send(f"图片文件 {str(img)} 发送失败")