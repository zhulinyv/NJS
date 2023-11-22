import io
import httpx
import hashlib
import asyncio

from pil_utils import BuildImage, Text2Image
from nonebot.adapters.onebot.v11 import Message


async def download_avatar(user_id: int) -> bytes:
    url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = await download_url(url)
    if hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
        data = await download_url(url)
    return data


async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=20)
                resp.raise_for_status()
                return resp.content
            except Exception:
                await asyncio.sleep(3)
    raise Exception(f"{url} 下载失败！")


async def download_user_img(user_id: int):
    data = await download_avatar(user_id)
    img = BuildImage.open(io.BytesIO(data))
    return img.save_png()


async def user_img(user_id: int) -> bytes:
    """
    获取用户头像url
    """
    url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = await download_url(url)
    if hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
    return url


def text_to_png(msg):
    """
    文字转png
    """
    output = io.BytesIO()
    Text2Image.from_text(msg, 50, spacing=10).to_image("white", (20, 20)).save(
        output, format="png"
    )
    return output


def bbcode_to_png(msg, spacing: int = 10):
    """
    bbcode文字转png
    """
    output = io.BytesIO()
    Text2Image.from_bbcode_text(msg, 50, spacing=spacing).to_image(
        "white", (20, 20)
    ).save(output, format="png")
    return output


def get_message_at(message: Message) -> list:
    """
    获取at列表
    """
    qq_list = []
    for msg in message:
        if msg.type == "at":
            qq_list.append(int(msg.data["qq"]))
    return qq_list
