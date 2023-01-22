"""每日开放资源关卡"""
import nonebot
from nonebot import logger
from nonebot import on_regex
from nonebot.permission import SUPERUSER
from nonebot_plugin_apscheduler import scheduler
import os

from .config import Config
from .data_source import get_daily_sources
from .alter import alter_plan

global_config = nonebot.get_driver().config
ark_daily_config = Config(**global_config.dict())

material = on_regex(r"方舟今[日|天]*[资源]*[材料]*", priority=5, block=True)
super_cmd = on_regex(r"更新方舟今[日|天]*[资源]*[材料]*", permission=SUPERUSER, priority=1, block=True)


@material.handle()
async def _():
    rst_img = await get_daily_sources()
    if rst_img:
        rst = rst_img
    else:
        result = await alter_plan()
        result = ", ".join(result)
        rst = (
            f"方舟今日资源截图失败！\n请更换至非windows平台部署本插件\n或检查网络连接并稍后重试\n"
            f"今日开放的资源关卡：{result}"
        )
    await material.finish(rst)


@super_cmd.handle()
async def _():
    try:
        await get_daily_sources(is_force=True)
    except Exception as e:
        logger.error(f"方舟今日资源更新失败！{type(e)}: {e}")
        await super_cmd.finish("方舟今日资源更新失败！请稍后重试！")
    else:
        await super_cmd.finish("方舟今日资源更新完成！")


@scheduler.scheduled_job(
    "cron",
    hour=4,
    minute=1,
)
async def _():
    try:
        await get_daily_sources(is_force=True)
    except Exception as e:
        logger.error(f"方舟今日资源更新失败！{type(e)}: {e}")


driver = nonebot.get_driver()
@driver.on_startup
async def _():
    if not os.path.exists(ark_daily_config.daily_levels_path):
        os.makedirs(ark_daily_config.daily_levels_path)
    await get_daily_sources(is_force=True)
