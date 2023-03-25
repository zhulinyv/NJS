from pathlib import Path

from ..core.models_v3 import Character
from ..configs.path_config import PathConfig

from nonebot import get_driver

from typing import List, Set
from enum import Enum
from PIL import Image, ImageFont
from PIL.ImageDraw import Draw
from io import BytesIO


driver = get_driver()
pcfg = PathConfig.parse_obj(get_driver().config.dict())
data_path = Path(pcfg.arknights_data_path).absolute()
font_path = Path(pcfg.arknights_font_path).absolute()
GUESS_IMG_PATH = data_path / "guess_character"


async def get_all_characters() -> List["Character"]:
    """所有干员"""
    return await Character.all()


async def get_random_character() -> "Character":
    """随机一个干员"""
    return await Character.random()


class GuessResult(Enum):
    WIN = 0  # 猜对了
    LOSE = 1  # 没猜出
    DUPLICATE = 2  # 猜过了
    ILLEGAL = 3  # 不是干员


class GuessCharacter:
    def __init__(self, cht: "Character"):
        self._answer: "Character" = cht  # 目标
        self._times: int = 8  # 能猜的次数
        self._guessed: List["Character"] = []  # 猜过的

        self._block_size = (40, 40)  # 表情块尺寸
        self._block_padding = (10, 10)  # 表情块之间间距
        self._padding = (20, 20)  # 边界间距
        self._font_size = 32  # 字体大小
        self._font = ImageFont.truetype((font_path / "Arknights-zh.otf").__str__(), self._font_size)
        self._bg_color = (255, 255, 255)  # 背景颜色

        self._correct_face = Image.open(GUESS_IMG_PATH / "correct.png", "r").convert("RGBA")  # 完全一致
        self._vague_face = Image.open(GUESS_IMG_PATH / "vague.png", "r").convert("RGBA")  # 职业 / 阵营部分一致 / 答案高台地面均可放，猜高台或地面
        self._wrong_face = Image.open(GUESS_IMG_PATH / "wrong.png", "r").convert("RGBA")  # 完全不同
        self._up_face = Image.open(GUESS_IMG_PATH / "up.png", "r").convert("RGBA")  # 低于目标星级
        self._down_face = Image.open(GUESS_IMG_PATH / "down.png", "r").convert("RGBA")  # 高于目标星级

    async def guess(self, cht: Character) -> GuessResult:
        """每次猜完"""
        if not await self.is_character_legal(cht.name):
            return GuessResult.ILLEGAL
        if cht.name in {_.name for _ in self._guessed}:
            return GuessResult.DUPLICATE
        self._guessed.append(cht)

        if cht.name == self._answer.name:
            return GuessResult.WIN
        if len(self._guessed) == self._times:
            return GuessResult.LOSE

    async def draw_bar(self, cht: Character) -> Image:
        """画一行"""
        avatar = cht.avatar.resize((80, 80))
        rarity_face = self.get_rarity_face(cht)
        profession_face = self.get_profession_face(cht)
        faction_face = self.get_faction_face(cht)
        race_face = await self.get_race_face(cht)
        position_face = self.get_position_face(cht)

        bar = Image.new("RGBA", size=(80*6+16*5, 80), color=(0, 0, 0, 0))
        faces = [avatar, rarity_face, profession_face, faction_face, race_face, position_face]
        for idx, face in enumerate(faces):
            bar.paste(face, box=((80+16)*idx, 0), mask=face.split()[3])
        return bar

    async def draw(self) -> BytesIO:
        """正式绘画逻辑"""
        main_bg = Image.new("RGBA", size=(80*6+16*5+16*2, 32+80*8+16*8+16*2), color=(255, 255, 255, 255))

        # 先画头
        header = Image.new(mode="RGBA", size=(80*6+16*5, 32), color=(0, 0, 0, 0))
        draw = Draw(header)
        texts = ["干员", "星级", "职业", "阵营", "种族", "站位"]
        for i, t in enumerate(texts):
            draw.text(xy=((80+16)*i+40, 16), text=t, font=self._font, anchor="mm", fill=(0, 0, 0))
        main_bg.paste(im=header, box=(16, 16), mask=header.split()[3])

        # 一行一行画
        for idx, cht in enumerate(self._guessed):
            bar = await self.draw_bar(cht)
            main_bg.paste(im=bar, box=(16, 16+32+16+(80+16)*idx), mask=bar.split()[3])

        return self.save(main_bg)

    @staticmethod
    def save(image: Image) -> BytesIO:
        """临时缓存"""
        output = BytesIO()
        image = image.convert("RGB")
        image.save(output, format="jpeg")
        return output

    @staticmethod
    async def is_character_legal(cht_name: str) -> bool:
        """判断是不是咱的干员"""
        return cht_name in {_.name for _ in await get_all_characters()}

    def get_rarity_face(self, cht: Character) -> Image:
        """星级检查"""
        if cht.rarity > self._answer.rarity:
            return self._down_face
        elif cht.rarity < self._answer.rarity:
            return self._up_face
        else:
            return self._correct_face

    def get_profession_face(self, cht: Character) -> Image:
        """职业检查"""
        if cht.sub_profession_id == self._answer.sub_profession_id:
            return self._correct_face
        elif cht.profession_id == self._answer.profession_id:
            return self._vague_face
        else:
            return self._wrong_face

    def get_faction_face(self, cht: Character) -> Image:
        """阵营检查"""
        if cht.faction_id == self._answer.faction_id:
            return self._correct_face
        elif cht.faction_id.startswith(self._answer.faction_id) or self._answer.faction_id.startswith(cht.faction_id):
            return self._vague_face
        else:
            return self._wrong_face

    async def get_race_face(self, cht: Character) -> Image:
        """种族检查"""
        return self._correct_face if await cht.get_race() == await self._answer.get_race() else self._wrong_face

    def get_position_face(self, cht: Character) -> Image:
        """站位检查"""
        if cht.position == self._answer.position:
            return self._correct_face
        elif self._answer.position == "BOTH":
            return self._vague_face
        else:
            return self._wrong_face

    async def get_hint(self) -> str:
        """返回提示"""
        return (
            f"星数：{'★'*(self._answer.rarity+1)}"
            f"\n职业：{await self._answer.get_profession_name()}-{await self._answer.get_sub_profession_name()}"
            f"\n种族：{await self._answer.get_race()}"
            f"\n性别：{await self._answer.get_sex()}"
            f"\n阵营：{await self._answer.get_faction_name()}"
            f"\n站位：{self._answer.position}"
        )

    async def get_result(self) -> str:
        """返回结果"""
        return (
            f"答案: {self._answer.name}"
            f"\n{await self.get_hint()}"
        )

    @property
    def times(self) -> int:
        """最多猜几次"""
        return self._times

    @property
    def guessed(self) -> List["Character"]:
        """猜过的干员"""
        return self._guessed


__all__ = [
    "get_all_characters",
    "get_random_character",
    "GuessResult",
    "GuessCharacter"
]
