import httpx

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from nonebot import logger

def Lolicon(N:int = 1, Tag:str = "", R18:int = 0):
    if Tag:
        tag_list = Tag.strip().split()
        tag = "&tag="
        for seg in tag_list[:3]:
            tag += f"{seg}|"
        else:
            tag = tag[:-1]
    else:
        tag = ""

    msg = ""
    if 1 <= N <= 10:
        msg += f"Bot_NICKNAME为你准备了{N}张随机{'r18'if R18 else ''}{tag[5:]}色图。"
    elif N > 10:
        N = 1
        if R18:
            msg += f"Bot_NICKNAME为你的身体着想，为你准备了一张随机r18{tag[5:]}色图。"
        else:
            msg += f"Bot_NICKNAME被禁止单次发送超过10张色图...但是，{Bot_NICKNAME}为你准备了一张随机{tag[5:]}色图。"
    else:
        N = 1
        msg += f"Bot_NICKNAME接收到了奇怪的数量参数，不过Bot_NICKNAME送你一张随机{'r18'if R18 else ''}{tag[5:]}色图。"
    logger.info(f"正在从 Lolicon API 获取图片。")
    resp = httpx.get(f"https://api.lolicon.app/setu/v2?num={N}&r18={R18}{tag}&excludeAI=1")
    if resp.status_code == 200:
        resp = resp.text
        resp = ''.join(x for x in resp if x.isprintable())
        Lolicon_list = json.loads(resp)["data"]
        image_list = []
        if Lolicon_list:
            N = len(Lolicon_list)
            for i in range(N):
                image_list.append(Lolicon_list[i]["urls"]["original"])
        else:
            msg = f"没有找到【{tag}】"
    else:
        logger.info(f"从 Lolicon API 获取图片失败，status_code：{resp.status_code}")
        msg = "连接出错了..."
        image_list = None
    return msg, image_list