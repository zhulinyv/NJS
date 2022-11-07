import httpx
from nonebot import logger, on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

hitokoto_matcher = on_command("一言", aliases={"一句"})

@hitokoto_matcher.handle()
async def hitokoto(matcher: Matcher, args: Message = CommandArg()):
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
