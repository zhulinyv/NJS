import base64
import io
from typing import Optional

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_txt2img import Txt2Img

from .config import l4_config

l4_font = l4_config.l4_font
"""直接超的智障回复"""


def mode_txt_to_img(
    title: str,
    text: str,
    ex_text: Optional[str] = None,
    font_size: int = 32,
    ex_msg: Optional[str] = None,
):
    """文字转图片，如果有额外的信息则构造图文"""
    txt2img = Txt2Img()
    txt2img.set_font_size(font_size)
    pic = txt2img.draw(title, text)
    pic = base64.b64decode(pic)

    if not ex_msg:
        msg = MessageSegment.image(pic)
    else:
        msg = Message(MessageSegment.image(pic) + MessageSegment.text(ex_msg))

    return msg
