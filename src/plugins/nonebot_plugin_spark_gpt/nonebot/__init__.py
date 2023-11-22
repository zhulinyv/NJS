from arclet.alconna import Alconna, Args, Option, Arparma  # noqa: F401
from nonebot_plugin_alconna import on_alconna

from nonebot_plugin_saa_cx import MessageFactory, Image
from . import (
    chat_consumer,
    chat_manager,
    command_manager,
    prompt_manager,
    model_manager,
)  # noqa: F401
from ..const.menus import menus
from ..utils import Command_Start

shelp = on_alconna(Alconna(f"{Command_Start}shelp"))


@shelp.handle()
async def shelp_():
    image = await menus.get_menu_image("all")
    await MessageFactory(Image(image)).send()
