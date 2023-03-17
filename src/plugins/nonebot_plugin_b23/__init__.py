import httpx
from nonebot import on_command, get_driver
from nonebot.internal.matcher import Matcher
from nonebot.params import RawCommand

from .config import Config

config = Config.parse_obj(get_driver().config)

b23_command = on_command(
    "b站热搜",
    aliases=config.b23_commands,
    block=config.b23_block,
    priority=config.b23_priority
)


@b23_command.handle()
async def b23_handler(matcher: Matcher, command: str = RawCommand()):
    try:
        async with httpx.AsyncClient() as r:
            r: httpx.AsyncClient
            res = await r.get(
                "https://app.bilibili.com/x/v2/search/trending/ranking"
            )
            msg = f"{command}:\n"
            for index, i in enumerate(res.json().get("data", {}).get("list", [])):
                msg += f"{index + 1}.{i['show_name']}\n"
            await matcher.send(msg.strip())
    except Exception as e:
        await matcher.send(f"获取B站热搜失败,error:{e}")
