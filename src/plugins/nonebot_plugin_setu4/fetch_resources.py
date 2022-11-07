import os
from pathlib import Path
from httpx import AsyncClient
import nonebot
from nonebot.log import logger

# github_proxy, 可在env设置, 数据库的存放地址
try:
    database_path = nonebot.get_driver().config.database_path
except:
    database_path = 'https://raw.githubusercontent.com/Special-Week/nonebot_plugin_setu4/main/nonebot_plugin_setu4/resource/lolicon.db'

# 下载数据库并返回content
async def DownloadDatabase():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    }
    async with AsyncClient() as client:
        re = await client.get(url=database_path, headers=headers, timeout=120)
        if re.status_code == 200:
            with open(Path(os.path.join(os.path.dirname(__file__), "resource")) / "lolicon.db", "wb") as f:
                f.write(re.content)
            logger.success("成功获取lolicon.db")
            return "成功获取lolicon.db"
        else:
            logger.error(f"获取 lolicon.db 失败: {re.status_code}")
            return f"获取 lolicon.db 失败: {re.status_code}"


# 下载图片并且返回content,或者status_code
async def DownloadPic(url, client):
    try:
        headers = {
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        }
        re = await client.get(url=url, headers=headers, timeout=120)
        if re.status_code == 200:
            logger.success("成功获取图片")
            return re.content
        else:
            return re.status_code
    except:
        return 408
