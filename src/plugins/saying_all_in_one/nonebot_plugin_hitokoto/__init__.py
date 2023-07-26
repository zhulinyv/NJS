import httpx
from nonebot import logger, on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from ..nonebot_plugin_dog.utils import *


hitokoto_matcher = on_command("一言", aliases={"一句"}, priority=60, block=True)

@hitokoto_matcher.handle()
async def hitokoto(event: GroupMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if not (await check_group_allow(str(event.group_id))):
        await hitokoto_matcher.finish(notAllow, at_sender=True)
    if args:
        return
    async with httpx.AsyncClient() as client:
        response = await client.get("https://v1.hitokoto.cn?c=a&c=b&c=c&c=d&c=h")
    if response.is_error:
        logger.error("获取一言失败")
        return
    data = response.json()
    msg = data["hitokoto"]
    add = ""
    if works := data["from"]:
        add += f"《{works}》"
    if from_who := data["from_who"]:
        add += f"{from_who}"
    if add:
        msg += f"\n——{add}"
    await matcher.finish(msg)
