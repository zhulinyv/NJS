from pathlib import Path
import os
import random
data_dir = "./data/sb_CD"
import nonebot
from typing import Union
from nonebot.adapters.onebot.v11 import Message
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from httpx import AsyncClient
import re


# NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]      # bot的nickname,可以换成你自己的
# MASTER: str = list(nonebot.get_driver().config.superusers)[0]      # bot的主人名称,也可以换成你自己的
NICKNAME: str = "脑积水"
MASTER: str = "(๑•小丫头片子•๑)"


# 载入词库(这个词库有点涩)
AnimeThesaurus = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "resource/json")) / "data.json", "r", encoding="utf8"))

# read_json的工具函数
def read_json() -> dict:
    try:
        with open(data_dir + "usercd.json", "r") as f_in:
            data = json.load(f_in)
            f_in.close()
            return data
    except FileNotFoundError:
        try:
            import os

            os.makedirs(data_dir)
        except FileExistsError:
            pass
        with open(data_dir + "usercd.json", mode="w") as f_out:
            json.dump({}, f_out)

        return {}

# write_json的工具函数
def write_json(qid: str, time: int, mid: int, data: dict):
    data[qid] = [time, mid]
    with open(data_dir + "usercd.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()


# remove_json的工具函数
def remove_json(qid: str):
    with open(data_dir + "usercd.json", "r") as f_in:
        data = json.load(f_in)
        f_in.close()
    data.pop(qid)
    with open(data_dir + "usercd.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()


attack_sendmessage = [
    "不理你啦，baka",
    "我给你一拳",
    "不理你啦！バーカー",
    "baka！不理你了！",
    "你在说什么呀，咱就不理你了！",
]

# 获取resource/audio下面的全部文件
aac_file_path = os.path.join(os.path.dirname(__file__), "resource/audio")
aac_file_list = os.listdir(aac_file_path)

# hello之类的回复
hello__reply = [
    "你好！",
    "哦豁？！",
    "你好！Ov<",
    f"库库库，呼唤{NICKNAME}做什么呢",
    "我在呢！",
    "呼呼，叫俺干嘛",
]


# 戳一戳消息
poke__reply = [
    "lsp你再戳？",
    "连个可爱美少女都要戳的肥宅真恶心啊。",
    "你再戳！",
    "？再戳试试？",
    "别戳了别戳了再戳就坏了555",
    "我爪巴爪巴，球球别再戳了",
    f"请不要戳{NICKNAME} >_<",
    "放手啦，不给戳QAQ",
    f"喂(#`O′) 戳{NICKNAME}干嘛！",
    "戳坏了，赔钱！",
    "戳坏了",
    "嗯……不可以……啦……不要乱戳",
    "那...那里...那里不能戳...绝对...",
    "(。´・ω・)ん?",
    "有事恁叫我，别天天一个劲戳戳戳！",
    "再戳一下试试？",
    "正在关闭对您的所有服务...关闭成功",
    "啊呜，太舒服刚刚竟然睡着了。什么事？",
    "正在定位您的真实地址...定位成功。轰炸机已起飞",
]

# 从字典里返还消息, 抄(借鉴)的zhenxun-bot
async def get_chat_result(text: str, nickname: str) -> str:
    if len(text) < 7:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key]).replace("你", nickname)

# 从qinyunke_api拿到消息
async def qinyun_reply(url):
    async with AsyncClient() as client:
        response = await client.get(url)
        # 这个api好像问道主人或者他叫什么名字会返回私活,这里replace掉部分
        res = response.json()["content"].replace("林欣", MASTER).replace("{br}", "\n").replace("贾彦娟", MASTER).replace("周超辉", MASTER).replace("鑫总", MASTER).replace("张鑫", MASTER).replace("菲菲", NICKNAME).replace("dn", MASTER).replace("1938877131", "2749903559").replace("小燕", NICKNAME)
        res = re.sub(u"\\{.*?\\}", "", res)
        if "taobao" in res:
            res = NICKNAME + "暂时听不懂主人说的话呢"
        return res

# 从小爱同学api拿到消息, 这个api私货比较少
async def xiaoice_reply(url):
    async with AsyncClient() as client:
        res = (await client.get(url)).text
        res = res[res.find("{"):res.rfind("}")+1]
        res = json.loads(res)
        res = res["text"].replace("小爱", NICKNAME)
        return res
