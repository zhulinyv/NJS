from pathlib import Path
from typing import Union

from httpx import AsyncClient
from nonebot.log import logger

from .config import config


async def download_database() -> str:
    """下载数据库"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    }
    async with AsyncClient() as client:
        re = await client.get(url=config.database_path, headers=headers, timeout=120)
        if re.status_code == 200:
            with open(Path(__file__).parent / "resource/lolicon.db", "wb") as f:
                f.write(re.content)
            logger.success("成功获取lolicon.db")
            return "成功获取lolicon.db"
        else:
            logger.error(f"获取 lolicon.db 失败: {re.status_code}")
            return f"获取 lolicon.db 失败: {re.status_code}"


async def download_pic(url: str, client: AsyncClient) -> Union[bytes, int]:
    "下载图片并且返回content(bytes),或者status_code"
    try:
        re = await client.get(url=url, timeout=120)
        if re.status_code != 200:
            return re.status_code
        logger.success("成功获取图片")
        return re.content
    except Exception:
        return 408
