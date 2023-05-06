from pathlib import Path
from typing import List, Literal, Optional, Union

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chatgpt_session_token: str = ""
    chatgpt_access_token: str = ""
    chatgpt_model: str = ""
    chatgpt_account: str = ""
    chatgpt_password: str = ""
    chatgpt_cd_time: int = 60
    chatgpt_notice: bool = True
    chatgpt_auto_refresh: bool = True
    chatgpt_proxies: Optional[str] = None
    chatgpt_refresh_interval: int = 30
    chatgpt_command: Union[str, List[str]] = ""
    chatgpt_to_me: bool = True
    chatgpt_timeout: int = 30
    chatgpt_api: str = "https://chat.loli.vet/"
    chatgpt_image: bool = False
    chatgpt_image_width: int = 500
    chatgpt_priority: int = 98
    chatgpt_block: bool = True
    chatgpt_private: bool = True
    chatgpt_scope: Literal["private", "public"] = "private"
    chatgpt_data: Path = Path(__file__).parent
    chatgpt_max_rollback: int = 8
    chatgpt_default_preset: str = ""

config = Config.parse_obj(get_driver().config)
