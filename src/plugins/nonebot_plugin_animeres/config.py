from typing import Optional
from pydantic import BaseModel
from nonebot import get_driver


class Config(BaseModel):
    cartoon_proxy: Optional[str] = None
    cartoon_forward: bool = False
    cartoon_length: int = 3
    cartoon_formant: str = "{title}\n{magnet}"


global_config = Config(**get_driver().config.dict())

