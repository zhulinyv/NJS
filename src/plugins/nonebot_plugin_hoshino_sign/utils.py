import os
import ujson as json
from PIL import Image
from pathlib import Path
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot

from .config import Config, sign_config


# 是否启动时直接将所有图片加载到内存中以提高查看仓库的速度(增加约几M内存消耗)
PRELOAD = True
# 查看仓库时每行显示的卡片个数
COL_NUM = 11
__BASE = os.path.split(os.path.realpath(__file__))
FRAME_DIR_PATH = os.path.join(__BASE[0], 'image')
GOODWILL_PATH = "./data/nonebot_plugin_hoshino_sign/json/"
STAMP_PATH = Path(sign_config.stamp_path)

card_file_names_all = []

if not os.path.exists(GOODWILL_PATH):
    # 不存在就创建文件
    os.makedirs(GOODWILL_PATH)
    userdata = {}
    with open(GOODWILL_PATH + "goodwill.json", "w", encoding="utf-8") as f:
        json.dump(userdata, f, indent=4, ensure_ascii=False)

# 资源预检
image_cache = {}
image_list = os.listdir(STAMP_PATH)
for image in image_list:
    # 图像缓存
    if PRELOAD:
        image_path = os.path.join(STAMP_PATH, image)
        img = Image.open(image_path)
        image_cache[image] = img.convert('RGBA') if img.mode != 'RGBA' else img
    card_file_names_all.append(image)
len_card = len(card_file_names_all)

def normalize_digit_format(n):
    return f'0{n}' if n < 10 else f'{n}'

def get_pic(pic_path, grey):
    if PRELOAD:
        sign_image = image_cache[pic_path]
    else:
        sign_image = Image.open(os.path.join(__BASE, 'stamp', pic_path))
    sign_image = sign_image.resize((80, 80), Image.LANCZOS)
    if grey:
        sign_image = sign_image.convert('L')
    return sign_image

async def get_at(event: GroupMessageEvent) -> int:
    """获取被艾特用户 ID"""
    msg = event.get_message()
    for msg_seg in msg:
        if msg_seg.type == "at":
            return -1 if msg_seg.data["qq"] == "all" else int(msg_seg.data["qq"])
    return -1

async def get_user_card(bot: Bot, group_id, qid):
    # 返还用户nickname
    user_info: dict = await bot.get_group_member_info(group_id=group_id, user_id=qid)
    user_card = user_info["card"]
    if not user_card:
        user_card = user_info["nickname"]
    return user_card


login_presents = [
    '扫荡券×5', '卢币×1000', '普通EXP药水×5', '宝石×50', '玛那×3000',
    '扫荡券×10', '卢币×1500', '普通EXP药水×15', '宝石×80', '白金转蛋券×1',
    '扫荡券×15', '卢币×2000', '上级精炼石×3', '宝石×100', '白金转蛋券×1',
]

todo_list = [
    '找伊绪老师上课',
    '给宫子买布丁',
    '和真琴寻找伤害优衣的人',
    '找镜哥探讨女装',
    '跟吉塔一起登上骑空艇',
    '和霞一起调查伤害优衣的人',
    '和佩可小姐一起吃午饭',
    '找小小甜心玩过家家',
    '帮碧寻找新朋友',
    '去真步真步王国',
    '找镜华补习数学',
    '陪胡桃排练话剧',
    '和初音一起午睡',
    '成为露娜的朋友',
    '帮铃莓打扫咲恋育幼院',
    '和静流小姐一起做巧克力',
    '去伊丽莎白农场给栞小姐送书',
    '观看慈乐之音的演出',
    '解救挂树的队友',
    '来一发十连',
    '井一发当期的限定池',
    '给妈妈买一束康乃馨',
    '购买黄金保值',
    '竞技场背刺',
    '给别的女人打钱',
    '氪一单',
    '努力工作，尽早报答妈妈的养育之恩',
    '成为魔法少女',
    '搓一把日麻'
]
