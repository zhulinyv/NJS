import time
from typing import Union

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Event as v11Event
from nonebot.adapters.onebot.v12 import Event as v12Event
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.plugin import PluginMetadata
from pydantic import BaseModel


class Config(BaseModel):
    eventexpiry_expire: int = 30


__plugin_meta__ = PluginMetadata(
    name="过期事件过滤器",
    description="自动过滤过期事件",
    usage="自动过滤过期事件",
    type="library",
    homepage="https://github.com/A-kirami/nonebot-plugin-eventexpiry",
    config=Config,
    supported_adapters={"~onebot.v11", "~onebot.v12"},
)

driver = get_driver()

config = Config.parse_obj(driver.config)


@event_preprocessor
def event_expiry_handler(event: Union[v11Event, v12Event]) -> None:
    event_time = event.time if isinstance(event.time, int) else event.time.timestamp()
    if time.time() - event_time > config.eventexpiry_expire:
        raise IgnoredException("事件已过期")
