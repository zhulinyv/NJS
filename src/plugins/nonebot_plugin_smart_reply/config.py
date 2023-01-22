from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chatgpt_session_token: str = ""
    chatgpt_account: str = ""
    chatgpt_password: str = ""
    chatgpt_refresh_interval: int = 30
    chatgpt_timeout: int = 15
    chatgpt_api: str = "https://chat.openai.com/"


config = Config.parse_obj(get_driver().config)
