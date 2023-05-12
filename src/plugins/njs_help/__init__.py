import os
import nonebot
from pathlib import Path
from nonebot import require
from nonebot import on_command
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageSegment,
    GroupMessageEvent,
    )

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import get_new_page

from .utils import *

try:
    NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]
except Exception:
    NICKNAME: str = "脑积水"



njs_help = on_command("njs", aliases={"NJS"}, priority=2, block=True)
@njs_help.handle()
async def _(bot: Bot, event: Event, msg: Message = CommandArg()):
    number = msg.extract_plain_text().strip()
    if number in ["帮助", "菜单", "列表", "help", "Help" ,"HELP"]:
        # 制作图片发送
        async with get_new_page(viewport={"width": 300, "height": 300}) as page:
            await page.goto(
                "file://" + (str(Path(__file__).parent / "resource" /"njs_help.html")),
                wait_until="networkidle",
            )
            pic = MessageSegment.image(await page.screenshot(full_page=True, path="./src/plugins/njs_help/njs_help.png"))
        # 群聊转发
        if isinstance(event, GroupMessageEvent):
            msgs = []
            message_list = []
            message_list.append(help_reply_head)
            message_list.append(pic)
            message_list.append(help_reply_foot)
            for msg in message_list:
                msgs.append({
                    'type': 'node',
                    'data': {
                        'name': f"{NICKNAME}",
                        'uin': bot.self_id,
                        'content': msg
                    }
                })
            await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)
        # 其它直接发送
        else:
            await njs_help.send(help_reply_head)
            await njs_help.send(pic)
            await njs_help.send(help_reply_foot)
    elif number.isdigit():
        try:
            await njs_help.finish('指令如下: \n' + help_reply[f"h{number}_r"], at_sender=True)
        except KeyError:
            try:
                if int(number) <= 99:
                    if number in ["1", "14", "58", "76"]:
                        help_image = Path(os.path.join(os.path.dirname(__file__), "resource")) / f"h{number}.jpg"
                    else:
                        help_image = Path(os.path.join(os.path.dirname(__file__), "resource")) / f"h{number}.png"
                    await njs_help.finish('指令如下: \n' + MessageSegment.image(help_image), at_sender=True)
                else:
                    await njs_help.finish('功能扩建中...', at_sender=True)
            except ActionFailed:
                try:
                    if isinstance(event, GroupMessageEvent):
                        msgs = []
                        message_list = []
                        message_list.append('指令如下: \n' + MessageSegment.image(help_image))
                        for msg in message_list:
                            msgs.append({
                                'type': 'node',
                                'data': {
                                    'name': f"{NICKNAME}",
                                    'uin': bot.self_id,
                                    'content': msg
                                }
                            })
                        await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)
                    else:
                        await njs_help.finish("指令发不出来啦~! 请查看帮助文档:\n优先: zhulinyv.github.io/NJS\n备用: cnblogs.com/xytpz/p/NJS.html", at_sender=True)
                except Exception as e:
                    error = f"{type(e).__name__}: {e}"
                    logger.error(f"错误日志{error}")
                    await njs_help.finish("指令发不出来啦~! 请查看帮助文档:\n优先: zhulinyv.github.io/NJS\n备用: cnblogs.com/xytpz/p/NJS.html", at_sender=True)
    else:
        await njs_help.finish('功能扩建中...', at_sender=True)