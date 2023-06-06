from nonebot import on_command
from nonebot.plugin import PluginMetadata

from .utils import bittorrent

# 声明一个响应器, 优先级10, 向下阻断
on_command("磁力搜索", aliases={'bt'}, priority=10, block=True,handlers=[bittorrent.main])

__plugin_meta__ = PluginMetadata(
    name="bittorrent",
    description="磁力搜索插件",
    usage="磁力搜索 xxx",
    extra={
        'author':   'Special-Week',
        'version':  '0.0.8',
        'priority': 10,
    }
)