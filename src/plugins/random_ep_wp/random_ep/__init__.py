import os
import random
from pathlib import Path
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageSegment, Message



random_emotion = on_command("随机", priority=50, block=True)

@random_emotion.handle()
async def _(msg: Message = CommandArg()):
    tag = msg.extract_plain_text().strip()

    if tag == "坤坤":
        await random_emotion.send(MessageSegment.image(file='https://www.duxianmen.com/api/ikun/'))
    elif tag == "胡桃":
        await random_emotion.send(MessageSegment.image(file='https://img.moehu.org/pic.php?id=mc'))
    elif tag == "兽耳酱":
        await random_emotion.send(MessageSegment.image(file='https://img.moehu.org/pic.php?id=kemomimi'))
    else:
        try:
            img_path = Path(os.path.join(os.path.dirname(__file__), f"resource/{tag}"))
            all_file_name = os.listdir(str(img_path))
            img_name = random.choice(all_file_name)
            img = img_path / img_name
            await random_emotion.send(MessageSegment.image(img))
        except:
            await random_emotion.send("还没有这个表情哦, 快去添加叭~", at_sender=True)



add_emotion = on_command("添加随机表情", priority=50, block=True)

@add_emotion.handle()
async def _():
    ...




# 建议使用 API 而不是本地
# 空间占用好大 >_<