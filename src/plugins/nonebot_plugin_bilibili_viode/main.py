from typing import Union

from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot_plugin_guild_patch import GuildMessageEvent

from . import config
from .img import build_get_share_info, build_video_poster
from .utils import *

share_sort_url = on_message(priority=99, block=False)


@share_sort_url.handle()
async def _(event: Union[MessageEvent, GuildMessageEvent]):
    video_id_url = await bilibili_video_id_from_url(event.raw_message)
    video_id = await bilibili_video_id_validate(event.raw_message)
    if (video_id_url or video_id) is None:
        return
    if video_id_url is not None:
        video_id = await bilibili_video_id_validate(video_id_url)
    video_info = await get_video_info(video_id)
    if config.bilibili_poster:
        img = await build_video_poster(video_info)
    else:
        img = await build_get_share_info(video_info)
    if img:
        msg = MessageSegment.image(img) + MessageSegment.text(
            "\n点击前往:\n" + video_info.shareUrl
        )
        await share_sort_url.finish(msg)
