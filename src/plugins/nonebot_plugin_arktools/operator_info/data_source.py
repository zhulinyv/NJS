import contextlib
import os
from typing import Union

from PIL import Image, ImageFont
from PIL.ImageDraw import Draw, ImageDraw
from nonebot import get_driver
import json
from pathlib import Path
from .config import Config
from .._exceptions import OperatorNotExistException


operator_config = Config.parse_obj(get_driver().config.dict())
TEST_CHARACTER_NAME = "艾雅法拉"
JSON_PATH = Path(__file__).parent.parent / "_data" / "operator_info" / "json"
IMAGE_PATH = Path(__file__).parent.parent / "_data" / "operator_info" / "image"
FONT_PATH = Path(__file__).parent.parent / "_data" / "operator_info" / "font"
SAVE_PATH = Path(operator_config.operator_save_path).absolute()

class OperatorInfo:
    """小类，用来获取干员绘图必须的信息"""
    def __init__(self, name: str):
        self.operator_table = {}
        self.operator_result_info: dict = {}
        self.init_data: dict = {}

        self.init_info(name)

    def init_info(self, name: str):
        self._get_operator_basic_info(name)
        self._get_operator_all_skills_materials()
        self._get_operator_skills_materials()
        self._get_operator_evolve_materials()
        self._get_operator_equip_materials()
        return self.operator_result_info

    def _get_operator_basic_info(self, name: str):
        """找到干员"""
        name = name or TEST_CHARACTER_NAME
        if not self.operator_table:
            with open(JSON_PATH / "character_table.json", "r", encoding="utf-8") as f:
                self.operator_table: dict = json.load(f)

        for code, data in self.operator_table.items():
            if data["name"] == name:
                self.operator_result_info["operator_code"] = code
                self.operator_result_info["rarity"] = data["rarity"]
                self.init_data = data
                return
        raise OperatorNotExistException(details=name)  # 干员不存在

    def _get_operator_all_skills_materials(self):
        """获取干员技能1-7材料"""
        all_skills: list = self.init_data["allSkillLvlup"]  # 技能(1-7升级)
        all_skills_materials: dict = {}
        for all_skills_lvl, skill in enumerate(all_skills, start=1):
            cost: list = skill["lvlUpCost"]
            materials: dict = {material["id"]: material["count"] for material in cost}

            all_skills_materials[all_skills_lvl] = materials

        self.operator_result_info["all_skills_materials"] = all_skills_materials

    def _get_operator_skills_materials(self):
        """获取干员技能专精材料"""
        skills: list = self.init_data["skills"]  # 技能(专精升级)

        skills_materials: dict = {}  # 技能代码名 - 专精需要材料与数量
        for skill in skills:
            materials_list: list = []
            cost_condition: list = skill["levelUpCostCond"]
            if not cost_condition:
                continue
            for condition in cost_condition:
                cost: list = condition["levelUpCost"]
                materials: dict = {material["id"]: material["count"] for material in cost}
                materials_list.append(materials)
            skills_materials[skill["skillId"]] = materials_list
        self.operator_result_info["skills_materials"] = skills_materials

    def _get_operator_evolve_materials(self):
        """获取干员精英化材料"""
        phases: list = self.init_data["phases"]
        operator_rarity: int = self.init_data["rarity"]

        evolve_materials: dict = {}  # 精英化材料与数量
        evolve_lvl = 0
        for phase in phases:
            cost: list = phase["evolveCost"]
            if cost is None:
                continue
            materials: dict = {material["id"]: material["count"] for material in cost}

            evolve_lvl += 1
            evolve_materials[evolve_lvl] = materials

        if operator_rarity == 2:
            evolve_materials[1]["4001"] = 10000  # 龙门币

        elif operator_rarity == 3:
            evolve_materials[1]["4001"] = 15000  # 龙门币
            evolve_materials[2]["4001"] = 60000  # 龙门币
        elif operator_rarity == 4:
            evolve_materials[1]["4001"] = 20000  # 龙门币
            evolve_materials[2]["4001"] = 120000  # 龙门币
        elif operator_rarity == 5:
            evolve_materials[1]["4001"] = 30000  # 龙门币
            evolve_materials[2]["4001"] = 180000  # 龙门币
        self.operator_result_info["evolve_materials"] = evolve_materials

    def _get_operator_equip_materials(self):
        """获取干员模组升级材料"""
        equip_materials = {}
        with open(JSON_PATH / "uniequip_table.json", "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        code = self.operator_result_info["operator_code"]
        if code not in data["charEquip"]:
            self.operator_result_info["equip_materials"] = equip_materials
            return
        all_equips = [e for e in data["charEquip"][code] if "001" not in e]
        for e in all_equips:
            equip_materials[data["equipDict"][e]["typeIcon"].upper()] = [
                {c["id"]: c["count"] for c in cost}
                for _, cost in data["equipDict"][e]["itemCost"].items()
            ]
        self.operator_result_info["equip_materials"] = equip_materials

    @staticmethod
    def map_skill_code2name(skill_code: str) -> str:
        with open(JSON_PATH / "skill_table.json", "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        return data[skill_code]["levels"][0]["name"]

    @staticmethod
    def map_equip_code2name(skill_code: str) -> str:
        with open(JSON_PATH / "uniequip_table.json", "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        return data[skill_code]["levels"][0]["name"]

    @property
    def code(self):
        return self.operator_result_info["operator_code"]

    @property
    def rarity(self):
        return self.operator_result_info["rarity"]

    @property
    def info(self):
        return self.operator_result_info

    @property
    def all_skills(self) -> dict:
        return self.info["all_skills_materials"]

    @property
    def evolve(self) -> dict:
        return self.info["evolve_materials"]

    @property
    def skills(self) -> dict:
        return self.info["skills_materials"]

    @property
    def equips(self) -> dict:
        return self.info["equip_materials"]


class BuildOperatorImage:
    """绘图"""

    def __init__(self, operator: OperatorInfo, font_file_en: Union[str, Path] = str(FONT_PATH / "Arknights-en.ttf"), font_file_zh: Union[str, Path] = str(FONT_PATH / "Arknights-zh.otf")):
        self.operator = operator  # 干员
        self.font_file_en = font_file_en  # 字体文件
        self.font_file_zh = font_file_zh  # 字体文件

        self.is_all_skills: bool = operator.rarity > 1  # 是否有技能升级(1, 2星无)
        self.is_skills: bool = operator.rarity > 2  # 是否有技能专精(1, 2, 3星无)
        self.is_evolve_1: bool = self.is_all_skills  # 能否精一(1, 2星无)
        self.is_evolve_2: bool = self.is_skills  # 能否精二2(1, 2, 3星无)
        self.is_equip: bool = bool(self.operator.operator_result_info["equip_materials"])  # 有无模组

        self.background: Image  # 背景
        self.avatar: Image  # 干员头图

        self.all_skills: Image  # 1-7部分
        self.skills: Image  # 技能专精部分
        self.evolve: Image  # 精英化部分

        self.result: Image  # 整合部分

    def build_whole_image(self) -> Path:
        None if os.path.exists(SAVE_PATH) else os.makedirs(SAVE_PATH)
        file = SAVE_PATH / f"{self.operator.code}.png"

        all_skills_img = self._build_all_skills()  # 1-7
        skills_img = self._build_skills()  # 专精
        evolve_img = self._build_evolve()  # 精英化
        skin_img = self._build_skin()  # 立绘
        equip_img = self._build_equip()

        main_background = Image.new(mode="RGBA", size=(1904, 768), color=(100, 100, 100, 200))
        Draw(main_background).rectangle(xy=(0, 0, 1904, 768), outline=(10, 10, 10), width=4)  # 最外围边框

        if self.operator.rarity < 2:  # 只有精一立绘
            main_background.paste(im=skin_img, box=(-160, 0), mask=skin_img.split()[3])
        else:
            main_background.paste(im=skin_img, box=(-160, -140), mask=skin_img.split()[3])
        main_background.paste(im=all_skills_img, box=(800, 48), mask=all_skills_img.split()[3])  # 右上角
        main_background.paste(im=skills_img, box=(800, 312), mask=skills_img.split()[3])  # 右下角
        main_background.paste(im=evolve_img, box=(320, 48), mask=evolve_img.split()[3])  # 左上角
        main_background.paste(im=equip_img, box=(48, 312), mask=equip_img.split()[3])  # 左下角

        with contextlib.suppress(Exception):
            main_background.save(file)
        return file

    def _build_equip(self) -> Image:
        """模组升级部分"""
        font_en = ImageFont.truetype(self.font_file_en, 24)
        font_zh = ImageFont.truetype(self.font_file_zh, 24)
        main_background = Image.new(mode="RGBA", size=(704, 408), color=(235, 235, 235, 160))  # 底图
        if not self.is_equip:  # 没有模组
            font_zh = ImageFont.truetype(self.font_file_zh, 48)
            Draw(main_background).text(xy=(352, 216), anchor="ms", align="center", text="该干员无模组", font=font_zh, fill=(255, 255, 255, 255))
            return main_background

        img_head_shadow = Image.new(mode="RGBA", size=(704, 24), color=(175, 175, 175, 200))  # 顶部阴影
        main_background.paste(im=img_head_shadow, box=(0, 0), mask=img_head_shadow.split()[3])

        equips = self.operator.equips
        main_backgrounds = []
        for equip, data in equips.items():  # 对每个模组
            equip_main_backgrounds = Image.new(mode="RGBA", size=(352, 384), color=(235, 235, 235, 160))  # 每个模组的底图
            icon_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
            equip_main_backgrounds.paste(im=icon_shadow, box=(0, 0), mask=icon_shadow.split()[3])
            # equip_icon = self.get_equip_icon(equip).resize(size=(96, 96))  # TODO 模组图标
            # equip_main_backgrounds.paste(im=equip_icon, box=(0, 0))
            equip_name = equip  # 模组名
            draw = Draw(equip_main_backgrounds)
            self.text_border(text=equip_name, draw=draw, x=224, y=60, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))

            backgrounds = []
            for idx, level in enumerate(data):  # 对每层专精
                background = Image.new(mode="RGBA", size=(352, 96), color=(235, 235, 235, 160))  # 小底图
                text_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
                background.paste(im=text_shadow, box=(0, 0), mask=text_shadow.split()[3])

                level_icon = Image.open(IMAGE_PATH / "equip" / f"equip_lvl{idx + 1}.png", mode="r").convert("RGBA").resize(size=(96, 96))  # 专精图标
                background.paste(im=level_icon, box=(0, 0), mask=level_icon.split()[3])

                item_count = 0
                for mat, count in level.items():
                    icon = self.get_material_icon(mat).resize(size=(64, 64))  # 材料图标大小
                    if count >= 10000:
                        count = f"{count / 10000:.0f}w"
                        font = ImageFont.truetype(self.font_file_en, 14)
                        self.text_border(text=str(count), draw=Draw(icon), x=45, y=52, font=font, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))
                    else:
                        self.text_border(text=str(count), draw=Draw(icon), x=45, y=57, font=font_en, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))
                    background.paste(im=icon, box=(112 + item_count, 16), mask=icon.split()[3])
                    item_count += 80
                backgrounds.append(background)

            # 粘到大图上
            for idx, bg in enumerate(backgrounds):
                equip_main_backgrounds.paste(im=bg, box=(0, (idx + 1) * 96))
            main_backgrounds.append(equip_main_backgrounds)

        for idx, bg in enumerate(main_backgrounds):
            main_background.paste(im=bg, box=(idx * 352, 24))
        font_zh = ImageFont.truetype(self.font_file_zh, 16)
        # Draw(main_background).text(xy=(528, 20), anchor="ms", align="center", text="技 能 专 精", font=font_zh, fill=(255, 255, 255, 255))  # 最顶部的字
        self.text_border(text="模 组 升 级", draw=Draw(main_background), x=352, y=20, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 左侧文字

        main_draw =Draw(main_background)
        main_draw.line(xy=(0, 0, 702, 0), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 0, 0, 408), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(702, 0, 702, 408), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 406, 704, 406), width=4, fill=(50, 50, 50))

        main_draw.line(xy=(0, 24, 704, 24), width=2, fill=(50, 50, 50))

        main_draw.line(xy=(0, 120, 704, 120), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(0, 216, 704, 216), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(0, 312, 704, 312), width=2, fill=(50, 50, 50))

        main_draw.line(xy=(96, 24, 96, 408), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(352, 24, 352, 408), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(448, 24, 448, 408), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(704, 24, 704, 408), width=2, fill=(50, 50, 50))
        return main_background

    def _build_skin(self) -> Image:
        """立绘，优先用精二"""
        return Image.open(IMAGE_PATH / "skin" / self.get_operator_skin()).convert(mode="RGBA").resize((1176, 1176))

    def _build_all_skills(self) -> Image:
        """绘制 1-7 部分"""
        font_en = ImageFont.truetype(self.font_file_en, 24)
        main_background = Image.new(mode="RGBA", size=(1056, 216), color=(235, 235, 235, 160))  # 底图
        if not self.is_all_skills:  # 没有技能升级，如一星二星
            font_zh = ImageFont.truetype(self.font_file_zh, 48)
            Draw(main_background).text(xy=(528, 132), anchor="ms", align="center", text="该干员无技能升级", font=font_zh, fill=(255, 255, 255, 255))
            return main_background

        img_head_shadow = Image.new(mode="RGBA", size=(1056, 24), color=(175, 175, 175, 200))  # 顶部阴影
        main_background.paste(im=img_head_shadow, box=(0, 0), mask=img_head_shadow.split()[3])

        all_skills = self.operator.all_skills
        backgrounds = []
        for lvl, skill in all_skills.items():
            background = Image.new(mode="RGBA", size=(352, 96), color=(235, 235, 235, 160))  # 底图
            text_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
            background.paste(im=text_shadow, box=(0, 0), mask=text_shadow.split()[3])
            self.text_border(text=f"{lvl}~{lvl + 1}", draw=Draw(background), x=48, y=60, font=font_en, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 顶部文字
            # Draw(background).text(xy=(48, 60), anchor="ms", align="center", text=f"{lvl}~{lvl + 1}", font=font_en, fill=(255, 255, 255, 255))  # 左侧文字

            item_count = 0
            for mat, count in skill.items():
                icon = self.get_material_icon(material_code=mat).resize(size=(64, 64))  # 材料图标大小
                self.text_border(text=str(count), draw=Draw(icon), x=45, y=57, font=font_en, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))  # 右下角的数字
                background.paste(im=icon, box=(112 + item_count, 16), mask=icon.split()[3])  # 透明度粘贴(r,g,b,a)
                item_count += 80
            backgrounds.append(background)

        # 粘到大图上
        for idx, bg in enumerate(backgrounds):
            if idx < 3:
                main_background.paste(im=bg, box=(idx * 352, 24))
            else:
                main_background.paste(im=bg, box=((idx - 3) * 352, 120))
        font_zh = ImageFont.truetype(self.font_file_zh, 16)
        # Draw(main_background).text(xy=(528, 20), anchor="ms", align="center", text="技 能 升 级", font=font_zh, fill=(255, 255, 255, 255))  # 最顶部的字
        self.text_border(text="技 能 升 级", draw=Draw(main_background), x=528, y=20, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 顶部文字

        main_draw = Draw(main_background)
        # main_draw.rectangle(xy=(0, 0, 1056, 216), outline=(50, 50, 50), width=4)  # 最外围边框
        main_draw.line(xy=(0, 0, 1056, 0), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 0, 0, 216), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(1054, 0, 1054, 216), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 214, 1056, 214), width=4, fill=(50, 50, 50))

        main_draw.line(xy=(0, 24, 1056, 24), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(0, 120, 1056, 120), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(96, 24, 96, 216), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(352, 24, 352, 216), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(448, 24, 448, 216), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(704, 24, 704, 216), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(800, 24, 800, 216), width=2, fill=(50, 50, 50))
        return main_background

    def _build_skills(self) -> Image:
        """绘制技能专精部分"""
        font_en = ImageFont.truetype(self.font_file_en, 24)
        font_zh = ImageFont.truetype(self.font_file_zh, 24)
        main_background = Image.new(mode="RGBA", size=(1056, 408), color=(235, 235, 235, 160))  # 底图
        if not self.is_skills:  # 没有技能升专精，如一星二星三星
            font_zh = ImageFont.truetype(self.font_file_zh, 48)
            Draw(main_background).text(xy=(528, 216), anchor="ms", align="center", text="该干员无技能专精", font=font_zh, fill=(255, 255, 255, 255))
            return main_background

        img_head_shadow = Image.new(mode="RGBA", size=(1056, 24), color=(175, 175, 175, 200))  # 顶部阴影
        main_background.paste(im=img_head_shadow, box=(0, 0), mask=img_head_shadow.split()[3])

        skills = self.operator.skills
        main_backgrounds = []
        for skill, data in skills.items():  # 对每个技能
            skill_main_backgrounds = Image.new(mode="RGBA", size=(352, 384), color=(235, 235, 235, 160))  # 每个技能的底图
            icon_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
            skill_main_backgrounds.paste(im=icon_shadow, box=(0, 0), mask=icon_shadow.split()[3])
            skill_icon = self.get_skill_icon(skill).resize(size=(96, 96))  # 技能图标
            skill_main_backgrounds.paste(im=skill_icon, box=(0, 0))
            skill_name = self.operator.map_skill_code2name(skill)  # 技能名
            draw = Draw(skill_main_backgrounds)
            self.text_border(text=skill_name, draw=draw, x=224, y=60, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))

            backgrounds = []
            for idx, level in enumerate(data):  # 对每层专精
                background = Image.new(mode="RGBA", size=(352, 96), color=(235, 235, 235, 160))  # 小底图
                text_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
                background.paste(im=text_shadow, box=(0, 0), mask=text_shadow.split()[3])

                level_icon = Image.open(IMAGE_PATH / "skill" / f"skill_lvl{idx + 1}.png", mode="r").convert("RGBA").resize(size=(96, 96))  # 专精图标
                background.paste(im=level_icon, box=(0, 0), mask=level_icon.split()[3])

                item_count = 0
                for mat, count in level.items():
                    icon = self.get_material_icon(mat).resize(size=(64, 64))  # 材料图标大小
                    self.text_border(text=str(count), draw=Draw(icon), x=45, y=57, font=font_en, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))
                    background.paste(im=icon, box=(112 + item_count, 16), mask=icon.split()[3])
                    item_count += 80
                backgrounds.append(background)

            # 粘到大图上
            for idx, bg in enumerate(backgrounds):
                skill_main_backgrounds.paste(im=bg, box=(0, (idx + 1) * 96))
            main_backgrounds.append(skill_main_backgrounds)

        for idx, bg in enumerate(main_backgrounds):
            main_background.paste(im=bg, box=(idx * 352, 24))
        font_zh = ImageFont.truetype(self.font_file_zh, 16)
        # Draw(main_background).text(xy=(528, 20), anchor="ms", align="center", text="技 能 专 精", font=font_zh, fill=(255, 255, 255, 255))  # 最顶部的字
        self.text_border(text="技 能 专 精", draw=Draw(main_background), x=528, y=20, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 左侧文字

        main_draw =Draw(main_background)
        main_draw.line(xy=(0, 0, 1056, 0), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 0, 0, 408), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(1054, 0, 1054, 408), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 406, 1056, 406), width=4, fill=(50, 50, 50))

        main_draw.line(xy=(0, 24, 1056, 24), width=2, fill=(50, 50, 50))

        main_draw.line(xy=(0, 120, 1056, 120), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(0, 216, 1056, 216), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(0, 312, 1056, 312), width=2, fill=(50, 50, 50))

        main_draw.line(xy=(96, 24, 96, 408), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(352, 24, 352, 408), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(448, 24, 448, 408), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(704, 24, 704, 408), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(800, 24, 800, 408), width=2, fill=(50, 50, 50))
        return main_background

    def _build_evolve(self) -> Image:
        """绘制精英化部分"""
        font_en = ImageFont.truetype(self.font_file_en, 24)
        font_zh = ImageFont.truetype(self.font_file_zh, 24)
        main_background = Image.new(mode="RGBA", size=(432, 216), color=(235, 235, 235, 160))  # 底图
        if not self.is_evolve_1:  # 没有技能升专精，如一星二星三星
            font_zh = ImageFont.truetype(self.font_file_zh, 48)
            Draw(main_background).text(xy=(216, 132), anchor="ms", align="center", text="该干员无法精英化", font=font_zh, fill=(255, 255, 255, 255))
            return main_background

        img_head_shadow = Image.new(mode="RGBA", size=(432, 24), color=(175, 175, 175, 200))  # 顶部阴影
        main_background.paste(im=img_head_shadow, box=(0, 0), mask=img_head_shadow.split()[3])

        evolve = self.operator.evolve
        backgrounds = []
        for lvl, data in evolve.items():
            background = Image.new(mode="RGBA", size=(432, 96), color=(235, 235, 235, 160))  # 底图
            text_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
            background.paste(im=text_shadow, box=(0, 0), mask=text_shadow.split()[3])
            # draw = Draw(background)
            level_icon = Image.open(IMAGE_PATH / "elite" / f"elite{lvl}.png", mode="r").convert("RGBA")  # 专精图标
            if lvl == 1:
                level_icon = level_icon.resize(size=(96, 63))
                background.paste(im=level_icon, box=(0, 16), mask=level_icon.split()[3])
            elif lvl == 2:
                level_icon = level_icon.resize(size=(96, 80))
                background.paste(im=level_icon, box=(0, 8), mask=level_icon.split()[3])
            # background.paste(im=level_icon, box=(0, 0), mask=level_icon.split()[3])
            # self.text_border(text=f"精 {lvl}", draw=draw, x=48, y=60, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))

            item_count = 0
            for mat, count in data.items():
                icon = self.get_material_icon(material_code=mat).resize(size=(64, 64))  # 材料图标大小
                if count >= 10000:
                    count = f"{count / 10000:.0f}w"
                    font = ImageFont.truetype(self.font_file_en, 14)
                    self.text_border(text=str(count), draw=Draw(icon), x=45, y=52, font=font, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))  # 右下角的数字
                else:
                    self.text_border(text=str(count), draw=Draw(icon), x=45, y=57, font=font_en, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))  # 右下角的数字
                background.paste(im=icon, box=(112 + item_count, 16), mask=icon.split()[3])  # 透明度粘贴(r,g,b,a)
                item_count += 80
            backgrounds.append(background)

        # 粘到大图上
        for idx, bg in enumerate(backgrounds):
            main_background.paste(im=bg, box=(0, 24 + idx * 96))
        font_zh = ImageFont.truetype(self.font_file_zh, 16)
        # Draw(main_background).text(xy=(216, 20), anchor="ms", align="center", text="精英化", font=font_zh, fill=(255, 255, 255, 255))  # 最顶部的字
        self.text_border(text="精 英 化", draw=Draw(main_background), x=216, y=20, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 左侧文字

        main_draw =Draw(main_background)
        main_draw.line(xy=(0, 0, 432, 0), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 0, 0, 216), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(430, 0, 430, 216), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 214, 432, 214), width=4, fill=(50, 50, 50))

        main_draw.line(xy=(0, 24, 432, 24), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(0, 120, 432, 120), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(96, 24, 96, 216), width=2, fill=(50, 50, 50))

        return main_background

    def get_operator_avatar(self) -> Image:
        return Image.open(IMAGE_PATH / "avatar" / f"{self.operator.code}.png").convert(mode="RGBA")

    def get_operator_skin(self) -> Union[str, bytes]:
        skins = os.listdir(IMAGE_PATH / "skin")
        result = [name for name in skins if self.operator.code in name]
        result.sort()
        try:
            return result[1]
        except IndexError:
            return result[0]

    @classmethod
    def _map_skill_icon_id(cls, skill_code: str) -> Image:
        """技能也有不同的"""
        with open(JSON_PATH / "skill_table.json", "r", encoding="utf-8") as f:
            skill_table = json.load(f)
        return next((data["iconId"] or data["skillId"] for skill, data in skill_table.items() if skill == skill_code), None)

    @classmethod
    def get_skill_icon(cls, skill_code: str) -> Image:
        # print(skill_code)
        return Image.open(IMAGE_PATH / "skill" / f"skill_icon_{cls._map_skill_icon_id(skill_code)}.png").convert( mode="RGBA")

    @classmethod
    def _map_item_icon_id(cls, item_code: str) -> str:
        """物品的代码名和图标名不同"""
        with open(JSON_PATH / "item_table.json", "r", encoding="utf-8") as f:
            item_table = json.load(f)
        return next((data["iconId"] for item, data in item_table["items"].items() if item == item_code), None)

    @classmethod
    def get_material_icon(cls, material_code: str) -> Image:
        return Image.open(IMAGE_PATH / "item" / f"{cls._map_item_icon_id(material_code)}.png").convert(mode="RGBA")

    @staticmethod
    def text_border(text: str, draw: ImageDraw, x: int, y: int, font: ImageFont, shadow_colour: tuple, fill_colour: tuple):
        """文字加边框"""
        draw.text((x - 1, y), text=text, anchor="ms", font=font, fill=shadow_colour)
        draw.text((x + 1, y), text=text, anchor="ms", font=font, fill=shadow_colour)
        draw.text((x, y - 1), text=text, anchor="ms", font=font, fill=shadow_colour)
        draw.text((x, y + 1), text=text, anchor="ms", font=font, fill=shadow_colour)

        draw.text((x - 1, y - 1), text=text, anchor="ms", font=font, fill=shadow_colour)
        draw.text((x + 1, y - 1), text=text, anchor="ms", font=font, fill=shadow_colour)
        draw.text((x - 1, y + 1), text=text, anchor="ms", font=font, fill=shadow_colour)
        draw.text((x + 1, y + 1), text=text, anchor="ms", font=font, fill=shadow_colour)

        draw.text((x, y), text=text, anchor="ms", font=font, fill=fill_colour)


__all__ = [
    "OperatorInfo",
    "BuildOperatorImage"
]