import os
import ujson as json

from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.plugin.on import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageSegment,
    GroupMessageEvent,
    )

from .utils import *
from .draw import draw_help



njs = on_command("njs", aliases={"NJS"}, priority=1, block=True)
@njs.handle()
async def _(bot: Bot, event: Event, msg: Message = CommandArg()):
    number = msg.extract_plain_text().strip()
    if number in ["帮助", "菜单", "列表", "help"]:
        await draw_help()
        help_img = MessageSegment.image(path / "help_new.png")
        if isinstance(event, GroupMessageEvent):
            msgs = []
            message_list = []
            message_list.append(head_msg)
            message_list.append(help_img)
            message_list.append(foot_msg)
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
            await njs.send(head_msg, at_sender=True)
            await njs.send(help_img)
            await njs.send(foot_msg)
    elif (number.isdigit()) and (int(number) > 0):
        with open("./data/njs_help_new/help.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        try:
            target_plugin = data["插件列表"][int(number) - 1]
        except IndexError:
            await njs.finish("功能扩建中...", at_sender=True)

        plugin_name = target_plugin["插件名"]
        import_name = target_plugin["导包名"]
        draw_color = target_plugin["显示颜色"]
        help_word = target_plugin["帮助文字"]
        help_image = target_plugin["帮助图片"]
        help_document = target_plugin["帮助文档"]
        help_bbcode = target_plugin["BBcode"]

        if draw_color != "":
            current_status = str(draw_color).replace("绿色", "正常可用").replace("蓝色", "部分停用").replace("红色", "正在维护")
        msg = f"\n{plugin_name}\n{import_name}\n当前状态: {current_status}\n指令如下: "
        if help_word != "":
            msg += "\n" + help_word
        if help_image != "":
            help_image = MessageSegment.image(Path(Path(os.getcwd()) / str(help_image).replace("./", "")))
            msg += "\n" + help_image
        if help_document != "":
            await md(Path(Path(os.getcwd()) / str(help_document).replace("./", "")))
            markdown_img = MessageSegment.image(path / "markdown_img.png")
            msg += "\n" + markdown_img
        if help_bbcode != "":
            await bbcode(help_bbcode)
            bbcode_img = MessageSegment.image(path / "bbcode_img.png")
            msg += "\n" + bbcode_img

        await njs.finish(msg, at_sender=True)
    else:
        await njs.finish("功能扩建中...", at_sender=True)