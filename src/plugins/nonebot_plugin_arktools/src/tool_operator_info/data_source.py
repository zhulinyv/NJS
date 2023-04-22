"""
干员信息：
1. 头像、名称、立绘、代号、稀有度、职业、子职业、基础tag、位置、阵营
2. 血量、攻击、物防、法抗、费用、阻挡、再部署
3. 天赋
4. 潜能
5. 技能
6. 后勤
7. 精英化
8. 技能升级
9. 模组
"""
from pathlib import Path
from typing import Union

from PIL import Image, ImageFont
from PIL.ImageDraw import Draw
from io import BytesIO

from ..core.models_v3 import Character
from ..utils.image import text_border
from ..configs.path_config import PathConfig

from nonebot import get_driver


pcfg = PathConfig.parse_obj(get_driver().config.dict())
font_path = Path(pcfg.arknights_font_path).absolute()
gameimage_path = Path(pcfg.arknights_gameimage_path).absolute()
gamedata_path = Path(pcfg.arknights_gamedata_path).absolute()
# pcfg = PathConfig()


class BuildOperatorInfo:
    """作图"""
    def __init__(self, cht: Character, font_en: Union[str, Path] = font_path / "Arknights-en.ttf", font_zh: Union[str, Path] = font_path / "Arknights-zh.otf"):
        self._operator = cht
        self._font_en = font_en if isinstance(font_en, str) else font_en.__str__()
        self._font_zh = font_zh if isinstance(font_zh, str) else font_zh.__str__()

    @property
    def character(self) -> Character:
        return self._operator

    async def build_whole_image(self) -> BytesIO:
        all_skills_img: Image = await self._build_all_skills()
        equip_img: Image = await self._build_equips()
        elite_img: Image = await self._build_elite()
        skills_img: Image = await self._build_skills()
        skin_img: Image = await self._build_skin()

        main_background = Image.new(mode="RGBA", size=(1904, 768), color=(100, 100, 100, 200))
        Draw(main_background).rectangle(xy=(0, 0, 1904, 768), outline=(10, 10, 10), width=4)  # 最外围边框

        if self.character.rarity < 2:  # 只有精一立绘
            main_background.paste(im=skin_img, box=(-160, 0), mask=skin_img.split()[3])
        else:
            main_background.paste(im=skin_img, box=(-160, -140), mask=skin_img.split()[3])
        main_background.paste(im=all_skills_img, box=(800, 48), mask=all_skills_img.split()[3])  # 右上角
        main_background.paste(im=skills_img, box=(800, 312), mask=skills_img.split()[3])  # 右下角
        main_background.paste(im=elite_img, box=(320, 48), mask=elite_img.split()[3])  # 左上角
        main_background.paste(im=equip_img, box=(48, 312), mask=equip_img.split()[3])  # 左下角

        img_bytes = BytesIO()
        main_background.save(img_bytes, format="png")
        return img_bytes

    async def _build_all_skills(self) -> Image:
        """全技能升级"""
        font_en = ImageFont.truetype(self._font_en, 24)
        main_background = Image.new(mode="RGBA", size=(1056, 216), color=(235, 235, 235, 160))  # 底图
        if not self.character.has_skills:  # 没技能
            return self._build_all_skills_unavailable(main_background)

        img_head_shadow = Image.new(mode="RGBA", size=(1056, 24), color=(175, 175, 175, 200))  # 顶部阴影
        main_background.paste(im=img_head_shadow, box=(0, 0), mask=img_head_shadow.split()[3])

        backgrounds = []
        for lvl, all_skills in enumerate(self.character.all_skill_level_up):
            background = Image.new(mode="RGBA", size=(352, 96), color=(235, 235, 235, 160))  # 底图
            icon_box = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
            rank_icon = Image.open(gameimage_path / "ui" / "rank" / f"{lvl+1}.png").convert("RGBA").resize((96, 96))
            icon_box.paste(rank_icon, mask=rank_icon.split()[3])
            background.paste(im=icon_box, box=(0, 0), mask=icon_box.split()[3])
            # text_border(text=f"{lvl}~{lvl + 1}", draw=Draw(background), x=48, y=60, font=font_en, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 顶部文字
            for idx, cost_item in enumerate(await all_skills.get_cost()):
                icon = self.resize(cost_item.icon, 64)  # 材料图标大小
                text_border(text=str(cost_item.count), draw=Draw(icon), x=45, y=57, font=font_en, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))  # 右下角的数字
                background.paste(im=icon, box=(112 + idx*80, 16), mask=icon.split()[3])  # 透明度粘贴(r,g,b,a)
            backgrounds.append(background)

        for idx, bg in enumerate(backgrounds):
            if idx < 3:
                main_background.paste(im=bg, box=(idx * 352, 24))
            else:
                main_background.paste(im=bg, box=((idx - 3) * 352, 120))

        font_zh = ImageFont.truetype(self._font_zh, 16)
        text_border(text="技 能 升 级", draw=Draw(main_background), x=528, y=20, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 顶部文字

        main_draw = Draw(main_background)
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

    def _build_all_skills_unavailable(self, bg: Image) -> Image:
        """没技能的图"""
        font_zh = ImageFont.truetype(self._font_zh, 48)
        Draw(bg).text(xy=(528, 132), anchor="ms", align="center", text="该干员无技能升级", font=font_zh, fill=(255, 255, 255, 255))
        return bg

    async def _build_equips(self) -> Image:
        """模组升级"""
        font_en = ImageFont.truetype(self._font_en, 24)
        font_zh = ImageFont.truetype(self._font_zh, 24)
        main_background = Image.new(mode="RGBA", size=(704, 408), color=(235, 235, 235, 160))  # 底图
        if not await self.character.has_equips():
            return self._build_equips_unavailable(main_background)

        img_head_shadow = Image.new(mode="RGBA", size=(704, 24), color=(175, 175, 175, 200))  # 顶部阴影
        main_background.paste(im=img_head_shadow, box=(0, 0), mask=img_head_shadow.split()[3])

        main_backgrounds = []
        for equip in await self.character.get_equips():
            equip_main_backgrounds = Image.new(mode="RGBA", size=(352, 384), color=(235, 235, 235, 160))  # 每个模组的底图
            if equip.type_icon == "original":
                equip_icon = Image.open(gameimage_path / "equip" / "icon" / "default.png").convert("RGBA").resize((96, 96))
            else:
                equip_icon = Image.open(gameimage_path / "equip" / "icon" / f"{equip.icon_id}.png").convert("RGBA").resize((96, 96))
            icon_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
            icon_shadow.paste(im=equip_icon, box=(0, 0), mask=equip_icon.split()[3])
            equip_main_backgrounds.paste(im=icon_shadow, box=(0, 0), mask=icon_shadow.split()[3])
            text_border(text=equip.name, draw=Draw(equip_main_backgrounds), x=224, y=60, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))

            backgrounds = []
            for idx, items in (await equip.get_item_cost()).items():
                background = Image.new(mode="RGBA", size=(352, 96), color=(235, 235, 235, 160))  # 小底图
                text_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
                background.paste(im=text_shadow, box=(0, 0), mask=text_shadow.split()[3])

                level_icon = equip.rank(lvl=idx+1).resize((96-8, 96-8))
                background.paste(im=level_icon, box=(4, 4), mask=level_icon.split()[3])

                for idx_, cost_item in enumerate(items):
                    icon = self.resize(cost_item.icon, 64)
                    if cost_item.count >= 10000:
                        count = f"{cost_item.count / 10000:.0f}w"
                        font = ImageFont.truetype(self._font_en, 14)
                        text_border(text=str(count), draw=Draw(icon), x=45, y=52, font=font, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))
                    else:
                        text_border(text=str(cost_item.count), draw=Draw(icon), x=45, y=57, font=font_en, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))
                    background.paste(im=icon, box=(112 + idx_*80, 16), mask=icon.split()[3])
                backgrounds.append(background)

            # 粘到大图上
            for idx, bg in enumerate(backgrounds):
                equip_main_backgrounds.paste(im=bg, box=(0, (idx + 1) * 96))
            main_backgrounds.append(equip_main_backgrounds)

        for idx, bg in enumerate(main_backgrounds):
            main_background.paste(im=bg, box=(idx * 352, 24))
        font_zh = ImageFont.truetype(self._font_zh, 16)
        text_border(text="模 组 升 级", draw=Draw(main_background), x=352, y=20, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 左侧文字

        main_draw = Draw(main_background)
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

    def _build_equips_unavailable(self, bg: Image) -> Image:
        """没模组"""
        font_zh = ImageFont.truetype(self._font_zh, 48)
        Draw(bg).text(xy=(352, 216), anchor="ms", align="center", text="该干员无模组", font=font_zh, fill=(255, 255, 255, 255))
        return bg

    async def _build_elite(self) -> Image:
        """精英化"""
        font_en = ImageFont.truetype(self._font_en, 24)
        main_background = Image.new(mode="RGBA", size=(432, 216), color=(235, 235, 235, 160))  # 底图
        if not self.character.can_evolve_1:  # 无法精1
            return self._build_elite_unavailable(main_background)

        img_head_shadow = Image.new(mode="RGBA", size=(432, 24), color=(175, 175, 175, 200))  # 顶部阴影
        main_background.paste(im=img_head_shadow, box=(0, 0), mask=img_head_shadow.split()[3])

        phases = self.character.phases
        backgrounds = []
        for lvl, phase in enumerate(phases):
            if lvl == 0:
                continue
            background = Image.new(mode="RGBA", size=(432, 96), color=(235, 235, 235, 160))  # 底图
            icon_box = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
            background.paste(im=icon_box, box=(0, 0), mask=icon_box.split()[3])
            level_icon = Image.open(gameimage_path / "ui" / "elite" / f"{lvl}.png", mode="r").convert("RGBA")
            if lvl in [1, 2]:
                level_icon = level_icon.resize(size=(96, 93))
                background.paste(im=level_icon, box=(0, 0), mask=level_icon.split()[3])
            costs = await phase.get_elite_cost()
            item_count = 0
            for cost_item in costs:
                icon = cost_item.icon.resize(size=(64, 64))  # 材料图标大小
                count = cost_item.count
                if count >= 10000:
                    count = f"{count / 10000:.0f}w"
                    font = ImageFont.truetype(self._font_en, 14)
                    text_border(text=str(count), draw=Draw(icon), x=45, y=52, font=font, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))  # 右下角的数字
                elif count <= 0:
                    continue
                else:
                    text_border(text=str(count), draw=Draw(icon), x=45, y=57, font=font_en, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))  # 右下角的数字
                background.paste(im=icon, box=(112 + item_count, 16), mask=icon.split()[3])  # 透明度粘贴(r,g,b,a)
                item_count += 80
            backgrounds.append(background)

        # 粘到大图上
        for idx, bg in enumerate(backgrounds):
            main_background.paste(im=bg, box=(0, 24 + idx * 96))
        font_zh = ImageFont.truetype(self._font_zh, 16)
        # Draw(main_background).text(xy=(216, 20), anchor="ms", align="center", text="精英化", font=font_zh, fill=(255, 255, 255, 255))  # 最顶部的字
        text_border(text="精 英 化", draw=Draw(main_background), x=216, y=20, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 左侧文字

        main_draw =Draw(main_background)
        main_draw.line(xy=(0, 0, 432, 0), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 0, 0, 216), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(430, 0, 430, 216), width=4, fill=(50, 50, 50))
        main_draw.line(xy=(0, 214, 432, 214), width=4, fill=(50, 50, 50))

        main_draw.line(xy=(0, 24, 432, 24), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(0, 120, 432, 120), width=2, fill=(50, 50, 50))
        main_draw.line(xy=(96, 24, 96, 216), width=2, fill=(50, 50, 50))

        return main_background

    def _build_elite_unavailable(self, bg: Image) -> Image:
        """没法精英化"""
        font_zh = ImageFont.truetype(self._font_zh, 48)
        Draw(bg).text(xy=(216, 132), anchor="ms", align="center", text="该干员无法精英化", font=font_zh, fill=(255, 255, 255, 255))
        return bg

    async def _build_skills(self) -> Image:
        """技能专精"""
        font_en = ImageFont.truetype(self._font_en, 24)
        font_zh = ImageFont.truetype(self._font_zh, 24)
        main_background = Image.new(mode="RGBA", size=(1056, 408), color=(235, 235, 235, 160))  # 底图
        if not self.character.can_skills_lvl_up:  # 不能专精
            return self._build_skills_unavailable(main_background)

        img_head_shadow = Image.new(mode="RGBA", size=(1056, 24), color=(175, 175, 175, 200))  # 顶部阴影
        main_background.paste(im=img_head_shadow, box=(0, 0), mask=img_head_shadow.split()[3])
        main_backgrounds = []
        for skill in await self.character.get_skills():
            skill_main_backgrounds = Image.new(mode="RGBA", size=(352, 384), color=(235, 235, 235, 160))  # 每个技能的底图

            icon_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
            skill_main_backgrounds.paste(im=icon_shadow, box=(0, 0), mask=icon_shadow.split()[3])

            skill_icon = skill.icon.resize(size=(96, 96))  # 技能图标
            skill_main_backgrounds.paste(im=skill_icon, box=(0, 0))

            text_border(text=skill.name, draw=Draw(skill_main_backgrounds), x=224, y=60, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))

            backgrounds = []
            for idx, cond in enumerate(skill.level_up_cost_condition):
                background = Image.new(mode="RGBA", size=(352, 96), color=(235, 235, 235, 160))  # 小底图
                text_shadow = Image.new(mode="RGBA", size=(96, 96), color=(205, 205, 205, 200))  # 左侧阴影
                background.paste(im=text_shadow, box=(0, 0), mask=text_shadow.split()[3])

                level_icon = skill.rank(idx+1).convert("RGBA").resize(size=(96, 96))  # 专精图标
                background.paste(im=level_icon, box=(0, 0), mask=level_icon.split()[3])

                for idx_, cost_item in enumerate(await cond.get_cost()):
                    icon = self.resize(cost_item.icon, 64)  # 材料图标大小
                    text_border(text=str(cost_item.count), draw=Draw(icon), x=45, y=57, font=font_en, shadow_colour=(255, 255, 255, 255), fill_colour=(0, 0, 0, 255))
                    background.paste(im=icon, box=(112 + 80*idx_, 16), mask=icon.split()[3])

                backgrounds.append(background)

            # 粘到大图上
            for idx, bg in enumerate(backgrounds):
                skill_main_backgrounds.paste(im=bg, box=(0, (idx + 1) * 96))
            main_backgrounds.append(skill_main_backgrounds)

        for idx, bg in enumerate(main_backgrounds):
            main_background.paste(im=bg, box=(idx * 352, 24))
        font_zh = ImageFont.truetype(self._font_zh, 16)
        text_border(text="技 能 专 精", draw=Draw(main_background), x=528, y=20, font=font_zh, shadow_colour=(0, 0, 0, 255), fill_colour=(255, 255, 255, 255))  # 左侧文字

        main_draw = Draw(main_background)
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

    def _build_skills_unavailable(self, bg: Image) -> Image:
        """不能专精的图"""
        font_zh = ImageFont.truetype(self._font_zh, 48)
        Draw(bg).text(xy=(528, 216), anchor="ms", align="center", text="该干员无技能专精", font=font_zh, fill=(255, 255, 255, 255))
        return bg

    async def _build_skin(self) -> Image:
        """立绘"""
        return self.character.skin.convert(mode="RGBA").resize((1176, 1176))

    @staticmethod
    def resize(img: Image, size: int):
        w, h = img.size
        img = img.resize((int(w*size/h), size)) if w >= h else img.resize((size, int(h*size/h)))
        return img


__all__ = [
    "BuildOperatorInfo"
]
