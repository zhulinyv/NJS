
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment
)

from pathlib import Path
try:
    import ujson as json
except:
    import json

from .bili import jinghao,get_data, get_ship_msg

__version__ = "0.1.0"
__plugin_meta__ = PluginMetadata(
    name="碧蓝航线攻略",
    description='碧蓝航线井号榜等等攻略',
    usage='碧蓝航线攻略',
    type="application",
    homepage="https://github.com/Agnes4m/nonebot_plugin_AL",
    supported_adapters={"~onebot.v11"},
    extra={
        "version": __version__,
        "author": "Agnes4m <Z735803792@163.com>",
    },
)

al_command = on_command('al',aliases={'碧蓝航线'},priority=30,block=True)
tag_ser = on_command('alhelp',aliases={'碧蓝航线指令','碧蓝航线帮助'},priority=30,block=True)
tags = ['强度榜','装备榜','金部件榜','萌新榜','兵器榜','专武榜',
        '兑换榜','研发榜','改造榜','跨队榜','pt榜','氪金榜','打捞主线榜','打捞作战榜']
with open((Path(__file__).parent.joinpath("ship.json")),
          mode='r',encoding='utf-8')as f:
    ships = json.load(f)

@tag_ser.handle()
async def _(matcher:Matcher):
    msg = '指令:碧蓝+\n----------'
    data:str = ''
    for one in tags:
        data += f'{one} | '
    msg += data
    msg += "----------"
    msg += "碧蓝航线角色【角色名称】"
    await matcher.finish(msg)

@al_command.handle()
async def _(matcher:Matcher,args:Message = CommandArg()):
    word = args.extract_plain_text()
    if word in tags:
        # 井号榜
        await matcher.finish(MessageSegment.image(await get_data(await jinghao(word))))
    elif word.startswith("角色"):
        # 舰船搜索
        word = word[3:]
        for key, value in ships.items():
            if any(word in sublist for sublist in value):
                await matcher.finish(MessageSegment.image(await get_ship_msg(key)))
        await matcher.finish("没有这个角色~")
    else:
        await matcher.finish()