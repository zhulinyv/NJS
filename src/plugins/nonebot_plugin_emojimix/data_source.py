import httpx
import traceback
from typing import List, Union, Optional

from nonebot import get_driver
from nonebot.log import logger

from .config import Config
from .emoji_data import emojis, dates


emoji_config = Config.parse_obj(get_driver().config.dict())

API = "https://www.gstatic.com/android/keyboard/emojikitchen/"


def create_url(date: str, emoji1: List[int], emoji2: List[int]) -> str:
    def emoji_code(emoji: List[int]):
        return "-".join(map(lambda c: f"u{c:x}", emoji))

    u1 = emoji_code(emoji1)
    u2 = emoji_code(emoji2)
    return f"{API}{date}/{u1}/{u1}_{u2}.png"


def find_emoji(emoji_code: str) -> Optional[List[int]]:
    emoji_num = ord(emoji_code)
    for e in emojis:
        if emoji_num in e:
            return e
    return None


async def mix_emoji(emoji_code1: str, emoji_code2: str) -> Union[str, bytes]:
    emoji1 = find_emoji(emoji_code1)
    emoji2 = find_emoji(emoji_code2)
    if not emoji1:
        return f"不支持的emoji：{emoji_code1}"
    if not emoji2:
        return f"不支持的emoji：{emoji_code2}"

    urls: List[str] = []
    for date in dates:
        urls.append(create_url(date, emoji1, emoji2))
        urls.append(create_url(date, emoji2, emoji1))

    try:
        async with httpx.AsyncClient(proxies=emoji_config.http_proxy, timeout=20) as client:  # type: ignore
            for url in urls:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.content
            return "出错了，可能不支持该emoji组合"
    except:
        logger.warning(traceback.format_exc())
        return "下载出错，请稍后再试"
