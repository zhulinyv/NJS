import os
import json
import nonebot
from nonebot.adapters.onebot.v11 import GroupMessageEvent

if os.path.exists("data/dog/groupdata.json"):  # 读取用户数据
    with open("data/dog/groupdata.json", "r", encoding="utf-8") as f:
        groupdata = json.load(f)
else:   # 不存在则创建
    if not os.path.exists("data/dog"):
        os.makedirs("data/dog")  # 创建文件夹
    groupdata = {}

async def check_group_allow(gid: str) -> bool:
    #检查群是否允许
    if gid not in groupdata:
        groupdata[gid] = {"allow": True}# 写入默认值为true
    return groupdata[gid]["allow"]

def write_group_data() -> None:
    #写入群配置
    with open("data/dog/groupdata.json", "w", encoding="utf-8") as f:
        json.dump(groupdata, f, indent=4)


try:
    dog_cd = nonebot.get_driver().config.dog_cd       # 从配置文件中读取cd_time
except:
    dog_cd = 20      		# cd默认值

try:
    laugh_cd = nonebot.get_driver().config.laugh_cd       # 从配置文件中读取cd_time
except:
    laugh_cd = 20      		# cd默认值

try:
    hitokoto_cd = nonebot.get_driver().config.hitokoto_cd       # 从配置文件中读取cd_time
except:
    hitokoto_cd = 20      		# cd默认值

try:
    wenan_cd = nonebot.get_driver().config.wenan_cd       # 从配置文件中读取cd_time
except:
    wenan_cd = 20      		# cd默认值
'''
try:
    music_cd = nonebot.get_driver().config.music_cd       # 从配置文件中读取cd_time
except:
    music_cd = 0      		# cd默认值
'''

dog_CD_dir = {}  # 记录舔狗日记cd的字典
laugh_CD_dir = {}  # 记录讲个笑话cd的字典
hitokoto_CD_dir = {}  # 记录一言cd的字典
wenan_CD_dir = {}  # 记录文案cd的字典
#music_CD_dir = {}  # 记录点歌cd的字典
notAllow = "群内还未开启文案功能, 请管理员或群主发送\"开启文案\", \"关闭文案\"以开启/关闭该功能"


__usage__ = """指令1：/舔狗日记
指令2：/讲个笑话
指令3：/一言"""
