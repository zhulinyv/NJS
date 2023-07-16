import httpx

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from nonebot import logger

def Anosu(N:int = 1, Tag:str = "", R18:int = 0):
    msg = ""
    if 1 <= N <= 10:
        msg += f"Bot_NICKNAME为你准备了{N}张随机{'r18'if R18 else ''}{Tag}色图。"
    elif N > 10:
        N = 1
        if R18:
            msg += f"Bot_NICKNAME为你的身体着想，为你准备了一张随机r18{Tag}色图。"
        else:
            msg += f"Bot_NICKNAME被禁止单次发送超过10张色图...但是，{Bot_NICKNAME}为你准备了一张随机{Tag}色图。"
    else:
        N = 1
        msg += f"Bot_NICKNAME接收到了奇怪的数量参数，不过Bot_NICKNAME送你一张随机{'r18'if R18 else ''}{Tag}色图。"
    logger.info(f"正在从 anosu 获取图片。")
    resp = httpx.get(f"https://image.anosu.top/pixiv/json?num={N}&r18={R18}&keyword={Tag}")
    if resp.status_code == 200:
        resp = resp.text
        resp = ''.join(x for x in resp if x.isprintable())
        anosu_list = json.loads(resp)
        image_list = []
        if anosu_list:
            N = len(anosu_list)
            for i in range(N):
                image_list.append(anosu_list[i]["url"])
        else:
            msg = f"没有找到【{Tag}】"
    else:
        logger.info(f"从 anosu 获取图片失败，status_code：{resp.status_code}")
        msg = "连接出错了..."
        image_list = None
    return msg, image_list