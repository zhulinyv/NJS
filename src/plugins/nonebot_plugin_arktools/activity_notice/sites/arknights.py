"""方舟官网, https://ak.hypergryph.com/"""
from lxml import etree

from ..._utils import request_


async def pre_process():
    url = "https://ak.hypergryph.com/news/"
    response = await request_(url=url)
    text = response.text
    dom = etree.HTML(text, etree.HTMLParser())

    result = await get_arknights_activities(dom)

    result = await get_arknights_news(dom)

    ...


async def get_arknights_activities(dom):
    """活动(卡池、活动、合约)"""
    activities = dom.xpath("//ol[@data-category-key='ACTIVITY']/li/a/@href")[0]
    time = dom.xpath("//ol[@data-category-key='ACTIVITY']/li/a/span[@class='articleItemDate']/text()")[0]
    url = f"https://ak.hypergryph.com/{activities}"
    response = await request_(url=url)
    text = response.text
    dom_ = etree.HTML(text, etree.HTMLParser())
    paragraph = dom_.xpath("//p/strong/text() | //p/text[contains(string(), '时间')]")

    ...


async def get_arknights_news(dom):
    """新闻(制作组通讯)"""
    news = dom.xpath("//ol[@data-category-key='NEWS']/li/a/@href")[0]
    time = dom.xpath("//ol[@data-category-key='NEWS']/li/a/span[@class='articleItemDate']/text()")[0]
    url = f"https://ak.hypergryph.com/{news}"
    response = await request_(url=url)
    text = response.text
    dom_ = etree.HTML(text, etree.HTMLParser())

    ...




