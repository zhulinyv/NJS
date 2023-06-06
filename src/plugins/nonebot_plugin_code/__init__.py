# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/22 14:16
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py.py
# @Software: PyCharm

# @Time    : 2023/01/19 21:00
# @UpdateBy: Limnium
# 更新了正则的pattern，完善了返回机制，“优化”代码风格。
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, Message, Bot, GroupMessageEvent
from .run import run

runcode = on_command('code', priority=5)


@runcode.handle()
async def runcode_body(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    code = str(arg).strip()
    res = await run(code)
    messages = {"type": "node", "data": {"name": "return", "uin": bot.self_id, "content": Message(res)}}
    if isinstance(event, GroupMessageEvent):
        return await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=messages)
    else:
        return await bot.call_api("send_private_forward_msg", user_id=event.user_id, messages=messages)


__usage__ = """
发送
code [语言] [stdin(空格将被替换为回车)]
[代码]


运行代码示例(python)：
    code py 你好
    print(input())

目前仅支持c/cpp/c#/py/php/go/java/js
运行于：https://glot.io/
"""

__help_plugin_name__ = "在线运行代码"

__permission__ = 2
__help__vesion__ = '0.1'
