from pydantic import BaseModel,validator
from typing import Optional
from nonebot.log import logger
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
    bearer_token: Optional[str] = ""
    twitter_proxy: Optional[str] = ""
    command_priority: int = 10
    plugin_enabled: bool = True
    twitter_debug: bool = False
    
    @validator("bearer_token")
    def check_bearer_token(cls,v):
        if isinstance(v,str):
            logger.info("bearer_token 读取成功")
            return v
    @validator("twitter_proxy")
    def check_proxy(cls,v):
        if isinstance(v,str):
            logger.info("twitter_proxy 读取成功")
            return v
        
    @validator("command_priority")
    def check_command_priority(cls,v):
        if isinstance(v,int) and v >= 1:
            logger.info("command_priority 读取成功")
            return v
    
    @validator("twitter_debug")
    def check_twitter_debug(cls,v):
        if isinstance(v,bool):
            logger.info("twitter_debug 开启成功")
            return v
