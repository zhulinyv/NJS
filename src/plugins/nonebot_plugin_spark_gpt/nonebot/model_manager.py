from arclet.alconna import Alconna, Subcommand
from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_saa_cx import MessageFactory, Text, Image
from nonebot_plugin_spark_gpt.const import menus

from ..chatbots import chatbots
from ..utils import Command_Start

model = on_alconna(Alconna(f"{Command_Start}model",
                           Subcommand("help"),
                           Subcommand("list")))


@model.assign("$main")
async def mode_main():
    await MessageFactory(Text(menus.get_menu_string("model"))).finish()


@model.assign("help")
async def mode_help():
    await MessageFactory(Image(await menus.get_menu_image("model"))).finish()


@model.assign("list")
async def model_help():
    await MessageFactory(Image(await chatbots.get_image())).finish()
