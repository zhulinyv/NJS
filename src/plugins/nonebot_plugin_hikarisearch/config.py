from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    hikarisearch_api: str = "https://hikari.obfs.dev"
    hikarisearch_max_results: int = 3
    hikarisearch_withdraw: int = 0


hikari_config = Config.parse_obj(get_driver().config.dict())
