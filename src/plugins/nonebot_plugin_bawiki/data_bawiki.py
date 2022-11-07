from aiohttp import ClientSession
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import config
from .const import BAWIKI_DB_URL


async def db_get(suffix, raw=False):
    async with ClientSession() as c:
        async with c.get(f"{BAWIKI_DB_URL}{suffix}", proxy=config.proxy) as r:
            return (await r.read()) if raw else (await r.json())


async def db_get_wiki_data() -> dict:
    return await db_get("data/wiki.json")


async def db_wiki_stu(name):
    wiki = (await db_get_wiki_data())["student"]
    if not (url := wiki.get(name)):
        return "没有找到该角色的角评，可能是学生名称错误或者插件还未收录该角色角评"
    return MessageSegment.image(await db_get(url, True))
