import contextlib
from re import I

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import GROUP, PRIVATE_FRIEND
from nonebot.permission import SUPERUSER

from .mamager_handle import manager_handle
from .send_setu import send_setu

with contextlib.suppress(Exception):
    from nonebot.plugin import PluginMetadata
    __plugin_meta__ = PluginMetadata(
        name="setu4",
        description="内置数据库的setu插件, 尝试降低因为风控发不出图的概率",
        usage=r"^(setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?(.*)?",
        type="application",
        homepage="https://github.com/Special-Week/nonebot_plugin_setu4",
        supported_adapters={"~onebot.v11"},
        extra={
            'author':   'Special-Week',
            'version':  '0.02.114514',
            'priority': 10,
        }
    )



# 命令正则表达式
setu_regex: str = r"^(setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?(.*)?"
on_regex(
    setu_regex,
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
    priority=20,
    block=True,
    handlers=[send_setu.setu_handle]
)


# ----- 白名单添加与解除 -----
on_command(
    "setu_wl", 
    block=True, 
    priority=10,
    permission=SUPERUSER,
    handlers=[manager_handle.open_setu]
)


# ----- r18添加与解除 -----
on_command(
    "setu_r18", 
    block=True, 
    priority=10,
    permission=SUPERUSER,
    handlers=[manager_handle.set_r18]
)


# ----- cd时间更新 -----
on_command(
    "setu_cd", 
    block=True, 
    priority=10,
    permission=SUPERUSER,
    handlers=[manager_handle.set_cd]
)


# ----- 撤回时间更新 -----
on_command(
    "setu_wd", 
    block=True, 
    priority=10,
    permission=SUPERUSER,
    handlers=[manager_handle.set_wd]
)


# ----- 最大张数更新 -----
on_command(
    "setu_mn", 
    block=True, 
    priority=10,
    permission=SUPERUSER,
    handlers=[manager_handle.set_maxnum]
)


# ----- 黑名单添加与解除 -----
on_command(
    "setu_ban", 
    block=True, 
    priority=10,
    permission=SUPERUSER,
    handlers=[manager_handle.ban_setu]
)


# --------------- 发送帮助信息 ---------------
on_command(
    "setu_help", 
    block=True, 
    priority=10,
    aliases={"setu_帮助", "色图_help", "色图_帮助"}, 
    handlers=[manager_handle.setu_help]
)


# --------------- 更换代理 ---------------
on_command(
    "更换代理", 
    block=True, 
    priority=10,
    permission=SUPERUSER, 
    aliases={"替换代理", "setu_proxy"},
    handlers=[manager_handle.replace_proxy, manager_handle.replace_proxy_got]
)


# --------------- 查询黑白名单 ---------------
on_command(
    "setu_roster", 
    block=True, 
    priority=10,
    aliases={"色图名单"}, 
    permission=SUPERUSER,
    handlers=[manager_handle.query_black_white_list]
)


# --------------- 数据库更新 ---------------
on_command(
    'setu_db', 
    block=True, 
    priority=10,
    permission=SUPERUSER,
    handlers=[manager_handle.setu_db]
)
