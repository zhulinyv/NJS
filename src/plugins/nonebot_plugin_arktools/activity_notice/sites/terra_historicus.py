"""泰拉记事社, https://terra-historicus.hypergryph.com/"""
import time

from nonebot.log import logger

from ..._exceptions import APICodeException
from ..._utils import get_api, request_

APIS = get_api("terra-historicus")


async def get_comic_news():
    """获取泰拉记事社的最新漫画消息"""
    url = APIS["recentUpdate"]["url"]
    method = APIS["recentUpdate"]["method"]
    response = await request_(url=url, method=method)

    data = response.json()
    if data['code'] != 0:
        logger.error("泰拉记事社最新漫画获取失败")
        raise APICodeException(status=response['code'])

    data = response.json()['data']
    logger.info(f"comic_data: {data}")
    result = []
    for _ in data[:3]:
        result.append(await process_comic_news(_))
    logger.info(f"comic_result: {result}")
    return result


async def process_comic_news(news_data: dict) -> dict:
    """获取公告中的图片等信息"""
    cid = news_data['comicCid']
    url = APIS["comic-data"]["url"].format(cid)
    method = APIS["comic-data"]["method"]
    response = await request_(url=url, method=method)

    data = response.json()
    if data['code'] != 0:
        raise APICodeException(status=response['code'])

    data = response.json()['data']

    title = data['title']
    subtitle = data['subtitle']
    authors = data['authors']
    keywords = data['keywords']
    cover = data['cover']

    date = data['updateTime']
    date = time.localtime(date)
    date = time.strftime("%Y-%m-%d", date)

    return {
        "title": title,
        "subtitle": subtitle,
        "authors": authors,
        "keywords": keywords,
        "date": date,
        "cover": cover,
        "url": f"https://terra-historicus.hypergryph.com/comic/{cid}"
    }


