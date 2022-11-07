"""剿灭、蚀刻章、合约等活动到期提醒"""
import os

import nonebot
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Message
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .data_source import get_activities

global_config = nonebot.get_driver().config
activity_config = Config(**global_config.dict())

latest_activity = on_regex(r'[查看询]*方舟[最]*新+[活动闻]*', priority=5, block=True)


@latest_activity.handle()
async def _():
    rst_msg = await get_activities(is_force=True)
    if isinstance(rst_msg, Message):
        rst = rst_msg
    elif isinstance(rst_msg, str):
        rst = (
            f"方舟最新活动截图失败！\n请更换至非windows平台部署本插件\n或检查网络连接并稍后重试"
            f"最新的活动信息请见链接: {rst_msg}"
        )
    else:
        rst = "无法获得方舟最新活动信息！请稍后重试"
    await latest_activity.finish(rst)


@scheduler.scheduled_job(
    "cron",
    hour=4,
    minute=1,
)
async def _():
    try:
        await get_activities(is_force=True, is_cover=True)
    except Exception as e:
        logger.error(f"方舟最新活动检查失败！{type(e)}: {e}")


driver = nonebot.get_driver()
@driver.on_startup
async def _():
    if not os.path.exists(activity_config.activities_data_path):
        os.makedirs(activity_config.activities_data_path)
    if not os.path.exists(activity_config.activities_img_path):
        os.makedirs(activity_config.activities_img_path)
    await get_activities(is_force=True)
