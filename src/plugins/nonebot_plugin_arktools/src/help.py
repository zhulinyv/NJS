"""帮助"""
from .game_guess_operator import __plugin_meta__ as GUESS_META
from .misc_operator_birthday import __plugin_meta__ as BIRTHDAY_META
from .misc_monster_siren import __plugin_meta__ as SIREN_META
from .tool_announce_push import __plugin_meta__ as ANNOUNCE_META
from .tool_operator_info import __plugin_meta__ as INFO_META
from .tool_open_recruitment import __plugin_meta__ as RECRUIT_META
from .tool_sanity_notify import __plugin_meta__ as SAN_META
from .utils import __plugin_meta__ as UTILS_META

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from io import BytesIO
from nonebot_plugin_imageutils import text2image


HELP_DATAS = [
    GUESS_META,
    BIRTHDAY_META,
    SIREN_META,
    ANNOUNCE_META,
    INFO_META,
    RECRUIT_META,
    SAN_META,
    UTILS_META
]


help_msg = on_command("方舟帮助", aliases={"arkhelp"})

@help_msg.handle()
async def _():
    result = "\n".join(
        f"[color=red]{data.name}[/color]"
        f"\n{data.description}"
        f"\n{data.usage}\n"
        for data in HELP_DATAS
    )
    output = BytesIO()
    text2image(result).save(output, "png")
    await help_msg.finish(MessageSegment.image(output))
