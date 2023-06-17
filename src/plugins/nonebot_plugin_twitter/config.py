from pydantic import BaseModel,validator
from typing import Optional
from nonebot.log import logger
from nonebot import get_driver
import sys

if sys.version_info < (3, 10):
    from importlib_metadata import version
else:
    from importlib.metadata import version

try:
    __version__ = version("nonebot_plugin_bilichat")
except Exception:
    __version__ = None

class Config(BaseModel):
    twitter_website: Optional[str] = ""
    twitter_proxy: Optional[str] = None
    twitter_url: Optional[str] = ""
    twitter_qq: int = 2854196310
    command_priority: int = 10
    plugin_enabled: bool = True
    
    @validator("twitter_website")
    def check_twitter_website(cls,v):
        if isinstance(v,str):
            logger.info("twitter_website 读取成功")
            return v
    @validator("twitter_proxy")
    def check_proxy(cls,v):
        if isinstance(v,str):
            logger.info("twitter_proxy 读取成功")
            return v
    @validator("twitter_qq")
    def check_twitter_qq(cls,v):
        if isinstance(v,int):
            logger.info("twitter_qq 读取成功")
            return v
        
    @validator("command_priority")
    def check_command_priority(cls,v):
        if isinstance(v,int) and v >= 1:
            logger.info("command_priority 读取成功")
            return v
        
config_dev = Config.parse_obj(get_driver().config)

website_list = [
    "https://twitter.owacon.moe",
    "https://nitter.unixfox.eu",
    "https://nitter.1d4.us/",
    "https://nitter.it/",
    "https://bird.trom.tf/",
    "https://nitter.moomoo.me/"
]