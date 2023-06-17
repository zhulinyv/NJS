
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

__version__ = "0.2.0"
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

al_command = on_command('al',aliases={'碧蓝'},priority=50,block=True)
tag_ser = on_command('alhelp',aliases={'碧蓝指令','碧蓝帮助'},priority=30,block=False)
tags = ['强度榜','装备榜','金部件榜','萌新榜','兵器榜','专武榜',
        '兑换榜','研发榜','改造榜','跨队榜','pt榜','氪金榜','打捞主线榜','打捞作战榜']




@tag_ser.handle()
async def _(matcher:Matcher):
    msg = '指令:碧蓝+\n----------'
    data:str = ''
    for one in tags:
        data += f'{one} | '
    msg += """data
    ----------
    碧蓝角色【角色名称】
    碧蓝装备【名称】
    """
    await matcher.finish(msg)

@al_command.handle()
async def _(matcher:Matcher,args:Message = CommandArg()):
    word = args.extract_plain_text()
    if word in tags:
        # 井号榜
        await matcher.finish(MessageSegment.image(await get_data(await jinghao(word))))
    elif word.startswith("角色"):
        # 舰船搜索
        with open((Path(__file__).parent.joinpath("data/ship.json")),
          mode='r',encoding='utf-8')as f:
            ships = json.load(f)
        word = word.replace("角色","")
        for key, value in ships.items():
            if any(word in sublist for sublist in value):
                await matcher.finish(MessageSegment.image(await get_ship_msg(key)))
        await matcher.finish("没有这个角色~")
    elif word.startswith("装备"):
        with open((Path(__file__).parent.joinpath("data/eq.json")),
          mode='r',encoding='utf-8')as f:
            eq = json.load(f)
        word = word.replace("装备","")
        for key, value in eq.items():
            if any(word in sublist for sublist in value):
                await matcher.finish(MessageSegment.image(await get_ship_msg(key)))
        await matcher.finish("没有这个装备~")
    else:
        await matcher.finish()