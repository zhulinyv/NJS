
import httpx
from datetime import date
from pathlib import Path

from nonebot import require
from nonebot.adapters.onebot.v11 import Bot, MessageSegment

from nonebot_plugin_htmlrender import text_to_pic

try:
    import ujson as json
except ModuleNotFoundError:
    import json

PUSHDATA_FILE: Path = Path(__file__).parent/"PUSHDATA.json"


def read_json(file: Path = PUSHDATA_FILE) -> dict:
    if file.exists():
        with open(file, encoding="utf-8") as f:
            data = json.load(f)
        return data
    else:
        return {}


def write_json(data: dict, file: Path = PUSHDATA_FILE) -> None:
    with file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# 去除api返回内容中不符合json格式的部分
def html_to_json_func(text: str) -> json:
    """html -> json"""
    text = text.replace("<\/a>", "")
    text = text.replace("\n", "")

    # 去除html标签
    while True:
        address_head = text.find("<a target=")
        address_end = text.find(">", address_head)
        if address_head == -1 or address_end == -1:
            break
        text_middle = text[address_head:address_end + 1]
        text = text.replace(text_middle, "")

    # 去除key:desc值
    address_head: int = 0
    while True:
        address_head = text.find('"desc":', address_head)
        address_end = text.find('"cover":', address_head)
        if address_head == -1 or address_end == -1:
            break
        text_middle = text[address_head + 8:address_end - 2]
        address_head = address_end
        text = text.replace(text_middle, "")

    # 去除key:title中多引号
    address_head: int = 0
    while True:
        address_head = text.find('"title":', address_head)
        address_end = text.find('"festival"', address_head)
        if address_head == -1 or address_end == -1:
            break
        text_middle = text[address_head + 9:address_end - 2]
        if '"' in text_middle:
            text_middle = text_middle.replace('"', " ")
            text = text[:address_head + 9] + \
                text_middle + text[address_end - 2:]
        address_head = address_end

    data = json.loads(text)
    return data


# 信息获取
async def get_history_info(kind: str = "text") -> MessageSegment:
    async with httpx.AsyncClient() as client:
        month = date.today().strftime("%m")
        day = date.today().strftime("%d")
        url = f"https://baike.baidu.com/cms/home/eventsOnHistory/{month}.json"
        r = await client.get(url)
        if r.status_code == 200:
            r.encoding = "unicode_escape"
            data = html_to_json_func(r.text)
            today = f"{month}{day}"
            s = f"历史上的今天 {today}\n"
            len_max = len(data[month][month + day])
            for i in range(0, len_max):
                str_year = data[month][today][i]["year"]
                str_title = data[month][today][i]["title"]
                if i == len_max - 1:
                    s = s + f"{str_year} {str_title}"  # 去除段末空行
                else:
                    s = s + f"{str_year} {str_title}\n"
            if kind == "text":
                return MessageSegment.text(s)
            else:
                return MessageSegment.image(await text_to_pic(s))
        else:
            return MessageSegment.text("获取失败，请重试")


async def refresh_group_list(bot: Bot) -> list:
    """获取群聊列表"""
    groups = await bot.call_api("get_group_list", no_cache=True)
    g_list = []
    for group in groups:
        g_list.append(group["group_id"])
    return g_list
