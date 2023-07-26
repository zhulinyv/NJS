import asyncio
from dataclasses import dataclass
from io import BytesIO
from typing import Callable, List, Optional, Protocol, Tuple

import httpx
from nonebot.log import logger
from PIL.Image import Image as IMG
from pil_utils import BuildImage


@dataclass
class Command:
    keywords: Tuple[str, ...]
    func: Callable


def save_gif(frames: List[IMG], duration: float) -> BytesIO:
    output = BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration * 1000,
        loop=0,
        disposal=2,
        optimize=False,
    )
    return output


async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=20)
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
                await asyncio.sleep(3)
    raise Exception(f"{url} 下载失败！")


class Maker(Protocol):
    def __call__(self, img: BuildImage) -> BuildImage:
        ...


def get_avg_duration(image: IMG) -> float:
    if not getattr(image, "is_animated", False):
        return 0
    total_duration = 0
    for i in range(image.n_frames):
        image.seek(i)
        total_duration += image.info["duration"]
    return total_duration / image.n_frames


def split_gif(image: IMG) -> List[IMG]:
    frames: List[IMG] = []

    update_mode = "full"
    for i in range(image.n_frames):
        image.seek(i)
        if image.tile:  # type: ignore
            update_region = image.tile[0][1][2:]  # type: ignore
            if update_region != image.size:
                update_mode = "partial"
                break

    last_frame: Optional[IMG] = None
    for i in range(image.n_frames):
        image.seek(i)
        frame = image.copy()
        if update_mode == "partial" and last_frame:
            frame = last_frame.copy().paste(frame)
        frames.append(frame)
    image.seek(0)
    if image.info.__contains__("transparency"):
        frames[0].info["transparency"] = image.info["transparency"]
    return frames


def make_jpg_or_gif(
    img: BuildImage, func: Maker, keep_transparency: bool = True
) -> BytesIO:
    """
    制作静图或者动图
    :params
      * ``img``: 输入图片
      * ``func``: 图片处理函数，输入img，返回处理后的图片
      * ``keep_transparency``: 传入gif时，是否保留该gif的透明度
    """
    image = img.image
    if not getattr(image, "is_animated", False):
        return func(img).save_jpg()
    else:
        frames = split_gif(image)
        duration = get_avg_duration(image) / 1000
        frames = [func(BuildImage(frame)).image for frame in frames]
        if keep_transparency:
            image.seek(0)
            if image.info.__contains__("transparency"):
                frames[0].info["transparency"] = image.info["transparency"]
        return save_gif(frames, duration)
