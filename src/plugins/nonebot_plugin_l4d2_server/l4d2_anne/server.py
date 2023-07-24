import asyncio
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union

import httpx
from bs4 import BeautifulSoup
from nonebot.log import logger

from ..l4d2_queries.localIP import ALL_HOST, Group_All_HOST
from ..l4d2_utils.config import ANNE_IP, CONFIG_PATH, anne_url, headers

# 储存anne服务器ip
anne_url = "https://sb.trygek.com/"
# ANNE_IP = {}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
}


async def updata_anne_server():
    """更新anne服务器列表"""
    data = httpx.get(anne_url, headers=headers).content
    soup = BeautifulSoup(data, "html.parser")
    tbody = soup.find("tbody")
    if not tbody:
        return
    n = 0
    ip_list = []
    while n < 50:
        n += 1
        tr = tbody.find(id=f"server_{n}")  # type: ignore
        if tr:
            td: str = tr.select_one("td:nth-of-type(5)").get_text()  # type: ignore
        else:
            continue
        if not td:
            continue
        else:
            ip_list.append(td)
    if not ip_list:
        return None
    ip_dict: Dict[str, List[Dict[str, str]]] = {"云": []}
    n: int = 0

    for i, ip in enumerate(ip_list, start=1):
        ip_dict["云"].append({"id": str(i), "ip": ip})

    # ANNE_IP.update(ip_dict)
    with open(Path(CONFIG_PATH.parent / "l4d2/云.json"), "w", encoding="utf-8") as f:
        json.dump(ip_dict, f, indent=4, ensure_ascii=False)
    # print(ANNE_IP)
    ANNE_IP.update(ip_dict)
    return ip_dict


def server_key():
    """响应的服务器开头"""
    a = set()
    for tag1, value in ALL_HOST.items():
        try:
            a.add(tag1)
        except AttributeError:
            a.add("希腊那我从来没有想过这个事情")
    return a


def group_key():
    """响应群组服务器开头"""
    a = set()
    for tag1, value in Group_All_HOST.items():
        try:
            a.add(tag1)
        except AttributeError:
            a.add("希腊那我从来没有想过这个事情")
    return a
