from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel


class Cfg(BaseModel):
    baproxy: Optional[str] = None


config = Cfg.parse_obj(get_driver().config.dict())
