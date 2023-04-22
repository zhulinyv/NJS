import feedparser
from typing import Optional, List
from nonebot import get_driver
from datetime import datetime

from ..configs import PathConfig, ProxyConfig
from ..core.database import RSSNewsModel

pcfg = PathConfig.parse_obj(get_driver().config.dict())
xcfg = ProxyConfig.parse_obj(get_driver().config.dict())


async def get_news() -> Optional[List["RSSNewsModel"]]:
    """游戏公告/新闻"""
    url = f"{xcfg.rss_site}/arknights/news?filterout_title=封禁&limit=3"
    rss_data = feedparser.parse(url)
    if not rss_data or rss_data["status"] != 200:
        raise  # TODO
    if not rss_data["entries"]:
        return None

    latest_news = []
    for news in rss_data["entries"]:
        link = news["link"]
        data = await RSSNewsModel.filter(link=link).first()
        if data:
            continue

        time = datetime(*news["published_parsed"][:7])
        title = news["title"],
        # content = get_plain_text(news["summary"])
        content = news["summary"]
        await RSSNewsModel.create(
            time=time, title=title, content=content, link=link
        )
        latest_news.append(
            RSSNewsModel(time=time, title=title, content=content, link=link)
        )
    return latest_news


async def get_bilibili_dynamics():
    """B站动态"""
    ...
