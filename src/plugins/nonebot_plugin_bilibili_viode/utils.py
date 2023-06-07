import re

from httpx import AsyncClient
import yaml
from pathlib import Path


def load_config(config: str) -> dict:
    # 读取配置文件
    # 传入参数：配置文件索引
    # 返回值：配置文件内容
    template_file = Path(__file__).parent / "template" / f"{config}.yaml"
    with open(template_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_number(number: int) -> str:
    # 格式化播放量
    # 传入参数：播放量
    # 返回值：格式化后的播放量
    if number >= 100000000:
        return str(round(number / 100000000, 1)) + "亿"
    elif number >= 10000:
        return str(round(number / 10000, 1)) + "万"
    else:
        return str(number)


async def bilibili_video_id_from_url(uri: str) -> str:
    # 正则匹配哔哩哔哩视频链接, 返回视频ID
    # 传入参数：视频链接
    # 返回值：视频ID
    pattern = re.compile(
        r"http(s)?:\/\/?(www\.)?(bilibili\.com|b23\.tv)\/(video\/)?(av[0-9]*|BV[A-Za-z0-9]*|[A-Za-z0-9]*)"
    )
    matches = pattern.finditer(uri)
    if matches:
        urlMatch = matches.__next__()
        if urlMatch.group(3) == "b23.tv":
            async with AsyncClient() as client:
                resp = await client.get(urlMatch.group())
                if resp.status_code == 302:
                    return await bilibili_video_id_from_url(resp.headers["Location"])
        return urlMatch.group(5)
    return None


def bilibili_video_id_validate(video_id: str) -> str:
    # 正则校验哔哩哔哩视频ID,返回视频id
    # 传入参数：视频ID
    # 返回值：视频id
    regex = (
        r"(av[0-9]*)|(BV1[A-Za-z0-9]{2}4[A-Za-z0-9]{1}1[A-Za-z0-9]{1}7[A-Za-z0-9]{2})"
    )
    match = re.match(regex, video_id)
    if match:
        return match.group(0)
    return None


async def get_share_sort_url(av_id: str):
    # 获取B站视频的分享短链接
    # 传入参数：AV号
    # 返回值：分享短链接 （https://b23.tv/xxxxxx）
    body = {
        "build": "6060600",
        "buvid": "0",
        "oid": av_id,
        "platform": "android",
        "share_channel": "QQ",
        "share_id": "main.ugc-video-detail.0.0.pv",
        "share_mode": "7",
    }
    async with AsyncClient() as client:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = await client.post(
            url="http://api.biliapi.net/x/share/click", headers=headers, data=body
        )
        if resp.status_code == 200:
            data = resp.json()
            if data["code"] == 0:
                return data["data"]["link"]
    raise ValueError("Get share sort url failed")
