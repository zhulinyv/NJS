from pathlib import Path
from typing import Literal

from nonebot import get_driver
from pydantic import BaseModel, Extra, Field, validator


class Config(BaseModel, extra=Extra.ignore):
    ai_draw_api: str = "https://lulu.uedbq.xyz"
    ai_draw_token: str = ""
    ai_draw_cooldown: int = 60
    ai_draw_daily: int = 30
    ai_draw_timeout: int = 60
    ai_draw_revoke: int = 0
    ai_draw_message: Literal["mix", "part", "image"] = "mix"
    ai_draw_rank: int = Field(default=10, ge=0)
    ai_draw_data: Path = Path(__file__).parent
    ai_draw_text: str = "\n图像种子: {seed}\n提示标签: {tags}"
    ai_draw_database: bool = True

    @validator("ai_draw_data")
    def check_path(cls, v: Path):
        if v.exists() and not v.is_dir():
            raise ValueError("必须是有效的文件目录")
        return v


plugin_config = Config.parse_obj(get_driver().config)

api_url = plugin_config.ai_draw_api
token = plugin_config.ai_draw_token
cooldown_time = plugin_config.ai_draw_cooldown
daily_times = plugin_config.ai_draw_daily
timeout = plugin_config.ai_draw_timeout
revoke_time = plugin_config.ai_draw_revoke
message_mode = plugin_config.ai_draw_message
rank_number = plugin_config.ai_draw_rank
data_path = plugin_config.ai_draw_data / "data"
data_path.mkdir(parents=True, exist_ok=True)
save_path = plugin_config.ai_draw_data / "save"
save_path.mkdir(parents=True, exist_ok=True)
text_templet = plugin_config.ai_draw_text.replace("\\\\", "\\")
enable_database = plugin_config.ai_draw_database
