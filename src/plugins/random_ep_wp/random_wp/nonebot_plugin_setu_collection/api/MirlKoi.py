import httpx

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from nonebot import logger

MirlKoi_list = {}
MirlKoi_list["iw233"] = []
MirlKoi_list["top"] = []
MirlKoi_list["yin"] = []
MirlKoi_list["cat"] = []
MirlKoi_list["xing"] = []
MirlKoi_list["mp"] = []
MirlKoi_list["pc"] = []

MirlKoi_tag = {
    "色图 随机色图 随机涩图": "iw233",
    "推荐": "top",
    "白毛 白发 银发": "yin",
    "兽耳 猫耳 猫娘": "cat",
    "星空 夜空 星空壁纸 夜空壁纸": "xing",
    "壁纸 竖屏壁纸 手机壁纸": "mp",
    "电脑壁纸 横屏壁纸": "pc"
    }

tag_dict = {}
for key in MirlKoi_tag:
    value = MirlKoi_tag[key]
    tag_dict[value] = key.split()[0]


def is_MirlKoi_tag(Tag:str = ""):
    for x in MirlKoi_tag.keys():
        if Tag in x.split():
            return MirlKoi_tag[x]
        else:
            continue
    else:
        return None

def MirlKoi(N:int = 1, Tag:str = "", R18:int = 0):
    Tag = Tag if Tag else "iw233"
    tag = tag_dict[Tag]
    msg = ""
    if 1 <= N <= 10:
        msg += f"Bot_NICKNAME为你准备了{N}张{tag}。"
    elif N > 10:
        N = 1
        msg += f"Bot_NICKNAME被禁止单次发送超过10张色图...但是，Bot_NICKNAME为你准备了一张{tag}。"
    else:
        N = 1
        msg += f"Bot_NICKNAME接收到了奇怪的数量参数，不过Bot_NICKNAME送你一张{tag}。"

    msg += f"\n来源：{tag}"

    if len(MirlKoi_list[Tag]) < N:
        logger.info(f"正在从 MirlKoi 获取图片，来源：{Tag}")
        resp = httpx.get(f"https://dev.iw233.cn/api.php?sort={Tag}&type=json&num=100")
        if resp.status_code == 200:
            resp = resp.text
            resp = ''.join(x for x in resp if x.isprintable())
            MirlKoi_list[Tag] += json.loads(resp)["pic"]
        else:
            msg += f"\n呜......连接出错了..."
            N = 0
    else:
        logger.info(f"正在从 本地MirlKoi队列 获取图片，来源：{Tag}")

    if N == 0:
        image_list = None
    else:
        image_list = []
        for i in range(N):
            image_list.append(MirlKoi_list[Tag][0])
            MirlKoi_list[Tag].pop(0)

    return msg, image_list