import asyncio
import json
import os
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image
from lxml import etree
from nonebot import get_driver, logger
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import Config
from .._utils import get_browser
from .._utils import request_

activity_config = Config.parse_obj(get_driver().config.dict())
DATA_PATH = Path(activity_config.activities_data_path)
IMG_PATH = Path(activity_config.activities_img_path)


async def get_activities(*, is_force: bool = False, is_cover: bool = False):
    """获取近期活动"""
    announcement_url = "https://ak.hypergryph.com/news.html"
    result = None
    for retry in range(5):
        try:
            result = await request_(url=announcement_url)
        except httpx.TimeoutException:
            logger.warning(f"获取方舟近期活动第{retry + 1}次失败...")
            continue
        else:
            break
    if not result:
        return None
    text = result.text
    dom = etree.HTML(text, etree.HTMLParser())
    activity_urls = dom.xpath(
        "//ol[@class='articleList' and @data-category-key='ACTIVITY']/li/a/@href"
    )[:3]
    activity_titles = dom.xpath(
        "//ol[@class='articleList' and @data-category-key='ACTIVITY']/li/a/h1/text()"
    )[:3]
    activity_times = dom.xpath(
        "//ol[@class='articleList' and @data-category-key='ACTIVITY']/li/a/span[@class='articleItemDate']/text()"
    )[:3]
    activity_data = {time: {"url": f"https://ak.hypergryph.com{activity_urls[idx]}", "title": activity_titles[idx].strip()} for idx, time in enumerate(activity_times)}

    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    if not os.path.exists(DATA_PATH / "activities.json"):
        with open(DATA_PATH / "activities.json", 'w', encoding='utf-8') as f:
            json.dump({}, f)
    update_flag = await write_in_data(activity_data, activity_times[0])
    if update_flag or is_force:
        latest = activity_times[0]
        msg = await get_latest_info(activity_data, latest, is_cover=is_cover)
        return msg or None
    return None


async def write_in_data(activity_data: dict, latest: str) -> bool:
    """把最新的三条活动信息写入文件"""
    update_flag = False
    with open(DATA_PATH / "activities.json", 'r', encoding='utf-8') as f_read:
        old_data = json.load(f_read)
        if old_data and old_data['latest'] not in activity_data.keys():
            update_flag = True
            with open(DATA_PATH / "activities.json", 'w', encoding='utf-8') as f_write:
                json.dump(
                    {"latest": latest, "details": activity_data}
                    , f_write
                )
    return update_flag


async def get_latest_info(activity_data: dict, latest: str, *, is_cover: bool = False):
    """截图最新活动"""
    if not os.path.exists(IMG_PATH):
        os.makedirs(IMG_PATH)

    value = activity_data[latest]
    url = value['url']
    title = value['title']
    file_name = IMG_PATH / f"{title}.png"
    if file_name.exists() and not is_cover:
        return Message(
            f"{MessageSegment.image(file_name)}"
            f"{title}\n"
            f"公告更新日期(不是活动开始日期): {latest}\n"
            f"数据来源于: {url}"
        )

    page = None
    screenshot = None
    for retry in range(3):
        try:
            browser = await get_browser()
            if not browser:
                return None
            page = await browser.new_page()
            await page.goto(url, timeout=50000)
            await page.set_viewport_size({"width": 960, "height": 1080})
            await asyncio.sleep(1)
            screenshot = await page.screenshot(full_page=True, type='jpeg', quality=50)
        except TimeoutError as e:
            logger.warning(f"第{retry + 1}次获取方舟活动截图失败…… {e}")
            continue
        except Exception as e:
            if page:
                await page.close()
            logger.error(f"方舟活动截图失败！ - {e}")
            return None
        else:
            await page.close()
            break

    if screenshot:
        b_scr = BytesIO(screenshot)
        with Image.open(b_scr) as img:
            img.save(file_name)
        return Message(
            f"{MessageSegment.image(file_name)}"
            f"{title}\n"
            f"公告更新日期: {latest}\n"
            f"数据来源于: {url}"
        )
    if page:
        await page.close()

    return url
