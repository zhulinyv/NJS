import re
import emoji
from typing import Union

from nonebot import on_regex
from nonebot.params import RegexDict
from nonebot.plugin import PluginMetadata

from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg

from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import MessageSegment as V12MsgSeg

from .config import Config
from .data_source import mix_emoji

__plugin_meta__ = PluginMetadata(
    name="emoji合成",
    description="将两个emoji合成为一张图片",
    usage="{emoji1}+{emoji2}，如：😎+😁",
    config=Config,
    extra={
        "unique_name": "emojimix",
        "example": "😎+😁",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.2.0",
    },
)


emojis = filter(lambda e: len(e) == 1, emoji.EMOJI_DATA.keys())
pattern = "(" + "|".join(re.escape(e) for e in emojis) + ")"
emojimix = on_regex(
    rf"^\s*(?P<code1>{pattern})\s*\+\s*(?P<code2>{pattern})\s*$",
    block=True,
    priority=13,
)


@emojimix.handle()
async def _(bot: Union[V11Bot, V12Bot], msg: dict = RegexDict()):
    emoji_code1 = msg["code1"]
    emoji_code2 = msg["code2"]
    result = await mix_emoji(emoji_code1, emoji_code2)
    if isinstance(result, str):
        await emojimix.finish(result)

    if isinstance(bot, V11Bot):
        await emojimix.finish(V11MsgSeg.image(result))
    elif isinstance(bot, V12Bot):
        resp = await bot.upload_file(type="data", name="emojimix", data=result)
        file_id = resp["file_id"]
        await emojimix.finish(V12MsgSeg.image(file_id))
