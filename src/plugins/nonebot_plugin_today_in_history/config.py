from typing import Union
from pydantic import BaseModel, Extra

from nonebot import get_driver

HOUR_ENV: int = 7
MINUTE_ENV: int = 35
PUSHDATA_ENV: dict = {}
GROUP_ALL_ENV: bool = False


class Config(BaseModel, extra=Extra.ignore):
    history_qq_groups_all: bool = False  # 为True时全开启，history_qq_groups失效
    history_qq_groups: list[int] = []  # 格式 [123,456]
    history_qq_friends: list[int] = []  # 格式 [123,456]
    history_inform_time: Union[str, list] = None  # 默认早上7:35


plugin_config = Config.parse_obj(get_driver().config.dict())

if plugin_config.history_inform_time == None:
    HOUR_ENV: int = 7
    MINUTE_ENV: int = 35
elif isinstance(plugin_config.history_inform_time, str):
    HOUR_ENV, MINUTE_ENV = plugin_config.history_inform_time.split(" ")
# 兼容 v0.0.8 及以下
elif isinstance(plugin_config.history_inform_time, list):
    HOUR_ENV = plugin_config.history_inform_time[0]["HOUR"]
    MINUTE_ENV = plugin_config.history_inform_time[0]["MINUTE"]


GROUP_ALL_ENV = plugin_config.history_qq_groups_all


for group in plugin_config.history_qq_groups:
    PUSHDATA_ENV.setdefault(
        "g_{}".format(group),
        {
            "hour": HOUR_ENV,
            "minute": MINUTE_ENV
        }
    )

for friend in plugin_config.history_qq_friends:
    PUSHDATA_ENV.setdefault(
        "f_{}".format(friend),
        {
            "hour": HOUR_ENV,
            "minute": MINUTE_ENV
        }
    )
