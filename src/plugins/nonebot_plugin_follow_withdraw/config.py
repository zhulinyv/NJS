from typing import List, Literal

from nonebot import get_driver
from pydantic import BaseModel

ADAPtER_NAME = Literal["OneBot V11", "OneBot V12", "QQ Guild", "Discord", "Kaiheila"]


class Config(BaseModel):
    follow_withdraw_all: bool = True
    follow_withdraw_interval: float = 0.5
    follow_withdraw_enable_adapters: List[ADAPtER_NAME] = [
        "OneBot V11",
        "OneBot V12",
        "QQ Guild",
        "Discord",
        "Kaiheila",
    ]
    follow_withdraw_bot_blacklist: List[str] = []
    follow_withdraw_plugin_blacklist: List[str] = []


driver = get_driver()

withdraw_config = Config.parse_obj(driver.config.dict())
