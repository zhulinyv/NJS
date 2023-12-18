from nonebot.plugin.on import on_command

from .utils import *



# 使用bing的响应器
on_command(
    "bing", aliases={"newbing"}, priority=55, block=True, handlers=[newbing.bing_handle]
)