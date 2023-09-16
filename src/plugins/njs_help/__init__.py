import os
import asyncio
import ujson as json

from nonebot.params import CommandArg
from nonebot.plugin.on import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageEvent,
    MessageSegment,
    GroupMessageEvent,
    )

from .utils import *
from .draw import draw_help



njs = on_command("njs", aliases={"NJS"}, priority=1, block=True)
@njs.handle()
async def _(bot: Bot, event: Event, msg: Message = CommandArg()):
    number = msg.extract_plain_text().strip()
    name_list = []
    with open("./data/njs_help/help.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        all_data = data["插件列表"]
    for plugin_info in all_data:
        name_list.append(plugin_info["插件名"])

    if number in ["帮助", "菜单", "列表", "help"]:
        await draw_help(all_data)
        help_img = MessageSegment.image(path / "help.png")
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
            asyncio.sleep(1)
            await njs.send(help_img)
            asyncio.sleep(1)
            await njs.send(foot_msg)
    else:
        global get_plugin, draw_plugin_help

        async def get_plugin(data, num):
            global target_plugin
            try:
                target_plugin = (data[int(num) - 1])
            except IndexError:
                await njs.finish("功能扩建中...", at_sender=True)
            except ValueError:
                try:
                    target_plugin = (data[name_list.index(f"{num}")])
                except ValueError:
                    await njs.finish("功能扩建中...", at_sender=True)
            return target_plugin

        async def draw_plugin_help(plugin):
            try:
                extra_plugin = plugin["extra"]
                await draw_help(extra_plugin)
                help_img = MessageSegment.image(path / "help.png")
                await njs.send("本插件包含多个插件, 发送序号继续获取帮助" + help_img, at_sender = True)
            except KeyError:
                plugin_name = plugin["插件名"]
                import_name = plugin["导包名"]
                draw_color = plugin["显示颜色"]
                help_word = plugin["帮助文字"]
                help_image = plugin["帮助图片"]
                help_document = plugin["帮助文档"]
                help_bbcode = plugin["BBcode"]

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
        await draw_plugin_help(await get_plugin(all_data, number))

@njs.got("num")
async def _(event: MessageEvent):
    num = str(event.message)
    await draw_plugin_help(await get_plugin(target_plugin["extra"], int(num) - 1))