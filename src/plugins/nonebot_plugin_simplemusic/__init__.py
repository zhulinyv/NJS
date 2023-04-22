import asyncio
import traceback

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message

from .data_source import Func, Source, sources

__plugin_meta__ = PluginMetadata(
    name="点歌",
    description="点歌，支持qq、网易、酷我、酷狗、咪咕、b站音频区",
    usage="点歌/qq点歌/网易点歌/酷我点歌/酷狗点歌/咪咕点歌/b站点歌 + 关键词",
    extra={
        "unique_name": "simplemusic",
        "example": "点歌 万古生香",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.1.4",
    },
)


def retry(func: Func, count=3, sleep=3):
    async def wrapper(*args, **kwargs):
        for i in range(count):
            try:
                res = await func(*args, **kwargs)
                return res
            except:
                if i >= count - 1:
                    raise
                await asyncio.sleep(sleep)

    return wrapper


def create_matchers():
    def create_handler(source: Source) -> T_Handler:
        async def handler(matcher: Matcher, msg: Message = CommandArg()):
            keyword = msg.extract_plain_text().strip()
            if not keyword:
                matcher.block = False
                await matcher.finish()

            res = None
            try:
                res = await retry(source.func)(keyword)
                if not res:
                    res = f"{source.name}中找不到相关的歌曲"
            except Exception:
                logger.warning(traceback.format_exc())
                res = "出错了，请稍后再试"
            await matcher.finish(res)

        return handler

    for source in sources:
        on_command(
            source.keywords[0], aliases=set(source.keywords), block=True, priority=12
        ).append_handler(create_handler(source))


create_matchers()


async def handler(matcher: Matcher, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        matcher.block = False
        await matcher.finish()

    res = None
    for source in sources:
        try:
            res = await source.func(keyword)
        except:
            pass
        if res:
            await matcher.finish(res)
    if not res:
        await matcher.finish("找不到相关的歌曲")


on_command("点歌", block=True, priority=12).append_handler(handler)
