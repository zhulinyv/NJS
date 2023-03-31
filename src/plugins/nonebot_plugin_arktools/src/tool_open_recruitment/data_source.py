from pathlib import Path

import httpx
from aiofiles import open as aopen
import json
from typing import Set, List, Tuple, Dict, Any, Union
from PIL import Image, ImageFont
from PIL.ImageDraw import Draw
from itertools import permutations
import math
from io import BytesIO

from nonebot import get_driver, logger

from ..core.models_v3 import Character
from ..configs import BaiduOCRConfig, PathConfig
from ..utils import text_border, get_recruitment_available

bconfig = BaiduOCRConfig.parse_obj(get_driver().config.dict())
pcfg = PathConfig.parse_obj(get_driver().config.dict())
font_path = Path(pcfg.arknights_font_path).absolute()
gamedata_path = Path(pcfg.arknights_gamedata_path).absolute()


async def baidu_ocr(image_url: str, client: httpx.AsyncClient) -> Set[str]:
    """百度ocr"""
    access_token = await get_baidu_ocr_access_token(client)

    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"
    client.headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = {"url": image_url}
    response = await client.post(url, data=data)

    try:
        all_words = {_["words"] for _ in response.json()["words_result"]}
    except KeyError as e:
        logger.error("百度ocr识别失败:")
        logger.error(f"{response.json()}")
        return None

    async with aopen(gamedata_path / "excel" / "gacha_table.json", "r", encoding="utf-8") as fp:
        tags = {_["tagName"] for _ in json.loads(await fp.read())["gachaTags"]}

    return {_ for _ in all_words if _ in tags}


async def get_baidu_ocr_access_token(client: httpx.AsyncClient) -> str:
    """百度ocr获取token"""
    url = (
        f"https://aip.baidubce.com/oauth/2.0/token?"
        f"grant_type=client_credentials&"
        f"client_id={bconfig.arknights_baidu_api_key}&"
        f"client_secret={bconfig.arknights_baidu_secret_key}")
    response = await client.post(url=url)
    data = response.json()
    try:
        return data["access_token"]
    except KeyError as e:
        logger.warning("百度ocr获取token失败！")
        logger.warning(f"{data}")


def process_word_tags(tags: list):
    """处理文字简化标签"""
    for idx, tag in enumerate(tags):
        if tag in {"高资", "高姿", "高级"}:
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
            tag = tag.replace("术士", "术师")

        if tag in {"近卫", "狙击", "重装", "医疗", "辅助", "术师", "特种", "先锋", "男性", "女性"}:
            tags[idx] = f"{tags[idx]}干员"
    return tags


class BuildRecruitmentCard:
    """绘图"""
    def __init__(self, result_groups: List[Dict[str, Any]]):
        self.result_groups = result_groups
        self.font_norm = ImageFont.truetype(str(font_path / "Arknights-zh.otf"), 24)
        self.font_small = ImageFont.truetype(str(font_path / "Arknights-zh.otf"), 20)

        self.result_images: List[Tuple[Image, int]] = []

    def build_group(self, result_group: Dict[str, Any]):
        """每一个组合绘制"""
        tags: List[str] = result_group["tags"]
        chts: List[Character] = result_group["chts"]

        rows = math.ceil(len(chts) / 6)  # 每行最多6头像
        result_bg = Image.new("RGBA", (920, 152 * rows), (0, 0, 0, 0))  # tag 块是 152x152, 头图块是 128x(128+24)

        tag_bg = Image.new("RGBA", (152, 152), (50, 50, 50, 0))  # tag 块
        for idx, tag in enumerate(tags):  # 一个tag组里的每个tag
            text_border(text=tag, draw=Draw(tag_bg), x=76, y=(15 + 30 * idx), anchor="mm", font=self.font_norm,
                        fill_colour=(255, 255, 255, 255), shadow_colour=(0, 0, 0, 255))
        result_bg.paste(tag_bg, box=(0, 0), mask=tag_bg.split()[3])

        cht_bg = Image.new("RGBA", (920, 912), (50, 50, 50, 0))
        for idx, cht in enumerate(chts):  # 给头像贴光
            cht.avatar = cht.avatar.resize((128, 128))
            if cht.rarity == 5:  # 六星
                light = Image.new("RGBA", (128, 128), (255, 127, 39, 250))
                light.paste(cht.avatar, mask=cht.avatar.split()[3])
                cht.avatar = light
            elif cht.rarity == 4:  # 五星
                light = Image.new("RGBA", (128, 128), (255, 201, 14, 250))
                light.paste(cht.avatar, mask=cht.avatar.split()[3])
                cht.avatar = light
            elif cht.rarity == 3:  # 四星
                light = Image.new("RGBA", (128, 128), (216, 179, 216, 250))
                light.paste(cht.avatar, mask=cht.avatar.split()[3])
                cht.avatar = light
            elif cht.rarity == 0:  # 一星
                light = Image.new("RGBA", (128, 128), (255, 255, 255, 250))
                light.paste(cht.avatar, mask=cht.avatar.split()[3])
                cht.avatar = light

            cht_bg.paste(cht.avatar, box=(128 * (idx - 6 * (idx // 6)), 0 + 152 * (idx // 6)),
                         mask=cht.avatar.split()[3])  # 粘头像，每六个换行
            text_border(cht.name, Draw(cht_bg), x=(64 + 128 * (idx - 6 * (idx // 6))), y=(128 + 12 + 152 * (idx // 6)),
                        anchor="mm", font=self.font_small, fill_colour=(255, 255, 255, 255),
                        shadow_colour=(0, 0, 0, 255))
        result_bg.paste(cht_bg, box=(152, 0), mask=cht_bg.split()[3])
        return result_bg, rows  # 记录每个结果及行数，方便绘制总图

    def build_main(self):
        """绘制总图"""
        self.result_images = [self.build_group(group) for group in self.result_groups]
        result_groups = self.sort_result_groups()
        columns = len(result_groups)  # 总列数

        main_background = Image.new("RGBA", size=(10 * 2 + (920 + 24) * columns, 10 * 2 + 152 * 10),
                                    color=(50, 50, 50, 200))
        width = main_background.size[0]
        height = main_background.size[1]

        Draw(main_background).rectangle(xy=(0, 0, width, height), outline=(200, 200, 200), width=10)

        H = 0
        for idx_column, comb in enumerate(result_groups):  # 每列
            H = 0
            if idx_column != 0:
                Draw(main_background).line(xy=(10 + (920 + 24) * idx_column, 0, 10 + (920 + 24) * idx_column, height),
                                           width=4, fill=(200, 200, 200))
            for idx_row, img_tuple in enumerate(comb):  # 每行
                if idx_row != 0:
                    Draw(main_background).line(
                        xy=(10 + (920 + 24) * idx_column, 10 + H, 944 + 10 + (920 + 24) * idx_column, 10 + H), width=4,
                        fill=(200, 200, 200))
                main_background.paste(im=img_tuple[0], box=(10 + (920 + 24) * idx_column, 10 + H),
                                      mask=img_tuple[0].split()[3])
                H += img_tuple[0].size[1]

        if columns == 1 and 0 < H < height - 10:  # 只有一列，可能要裁图片
            main_background = main_background.crop(box=(0, 0, width, H + 16))
            Draw(main_background).line(xy=(0, H + 10, width, H + 10), width=10, fill=(200, 200, 200))

        output = BytesIO()
        main_background.save(output, format="png")
        return output

    def sort_result_groups(self) -> List:
        """
        分组, 每一大列行数最多 10 行
        """
        result_counts = sorted(self.result_images, key=lambda tup: tup[1], reverse=True)  # 按照行数排序

        already_in = []
        comb = []
        flag = False
        for idx1, result1 in enumerate(result_counts):
            result1: Tuple[Image, int]  # 分组图片，行数
            if idx1 in already_in:  # 单个分组的行数
                continue

            tmp_row = [result1[1]]  # 方便判断
            tmp_idx = [idx1]

            if not result_counts[idx1 + 1:]:
                flag = True
            for idx2, result2 in enumerate(result_counts[idx1 + 1:]):
                flag = False
                if idx2 + idx1 + 1 in already_in:  # 当列所有分组的总行数
                    continue
                if result1[1] + result2[1] > 10:  # 加起来超过10行
                    continue
                elif result1[1] + result2[1] == 10:  # 加起来刚好等于 10 行
                    already_in += [idx1, idx2 + idx1 + 1]
                    comb.append([idx1, idx2 + idx1 + 1])
                    break

                if sum(tmp_row) + result2[1] > 10:  # 加起来超过10行
                    continue
                elif sum(tmp_row) + result2[1] == 10:  # 加起来刚好等于 10 行
                    already_in += [idx1, idx2 + idx1 + 1]
                    comb.append(tmp_idx + [idx2 + idx1 + 1])
                    break

                tmp_idx.append(idx2 + idx1 + 1)
                already_in += [idx1, idx2 + idx1 + 1]
                tmp_row.append(result2[1])
                flag = True
            if flag:
                comb.append(tmp_idx)

        return [
            [
                result_counts[idx]
                for idx in c
            ] for c in comb
        ]

    @staticmethod
    def build_combinations(tags: set) -> set:
        """构造所有可能的5tag集合"""
        result = []
        for i in range(1, 6):
            result += list(permutations(tags, i))
        return set(result)

    @staticmethod
    async def build_target_characters(tags: set) -> List[Dict[str, Union[str, List[Character]]]]:
        """tag-干员组合"""
        chts = [(await Character().init(_)) for _ in await get_recruitment_available()]  # 所有可公招的干员
        combs = BuildRecruitmentCard.build_combinations(tags)  # 所有可能的tag组合
        cht_tags = {  # 这一条提出来，省了1k倍速度
            _.name: await _.get_tags_for_open_recruitment()
            for _ in chts
        }

        result = []
        for comb in combs:
            comb = sorted(list(comb))
            mapping = []
            for cht in chts:
                if cht.rarity == 5 and "高级资深干员" not in comb:
                    continue
                if len(comb) <= len(cht_tags[cht.name]) \
                        and set(comb).issubset(cht_tags[cht.name]) \
                        and cht.name not in mapping:
                    mapping.append(cht)
            if mapping and {"tags": comb, "chts": mapping} not in result:
                result.append({"tags": comb, "chts": mapping})

        result_ = []
        for r in result:
            flag = all(cht.rarity not in {1, 2} for cht in r["chts"])
            if flag:
                result_.append(r)
        return result_


__all__ = [
    "BuildRecruitmentCard",
    "process_word_tags",
    "baidu_ocr"
]
