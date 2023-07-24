from pathlib import Path
from typing import List

from PIL import Image, ImageDraw, ImageFont

# 半透明素材
half_whitel_image_path = Path(__file__).parent.parent.joinpath("data/img/white.png")
half_whitel_image = Image.open(half_whitel_image_path)


async def one_server_img(msg: dict):
    """单个服务器的dict信息变成图片"""
    img_background = await adjust_image_size(msg["Players"])
    img_background = await adjust_server_name(img_background, msg["name"])


async def adjust_image_size(text_list):
    """初始化背景"""
    initial_width = 1080
    initial_height = 600
    height_increment = 100

    num_players = len(text_list.get("Player", []))
    final_height = initial_height + num_players * height_increment

    image = Image.new("RGBA", (initial_width, final_height), "white")
    return image


async def adjust_server_name(image: Image.Image, name: str):
    """写标题"""
    pass


async def adjust_ping(image: Image.Image, ping: str):
    """写ping"""


async def adjust_player(image: Image.Image, Player: List[dict]):
    """写玩家"""
