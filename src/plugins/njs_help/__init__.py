import io
import os
import nonebot
from pathlib import Path
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot_plugin_imageutils import text2image
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageSegment,
    GroupMessageEvent,
    )

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
        # 转为图片发送
        img = text2image(help_reply_body)
        output = io.BytesIO()
        img.save(output, format="png")
        image = MessageSegment.image(output)
        # 群聊转发
        if isinstance(event, GroupMessageEvent):
            msgs = []
            message_list = []
            message_list.append(help_reply_head)
            message_list.append(image)
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
            await njs_help.send(image)
            await njs_help.send(help_reply_foot)
    elif number.isdigit():
        try:
            await njs_help.finish('指令如下: \n' + help_reply[f"h{number}_r"], at_sender=True)
        except KeyError:
            if number in ["1", "14", "58", "76"]:
                help_image = Path(os.path.join(os.path.dirname(__file__), "resource")) / f"h{number}.jpg"
            else:
                help_image = Path(os.path.join(os.path.dirname(__file__), "resource")) / f"h{number}.png"
            await njs_help.finish('指令如下: \n' + MessageSegment.image(help_image), at_sender=True)
    else:
        await njs_help.finish('功能扩建中...', at_sender=True)