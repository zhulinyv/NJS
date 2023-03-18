"""塞壬唱片, https://monster-siren.hypergryph.com/"""
from lxml import etree
from nonebot.log import logger

from ..._exceptions import APICodeException
from ..._utils import get_api, request_

CATEGORY = {
    1: "新歌发布",
    5: "上线致辞",
    7: "资讯速递",
    8: "艺人近况",
    11: "特别电台"
}

APIS = get_api("monster-siren")


async def get_album_news() -> list:
    """获取最新三条公告"""
    url = APIS["news"]["url"]
    method = APIS["news"]["method"]
    response = await request_(url=url, method=method)

    data = response.json()
    if data['code'] != 0:
        logger.error("塞壬唱片最新专辑获取失败")
        raise APICodeException(status=response['code'])

    data = response.json()['data']
    logger.debug(f"album_data: {data}")
    result = []
    for _ in data['list'][:3]:
        result.append(await process_album_news(_))
    logger.debug(f"album_result: {result}")
    return result


async def process_album_news(news_data: dict) -> dict:
    """获取公告中的图片等信息"""
    cid = news_data['cid']
    url = APIS["news-data"]["url"].format(cid)
    method = APIS["news-data"]["method"]
    response = await request_(url=url, method=method)

    data = response.json()
    if data['code'] != 0:
        raise APICodeException(status=response['code'])

    data = response.json()['data']

    title = data['title']
    author = data['author']
    date = data['date']

    cate = data['cate']
    cate = CATEGORY[cate] if cate in CATEGORY.keys() else None

    content = data['content']
    dom = etree.HTML(content, etree.HTMLParser())
    img = dom.xpath("//img/@src")
    img = img[0] if img else None

    return {
        "title": title,
        "date": date,
        "cate": cate,
        "author": author,
        "img": img,
        "url": f"https://monster-siren.hypergryph.com/info/{cid}"
    }




