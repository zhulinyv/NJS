import os
import json
from nonebot.adapters.onebot.v11 import GroupMessageEvent

DATA_PATH: str = "data/summon/"

"""启动时初始化文件操作"""
if os.path.exists(DATA_PATH + "userinfo.json"):
    with open(DATA_PATH + "userinfo.json", "r", encoding="utf-8") as f:
        userdata = json.load(f)     # 读取用户数据
else:
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)  # 不存在文件夹就创建文件夹
    userdata = {"send_model": 1}
    with open(DATA_PATH + "userinfo.json", "w", encoding="utf-8") as f:
        json.dump(userdata, f, indent=4, ensure_ascii=False)
# json结构如下
# {
#     "group_id": {
#         "name": "qq_id"
#     },
#     "send_model": 1
# }


def write_json() -> None:
    """保存json"""
    with open(DATA_PATH + "userinfo.json", "w", encoding="utf-8") as f:
        json.dump(userdata, f, indent=4, ensure_ascii=False)


async def get_at(event: GroupMessageEvent) -> int:
    """获取被艾特用户 ID"""
    msg = event.get_message()
    for msg_seg in msg:
        if msg_seg.type == "at":
            return -1 if msg_seg.data["qq"] == "all" else int(msg_seg.data["qq"])
    return -1
