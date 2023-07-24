from io import BytesIO

from nonebot.log import logger
from PIL import Image

# import sys
# sys.modules["srctools._cy_vtf_readwrite"] = None
from srctools.vtf import VTF, ImageFormats


async def img_to_vtf(pic_byte: bytes, tag) -> BytesIO:
    pic = BytesIO(pic_byte)
    pic = Image.open(pic).convert("RGBA")
    vtf_io = BytesIO()
    vtf_ = VTF(
        1024, 1024, fmt=ImageFormats.DXT5, thumb_fmt=ImageFormats.DXT1, version=(7, 2)
    )
    if tag == "覆盖":
        logger.info(tag)
        img2 = Image.new("RGBA", (1024, 1024), (255, 255, 255, 0))
        r, g, b, a = pic.split()
        img2.paste(pic, mask=a)
        pic = pic.resize((1024, 1024))
    elif tag == "填充":
        w, h = pic.size
        if w > h:
            ratio = 1024 / w
            new_width = 1024
            new_height = int(h * ratio)
        else:
            ratio = 1024 / h
            new_height = 1024
            new_width = int(w * ratio)
        pic = pic.resize((new_width, new_height), Image.ANTIALIAS)
        background = Image.new("RGBA", (1024, 1024), (255, 255, 255, 0))
        background.paste(pic, ((1024 - new_width) // 2, (1024 - new_height) // 2))
        pic = background
    else:
        logger.info("拉伸")
        pic = pic.resize((1024, 1024))
    largest_frame = vtf_.get()
    largest_frame.copy_from(pic.tobytes(), ImageFormats.RGBA8888)
    vtf_.save(vtf_io, version=(7, 2))
    return vtf_io
