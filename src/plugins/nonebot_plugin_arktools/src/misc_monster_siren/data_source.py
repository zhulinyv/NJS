import httpx
from typing import Union
from nonebot.adapters.onebot.v11 import MessageSegment


async def search_cloud(keyword: str) -> Union[str, MessageSegment]:
    """网易云"""
    url = "https://music.163.com/api/cloudsearch/pc"
    params = {"s": keyword, "type": 1, "offset": 0, "limit": 1}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, params=params)
        result = resp.json()
    if songs := result["result"]["songs"]:
        return MessageSegment.music("163", songs[0]["id"])
    return f"网易云音乐中没有找到“{keyword}”相关的歌曲哦"


async def search_tencent(keyword: str) -> Union[str, MessageSegment]:
    """qq音乐"""
    url = "https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg"
    params = {
        "format": "json",
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "notice": 0,
        "platform": "yqq.json",
        "needNewCode": 0,
        "uin": 0,
        "hostUin": 0,
        "is_xml": 0,
        "key": keyword,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        result = resp.json()
    if songs := result["data"]["song"]["itemlist"]:
        return MessageSegment.music("qq", songs[0]["id"])
    return f"QQ音乐中没有找到“{keyword}”相关的歌曲哦"
