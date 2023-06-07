from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from LittlePaimon.utils.brower import blhx_screenshot

from urllib.parse import quote
import string



__plugin_meta__ = PluginMetadata(
    name='碧蓝航线wiki',
    description='碧蓝航线wiki',
    usage='',
    extra={
        'author':   '(๑•小丫头片子•๑)',
        'version':  '0.1',
        'priority': 99,
    }
)

screenshot_cmd = on_command(
    '碧蓝航线wiki',
    priority=10,
    block=True
)


@screenshot_cmd.handle()
async def _(msg: Message = CommandArg()):
    url = 'https://wiki.biligame.com/blhx/'
    item = msg.extract_plain_text().strip()
    url += item
    # 转换链接格式
    url = quote(url, safe = string.printable)
    await screenshot_cmd.send(f'正在尝试获取wiki, 请稍等...更多信息请访问原文捏~{url}')
    try:
        img = await blhx_screenshot(url)
        await screenshot_cmd.send(MessageSegment.image(img))
    except Exception:
        await screenshot_cmd.send('wiki获取失败, 无法访问该网页, 请稍候再试')
