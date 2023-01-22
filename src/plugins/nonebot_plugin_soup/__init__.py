'''
Name: Code.
Author: Monarchdos
Date: 2023-01-11
'''
from nonebot import on_command
from nonebot.plugin import on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment, GroupMessageEvent
from nonebot.plugin import PluginMetadata
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
__plugin_meta__ = PluginMetadata(
    name = "心灵鸡汤",
    description = "来一碗心灵鸡汤吧",
    usage = "鸡汤,毒鸡汤",
)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
url = "https://api.ayfre.com/"
jt = on_command('鸡汤', priority=1, block=True)
@jt.handle()
async def jt_(bot: Bot, event: GroupMessageEvent):
    res = str(requests.get(url=url+"jt?type=bot", verify=False).text)
    if "wwwroot" in res or "html" in res: res = "gg"
    await jt.send(message=Message(res), at_sender=True)

djt = on_command('毒鸡汤', priority=1, block=True)
@djt.handle()
async def djt_(bot: Bot, event: GroupMessageEvent):
    res = str(requests.get(url=url+"djt?type=bot", verify=False).text)
    if "wwwroot" in res or "html" in res: res = "gg"
    await djt.send(message=Message(res), at_sender=True)