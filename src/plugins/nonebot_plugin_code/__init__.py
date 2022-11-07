# python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/22 14:16
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : __init__.py.py
# @Software: PyCharm
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message

from .run import run

runcode = on_command('code', priority=5)


@runcode.handle()
async def _(bot: Bot, event: MessageEvent):
    code = str(event.get_message()).strip()
    res = await run(code)
    await runcode.send(message=Message(res), at_sender=True)


__usage__ = """
发送
code [语言] [-i] [inputText]
[代码]

-i：可选 输入 后跟输入内容

运行代码示例(python)(无输入)：
    code py
        print("sb")
运行代码示例(python)(有输入)：
    code py -i 你好
        print(input())

目前仅支持c/cpp/c#/py/php/go/java/js
运行于：https://glot.io/
"""

__help_plugin_name__ = "在线运行代码"

__permission__ = 2
__help__vesion__ = '0.1'
