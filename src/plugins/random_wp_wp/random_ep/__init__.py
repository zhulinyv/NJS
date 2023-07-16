import os
import random
from pathlib import Path
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment

from .nonebot_plugin_randomnana import *


dz = on_command('我测你们码', aliases={'随机丁真', '丁真', '一眼丁真'}, priority=50, block=True)
ikun = on_command("ikun", aliases={'小黑子', '坤坤', '随机坤坤'}, priority=50, block=True)
ht = on_command('随机胡桃', aliases={'胡桃', '七濑胡桃'}, priority=50, block=True)
cj = on_command('柴郡', aliases={'随机柴郡', '猫猫', '随机猫猫'}, priority=50, block=True)
kemomimi = on_command('kemomimi', aliases={'兽耳酱', '狐狸娘', '随机兽耳酱'}, priority=50, block=True)
bsn = on_command('白圣女', aliases={'随机白圣女'}, priority=50, block=True)


@dz.handle()
async def _():
    img_path = Path(os.path.join(os.path.dirname(__file__), "resource/dz"))
    all_file_name = os.listdir(str(img_path))
    img_name = random.choice(all_file_name)
    img = img_path / img_name
    try:
        await dz.send(MessageSegment.image(img))
    except:
        await dz.send("我测你们码")

@ikun.handle()
async def ikun_handle():
    await ikun.send(MessageSegment.image(file='https://www.duxianmen.com/api/ikun/'))

@ht.handle()
async def ikun_handle():
    await ikun.send(MessageSegment.image(file='https://img.moehu.org/pic.php?id=mc'))

@cj.handle()
async def _():
    img_path = Path(os.path.join(os.path.dirname(__file__), "resource/cj"))
    all_file_name = os.listdir(str(img_path))
    img_name = random.choice(all_file_name)
    img = img_path / img_name
    await dz.send(MessageSegment.image(img))

@kemomimi.handle()
async def _():
    await kemomimi.send(MessageSegment.image(file='https://img.moehu.org/pic.php?id=kemomimi'))

@bsn.handle()
async def _():
    img_path = Path(os.path.join(os.path.dirname(__file__), "resource/bsn"))
    all_file_name = os.listdir(str(img_path))
    img_name = random.choice(all_file_name)
    img = img_path / img_name
    await dz.send(MessageSegment.image(img))



# 建议使用 API 而不是本地
# 空间占用好大 >_<