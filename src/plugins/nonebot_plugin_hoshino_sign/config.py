import os
from nonebot import get_driver
from pydantic import BaseModel, Extra

class Config(BaseModel, extra=Extra.ignore):
    NICKNAME: str = "脑积水"
    stamp_path: str = os.path.join(os.path.dirname(__file__), "stamp")
    bg_mode: int = 1
    font_path: str = os.path.dirname(os.path.abspath(__file__)) + "/STHUPO.TTF"

sign_config = Config.parse_obj(get_driver().config.dict())
