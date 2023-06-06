from typing import Optional
import nonebot
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    github_token : Optional[str] = None

global_config = nonebot.get_driver().config
githubcard_config = Config(**global_config.dict())