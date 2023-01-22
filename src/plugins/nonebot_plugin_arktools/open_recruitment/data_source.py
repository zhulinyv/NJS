import os
from .config import Config
from nonebot import get_driver
from nonebot import logger
from dataclasses import dataclass
from itertools import permutations

import json
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models
from pathlib import Path
from PIL import Image, ImageFont
from PIL.ImageDraw import Draw, ImageDraw
import math

recruit_config = Config.parse_obj(get_driver().config.dict())
SAVE_PATH = Path(recruit_config.recruitment_save_path)
FONT_PATH = Path(__file__).parent.parent / "_data" / "operator_info" / "font"


def process_word_tags(tags: list):
    """处理文字标签"""
    for idx, tag in enumerate(tags):
        if tag in {"高资", "高干", "高级"}:
            tags[idx] = "高级资深干员"
        elif tag in {"资深", "资干"}:
            tags[idx] = "资深干员"
        elif tag in {"机械", "支机"}:
            tags[idx] = "支援机械"
        elif tag in {"近战", "远程"}:
            tags[idx] = f"{tags[idx]}位"
        elif tag in {"回费", "费回", "回复", "恢复"}:
            tags[idx] = "费用回复"
        elif tags[idx] in {"快活", "复活", "快速"}:
            tags[idx] = "快速复活"
        elif "术士" in tag:
            tags[idx] = tag.replace("术士", "术师")
        elif tag in {"近卫", "狙击", "重装", "医疗", "辅助", "术师", "特种", "先锋", "男性", "女性"}:
            tags[idx] = f"{tags[idx]}干员"
    return tags



def ocr(image_url: str) -> set:
    """调用腾讯云进行 OCR 识别公招标签"""
    with open(Path(__file__).parent.parent / "_data" / "operator_info" / "json" / "gacha_table.json", "r", encoding="utf-8") as f:
        TAGS = json.load(f)
    TAGS = {_["tagName"] for _ in TAGS["gachaTags"]}
    try:
        cred = credential.Credential(recruit_config.tencent_cloud_secret_id, recruit_config.tencent_cloud_secret_key)
        client = ocr_client.OcrClient(cred, "ap-beijing")
        req = models.GeneralAccurateOCRRequest()
        params = {"ImageUrl": image_url}
        req.from_json_string(json.dumps(params))
        resp = client.GeneralAccurateOCR(req)
        data = json.loads(resp.to_json_string())

    except TencentCloudSDKException as e:
        logger.error(f"腾讯云识别公招标签出错: {e}")
        return set()

    else:
        filtered_char: set = {f"{i}" for i in range(10)}.union({chr(i) for i in range(65, 90)})  # 过滤字母和数字
        pre_tags = {word["DetectedText"] for word in data["TextDetections"] if all(c not in word["DetectedText"] for c in filtered_char)}

        return {tag for tag in pre_tags if tag in TAGS}


@dataclass
class Operator:
    code: str
    name: str
    prof: str
    pos: str
    tags: list
    rarity: int
    sex: bool = 0


def load_operator_data() -> dict:
    """读取干员基本信息：职业、位置、性别、标签、稀有度"""
    operators = {}
    with open(Path(__file__).parent.parent / "_data" / "operator_info" / "json" / "character_table.json", "r", encoding="utf-8") as f:
        operator_basic_info: dict = json.load(f)
    with open(Path(__file__).parent.parent / "_data" / "operator_info" / "json" / "handbook_info_table.json", "r", encoding="utf-8") as f:
        operator_data_info: dict = json.load(f)
    with open(Path(__file__).parent.parent / "_data" / "operator_info" / "json" / "gacha_table.json", "r", encoding="utf-8") as f:
        operator_obtainable: dict = json.load(f)
    for code, info in operator_basic_info.items():
        text = operator_obtainable["recruitDetail"]
        text = text.replace("\\n", "\n").replace("<@rc.eml>", "\n").replace("</>", "\n").split("\n")

        text = [_ for _ in text if _ and "<" not in _ and "--" not in _ and "★" not in _ and _ != " / "][1:]

        text = [" ".join(_.split(" / ")) for _ in text]
        text = " ".join(_.strip() for _ in text).split()
        if info["name"] not in text:
            continue
        if not info["itemObtainApproach"]:
            continue
        if info["isSpChar"]:
            continue
        operator = Operator(code=code, name=info["name"], prof=info["profession"], rarity=info["rarity"], tags=info["tagList"], pos=info["position"])

        if operator.prof == "PIONEER":
            operator.tags.append("先锋干员")
        elif operator.prof == "WARRIOR":
            operator.tags.append("近卫干员")
        elif operator.prof == "SNIPER":
            operator.tags.append("狙击干员")
        elif operator.prof == "MEDIC":
            operator.tags.append("医疗干员")
        elif operator.prof == "TANK":
            operator.tags.append("重装干员")
        elif operator.prof == "SUPPORT":
            operator.tags.append("辅助干员")
        elif operator.prof == "CASTER":
            operator.tags.append("术师干员")
        else:
            operator.tags.append("特种干员")
        if operator.pos == "MELEE":
            operator.tags.append("近战位")
        else:
            operator.tags.append("远程位")
        if operator.rarity == 5:
            operator.tags.append("高级资深干员")
        elif operator.rarity == 4:
            operator.tags.append("资深干员")
        elif operator.rarity == 0:
            operator.tags.append("支援机械")
        operators[code] = operator
    for code, info in operator_data_info["handbookDict"].items():
        if code not in operators:
            continue
        if "男" in info["storyTextAudio"][0]["stories"][0]["storyText"]:
            operators[code].sex = 1
    return operators


def get_rare_operators(tags: set) -> list:
    """获取干员"""
    operators = load_operator_data()
    combinations = build_combinations(tags)
    result = []
    for comb in combinations:
        comb = sorted(list(comb))
        mapping = []
        for code, data in operators.items():
            if len(comb) <= len(data.tags) and set(comb).issubset(data.tags):
                if "高级资深干员" not in comb and data.rarity == 5:
                    continue
                if (data.name, data.code, data.rarity) in mapping:
                    continue
                mapping.append((data.name, data.code, data.rarity))
        mapping = sorted(mapping)
        if mapping and {"tags": comb, "operators": mapping} not in result:
            result.append({"tags": comb, "operators": mapping})

    result_ = []
    for r in result:
        flag = all(op[2] not in {1, 2} for op in r["operators"])
        if flag:
            result_.append(r)
    return result_


def build_combinations(tags: set) -> set:
    result = []
    for i in range(1, 6):
        result += list(permutations(tags, i))
    return set(result)


def text_border(text: str, draw: ImageDraw, x: int, y: int, font: ImageFont, shadow_colour: tuple, fill_colour: tuple, anchor: str = "la"):
    """文字加边框"""
    draw.text((x - 1, y), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x + 1, y), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x, y - 1), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x, y + 1), text=text, anchor=anchor, font=font, fill=shadow_colour)

    draw.text((x - 1, y - 1), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x + 1, y - 1), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x - 1, y + 1), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x + 1, y + 1), text=text, anchor=anchor, font=font, fill=shadow_colour)

    draw.text((x, y), text=text, anchor=anchor, font=font, fill=fill_colour)


def build_image(result_list: list) -> Image:
    font = ImageFont.truetype(str(FONT_PATH / "Arknights-zh.otf"), 24)
    if not result_list:
        return None

    # 先构造每一个tag组
    result_imgs = []
    for result in result_list:
        """这是一个tag组的结果"""
        rows = math.ceil(len(result["operators"]) / 6)
        result_bg = Image.new("RGBA", (920, 152 * rows), (0, 0, 0, 0))
        """152x152的TAG, 128x(128+24)的头图"""

        tag_bg = Image.new("RGBA", (152, 152), (50, 50, 50, 0))
        for idx, tag in enumerate(result["tags"]):
            """一个tag组里的每个tag"""
            text_border(text=tag, draw=Draw(tag_bg), x=76, y=(15 + 30 * idx), anchor="mm", font=font, fill_colour=(255, 255, 255, 255), shadow_colour=(0, 0, 0, 255))
        result_bg.paste(tag_bg, box=(0, 0), mask=tag_bg.split()[3])

        op_bg = Image.new("RGBA", (920, 912), (50, 50, 50, 0))
        font_op = ImageFont.truetype(str(FONT_PATH / "Arknights-zh.otf"), 20)
        for idx, op_tuple in enumerate(result["operators"]):
            """一个tag组里的所有干员信息"""
            avatar = Image.open(Path(__file__).parent.parent / "_data" / "operator_info" / "image" / "avatar" / f"{op_tuple[1]}.png").convert("RGBA").resize((128, 128))  # 头像
            # 贴个对应颜色的光
            avatar_bg = None
            if op_tuple[2] == 5:  # 六星
                avatar_bg = Image.new("RGBA", (128, 128), (255, 127, 39, 250))
                avatar_bg.paste(avatar, mask=avatar.split()[3])
            elif op_tuple[2] == 4:  # 五星
                avatar_bg = Image.new("RGBA", (128, 128), (255, 201, 14, 250))
                avatar_bg.paste(avatar, mask=avatar.split()[3])
            elif op_tuple[2] == 3:  # 四星
                avatar_bg = Image.new("RGBA", (128, 128), (216, 179, 216, 250))
                avatar_bg.paste(avatar, mask=avatar.split()[3])
            elif op_tuple[2] == 0:  # 一星
                avatar_bg = Image.new("RGBA", (128, 128), (255, 255, 255, 250))
                avatar_bg.paste(avatar, mask=avatar.split()[3])

            if avatar_bg:
                op_bg.paste(avatar_bg, box=(128 * (idx - 6 * (idx // 6)), 0 + 152 * (idx // 6)),  mask=avatar_bg.split()[3])  # 粘头像，每六个换行
            text_border(op_tuple[0], Draw(op_bg), x=(64 + 128 * (idx - 6 * (idx // 6))), y=(128 + 12 + 152 * (idx // 6)), anchor="mm", font=font_op, fill_colour=(255, 255, 255, 255), shadow_colour=(0, 0, 0, 255))
        result_bg.paste(op_bg, box=(152, 0), mask=op_bg.split()[3])
        result_imgs.append((result_bg, rows))  # 记录每个结果及行数，方便绘制总图

    # 分组，每列十行
    result_combs: list = process_result_imgs(result_imgs)
    columns = len(result_combs)  # 总列数

    """绘制总图，最多十行 -> 152*10 + 24*2"""
    main_background = Image.new("RGBA", size=(10 * 2 + (920 + 24) * columns, 10 * 2 + 152 * 10), color=(50, 50, 50, 200))
    width = main_background.size[0]
    height = main_background.size[1]

    Draw(main_background).rectangle(xy=(0, 0, width, height), outline=(200, 200, 200), width=10)

    H = 0
    for idx_column, comb in enumerate(result_combs):  # 每列
        H = 0
        if idx_column != 0:
            Draw(main_background).line(xy=(10 + (920 + 24) * idx_column, 0, 10 + (920 + 24) * idx_column, height), width=4, fill=(200, 200, 200))
        for idx_row, img_tuple in enumerate(comb):  # 每行
            if idx_row != 0:
                Draw(main_background).line(xy=(10 + (920 + 24) * idx_column, 10 + H, 944 + 10 + (920 + 24) * idx_column, 10 + H), width=4, fill=(200, 200, 200))
            main_background.paste(im=img_tuple[0], box=(10 + (920 + 24) * idx_column, 10 + H), mask=img_tuple[0].split()[3])
            H += img_tuple[0].size[1]

    if len(result_combs) == 1 and 0 < H < height-10:  # 只有一列，可能要裁图片
        main_background = main_background.crop(box=(0, 0, width, H+16))
        Draw(main_background).line(xy=(0, H+10, width, H+10), width=10, fill=(200, 200, 200))

    file = SAVE_PATH / "temp.png"
    None if os.path.exists(SAVE_PATH) else os.makedirs(SAVE_PATH)
    main_background.save(file)
    return file


def process_result_imgs(result_imgs: list):
    # 先从大到小排列
    # 然后一一配组
    result_counts = sorted(result_imgs, key=lambda tup: tup[1], reverse=True)
    already_in = []
    comb = []
    flag = False
    for idx1, count1 in enumerate(result_counts):
        if idx1 in already_in:
            continue
        tmp_count = [count1[1]]
        tmp_idx = [idx1]
        for idx2, count2 in enumerate(result_counts[idx1+1:]):
            flag = False
            if idx2+idx1+1 in already_in:
                continue
            if count1[1] + count2[1] > 10:
                continue
            elif count1[1] + count2[1] == 10:
                already_in += [idx1, idx2+idx1+1]
                comb.append([idx1, idx2+idx1+1])
                break
            if sum(tmp_count) + count2[1] > 10:
                continue
            elif sum(tmp_count) + count2[1] == 10:
                already_in += [idx1, idx2+idx1+1]
                comb.append(tmp_idx + [idx2+idx1+1])
                break
            tmp_idx.append(idx2+idx1+1)
            already_in += [idx1, idx2+idx1+1]
            tmp_count.append(count2[1])
            flag = True
        if flag:
            comb.append(tmp_idx)

    return [[result_counts[idx] for idx in c] for c in comb]
