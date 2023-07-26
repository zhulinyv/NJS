"""
作者:萌新源
时间:2022/3/30
操作系统:debian for raspberry pi
修改请保留本插件的版权
本插件版权属于萌新源
要发布请注明出处
"""
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from httpx import AsyncClient

from ..nonebot_plugin_dog.utils import *

'''
星座查询 调用API http://hm.suol.cc/API/xzys.php?msg=
命令:#星座天蝎座 #星座巨蟹座
'''

xingzuo = on_command("星座", priority=50, block=True)


@xingzuo.handle()
async def xz(event: GroupMessageEvent, arg: Message = CommandArg()):
    if not (await check_group_allow(str(event.group_id))):
        await xingzuo.finish(notAllow, at_sender=True)
    url = f'http://hm.suol.cc/API/xzys.php?msg={arg}'
    async with AsyncClient() as r:
        get_data = await r.get(url)
    msg = get_data.text
    msg = msg.replace('{br}', '\n')
    await xingzuo.finish(Message(msg), at_sender=True)
