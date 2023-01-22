import os
from typing import Optional, List, Tuple, Dict, Union
import httpx
from PIL.ImageDraw import Draw, ImageDraw
from nonebot.adapters.onebot.v11 import MessageSegment
from pathlib import Path
import json
from PIL import Image, ImageFont
from aiofiles import os as aos, open as aopen

ALBUM_COVER_PATH = Path(__file__).parent.parent / "_data" / "monster-siren" / "album" / "covers"
SAVE_PATH = Path(__file__).parent.parent / "_data" / "monster-siren" / "album" / "build_image"
FONT_PATH = Path(__file__).parent.parent / "_data" / "operator_info" / "font"


async def search_cloud(keyword: str) -> Optional[MessageSegment]:
    """网易云"""
    url = "https://music.163.com/api/cloudsearch/pc"
    params = {"s": keyword, "type": 1, "offset": 0, "limit": 1}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, params=params)
        result = resp.json()
    if songs := result["result"]["songs"]:
        return MessageSegment.music("163", songs[0]["id"])

    return None


async def load_siren_list() -> List:
    with open(Path(__file__).parent.parent / "_apis" / "monster-siren.json", "r", encoding="utf-8") as fp:
        siren_apis = json.load(fp)
    albums_url = siren_apis["albums"]["url"]

    async with httpx.AsyncClient() as client:
        albums_data = (await client.get(albums_url)).json()["data"]

    return albums_data


async def init_covers(albums_data: List[Dict]):
    for path in {ALBUM_COVER_PATH}:
        if not path.exists():
            await aos.makedirs(path)
    async with httpx.AsyncClient() as client:
        for album in albums_data:
            name = album["name"]
            if (ALBUM_COVER_PATH / name).exists():
                continue
            cover = (await client.get(album["coverUrl"])).content
            async with aopen(ALBUM_COVER_PATH / f"{name}.png", "wb") as fp:
                await fp.write(cover)


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


async def build_image():
    albums_data = await load_siren_list()
    font = ImageFont.truetype(str(FONT_PATH / "Arknights-zh.otf"), 24)
    await init_covers(albums_data)

    main_background = Image.new(mode="RGBA", size=(2824, 4000), color=(0, 0, 0, 100))
    album_backgrounds = []
    for album in albums_data:
        album_bg = Image.new(mode="RGBA", size=(256, 320), color=(0, 0, 0, 0))
        name = album["name"]
        cover = Image.open(ALBUM_COVER_PATH / f"{name}.png").convert("RGBA").resize(size=(256, 256))

        album_bg.paste(im=cover, box=(0, 0), mask=cover.split()[3])
        text_border(text=name, draw=Draw(album_bg), anchor="mm", x=128, y=288, font=font, fill_colour=(255, 255, 255, 255), shadow_colour=(0, 0, 0, 255))
        album_backgrounds.append(album_bg)

    last_high = 0
    for idx, album_bg in enumerate(album_backgrounds):
        main_background.paste(im=album_bg, box=(24 + 280 * (idx % 10), 24 + 344 * (idx // 10)))
        last_high = 24 + 344 * (idx // 10) + 344

    main_background = main_background.crop(box=(0, 0, 2824, last_high))
    file = SAVE_PATH / "temp.png"
    None if os.path.exists(SAVE_PATH) else os.makedirs(SAVE_PATH)
    main_background.save(file)
    return file
