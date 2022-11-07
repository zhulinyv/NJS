from typing import Tuple
from pydantic import BaseModel, Extra

class Config(BaseModel, extra=Extra.ignore):
    waifu_cd_bye:int = 3600