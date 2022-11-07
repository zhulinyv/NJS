import contextlib
from typing import Optional

import nonebot
from nonebot import Driver
from nonebot.log import logger
from playwright.async_api import Browser, async_playwright

driver: Driver = nonebot.get_driver()


_browser: Optional[Browser] = None


async def init(**kwargs) -> Optional[Browser]:
    global _browser
    try:
        browser = await async_playwright().start()
        _browser = await browser.chromium.launch(**kwargs)
        return _browser
    except NotImplementedError:
        logger.warning("初始化 playwright 失败，请依次进行如下操作：")
        logger.warning("1.请检查 playwright 库和 uvicorn 库是否为最新版本")
        logger.warning("2.请删除 env 文件中的 “FASTAPI_RELOAD=true” 语句")
        logger.warning("3.请不要在 windows 环境下部署")
    except Exception as e:
        logger.warning(f"启动chromium发生错误 {type(e)}：{e}")
        if _browser:
            await _browser.close()
    return None


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)


# @driver.on_startup
def install():
    """自动安装、更新 Chromium"""
    logger.info("正在检查 Chromium 更新")
    import sys
    from playwright.__main__ import main

    sys.argv = ["", "install", "chromium"]
    with contextlib.suppress(SystemExit):
        main()
