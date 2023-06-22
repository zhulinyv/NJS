
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    Bot,
    Event,
    GroupMessageEvent,
)
import traceback
from pathlib import Path
try:
    import ujson as json
except:
    import json


from .bili import jinghao,get_data, get_ship_msg
from .send_message import blhx
from .config import ADMIN

logo ="""
    ......                  ` .]]@@@@@@@@@@@@@@@@@@@@@@@@@@@@@OO^       
    ......                ,/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@OO^       
    ......            /O@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@OO^       
    `.....           ,@^=.OOO\/\@@@@@@@@@@@@@@@@@@@@OO//@@@@@/OO\]]]OO\]
    ``....          ,@@/=^OOOOOOOO@@@@@@@@@@@\]OOOOOOO^^=@@@@OOOOOOOOOOO
    `.....          O@O^==OOOOOOOO@@@/.,@@@OOOOOOOOOOO\O,@@@@OOOOOOOOO@@
    ......    ,    .@@@^=`OOOOOOOOO/  ,O@@OOOOOOOOOOOOOO.O@@@OO/[[[[[[[.
    ......    =..,//@@@^=`OOOOOOOOO@.*=@@@OOOOOOOOOOOOOO]@@@OOO.     ,/`
    ......    =.\O]`,@O^\=OOOO@@@@@@O`=@@@@@@@OOOOOOOO*O,OO^....[[``]./]
    ......    ,^.oOoO@O^=,OO@@@@@OoO`\O\OO@@@@OOOOOOOOO]@@^.]]]/OOOo.,OO
    ......     =.=OOOO@@@@/[[=/.^,/....*.=^,[O@@@@OOOO.@@OOOOOOOOO/..OOO
    ......      \.\OO`.,....*`.=.^.......=....=@O[\@@O@@[^ ,`.=Oo*.,OOO/
    ......       ,@,`...  ....=^/......../....=/O^....\..O]/[\O[*]/OOO. 
    ......       ]@^.,....*..=O\^........^..*.O.\O.^..=^\..,\/\@OOO[.   
    ......    ,,`O^.,..../.,O`//........=..=`=^.=O`O..=^..OOO*/OOO.     
    ......   .=.=@..^...=^/O`*OO.]...o**\.,/=^...O^@^..^...OO^=`OOO`    
    ......  `=.,O^./.*.,OO`,.,/@/.*,O`,O*/@/`....\O\^......Oo^.^,OOO.   
    ...... .,`.o=^=^.../`...]/`***/O^/@oO@`..[[[[\/=\......O^^...=OO^   
    ......  ^.=`O^O.*.=\],]]]/\O/\@O[=O/`        =.=O....=^O^*....OOO.  
    ...... =../=OO^.*.=@@[[,@@@\ .. ..    ,\@@@@@] =O...`=^@`.....=OO^  
    ...... `..^=OO^.^,@`  ^ =oO\          .O\O@\.,\@@..,^OoO......=OOO. 
    ...... ^...=OO^.^.@^ =^*=^,O          \..Ooo^  ,@..=OOOO..*....OOO. 
    ...... ^...=o@^.`.O@. .  ... .. ....  ^.*`.*^  =^..o@oO@*.=....OOO^ 
    ...... ^...=oOO.*.\O   ... .......... .\   ` ,=^*.,OOOO@^.=`^..=OO\ 
    ...... ^...*`OO.*.=O ........          ......,`*^.=OOOo@^.=^^..=OOO.
    ...... \....*oO^..*O^ ....... @OO[[[`  ......../.,@OOOo@^..OO...OOO`
    ...... =.....*.=`..,O`       .O.....=   ... ^.=..OOOOO=O@..=O^..OOO^
    ...... .^...**.O@...\O^ .     \.....`   .^ /.,^.=O@OO`=O@^..OO`.=OO\
    ...... .^...,.=O=@...OO@\      ,[O\=.    ./`.*.*OOOOO..OOO*..OO.,OOO
    ....../O....../^=O@`..O@@@@@]`    .* .,/@@/..../OOOOO*.,OOO..,OO`=OO
    @OO\ooO....,*/@^,@@@\..@^[\@@@@@@O]*]//[`@^*^*=OOOOOO^..=OO\...\^.\@
    OOooo^..`./oOO@/ =^\/^.^\\....=]......,/@@^O^*O.... .,][],OO\....\`.
    @Oooo\/]OOOOOO/  .  \.=^....,..........[.,OO^=^.    /    ,`\OO`.....
    """

__version__ = "0.3"
__plugin_meta__ = PluginMetadata(
    name="碧蓝航线攻略",
    description='碧蓝航线井号榜等等攻略',
    usage=logo,
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
        word = word.replace("角色","").replace(" ", "")
        for key, value in ships.items():
            if any(word in sublist for sublist in value):
                await matcher.finish(MessageSegment.image(await get_ship_msg(key)))
        await matcher.finish("没有这个角色~")
    elif word.startswith("装备"):
        with open((Path(__file__).parent.joinpath("data/eq.json")),
          mode='r',encoding='utf-8')as f:
            eq = json.load(f)
        word = word.replace("装备","").replace(" ", "")
        for key, value in eq.items():
            if any(word in sublist for sublist in value):
                await matcher.finish(MessageSegment.image(await get_ship_msg(key)))
        await matcher.finish("没有这个装备~")
    else:
        await matcher.finish()
        
# 以下为移植的内容
on_command(
    "blhx", 
    block=True, 
    priority=50,
    handlers=[blhx.send_ship_skin_or_info]
)

on_command(
    "blhx 过场", 
    block=True, 
    priority=10,
    handlers=[blhx.send_random_gallery]
)

on_command(
    "blhx 帮助", 
    block=True, 
    priority=10,
    handlers=[blhx.send_blhx_help]
)
on_command(
    "blhx 强度榜", 
    block=True, 
    priority=10,
    handlers=[blhx.send_pve_recommendation]
)
on_command(
    "blhx 强制更新", 
    block=True, 
    priority=10,
    permission=SUPERUSER,
    handlers=[blhx.force_update]
)
on_command(
    "blhx 最新活动", 
    block=True, 
    priority=10,
    handlers=[blhx.get_recently_event]
)
on_command(
    "blhx 备注", 
    block=True, 
    priority=10,
    permission=ADMIN,
    handlers=[blhx.set_nickname]
)
on_command(
    "blhx 移除备注", 
    block=True, 
    priority=10,
    permission=ADMIN,
    handlers=[blhx.remove_nickname]
)
on_command(
    "blhx 皮肤", 
    block=True, 
    priority=10,
    handlers=[blhx.quick_search_skin]
)
on_command(
    "blhx 大建", 
    block=True, 
    priority=10,
    handlers=[blhx.building]
)
