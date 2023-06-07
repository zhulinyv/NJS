from io import BytesIO
from typing import Union

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot_plugin_guild_patch import GuildMessageEvent

from . import config
from .img import render_img
from .models.bilibili import VideoInfo
from .utils import bilibili_video_id_from_url, bilibili_video_id_validate

share_sort_url = on_message(block=False)


@share_sort_url.handle()
async def _(event: Union[MessageEvent, GuildMessageEvent], bot: Bot):
    # print(repr(event.raw_message), event.raw_message)
    video_id = bilibili_video_id_validate(event.raw_message)
    # print(video_id)
    if not video_id:
        # print(">>>>>")
        try:
            video_id = await bilibili_video_id_from_url(event.raw_message)
        except:
            return
        # print(video_id)
    else:
        pass
    if video_id.startswith("BV"):
        video_info = await VideoInfo.get(bvid=video_id)
    elif video_id.startswith("av"):
        video_info = await VideoInfo.get(aid=video_id[2:])
    img = render_img(video_info, config.bilibili_template)
    if img:
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        msg = MessageSegment.image(
            img_bytes.getvalue()) + MessageSegment.text("\n点击前往:" +
                                                        video_info.share_url)
        await bot.send(event, msg)
