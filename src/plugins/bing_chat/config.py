from pathlib import Path
from typing import Sequence, Literal

from nonebot import get_driver
from pydantic import BaseSettings


class Config(BaseSettings):
    bot_nickname: str = "脑积水"
    smart_reply_path: Path = Path("data/smart_reply")
    ai_reply_private: bool = True
    newbing_cd_time: int = 600
    newbing_style: Literal["creative", "balanced", "precise"] = "balanced"
    bing_or_openai_proxy: str = ""
    superusers: Sequence[str] = []

    class Config:
        extra = "ignore"


config: Config = Config.parse_obj(get_driver().config)


if not config.smart_reply_path.exists() or not config.smart_reply_path.is_dir():
    config.smart_reply_path.mkdir(0o755, parents=True, exist_ok=True)
