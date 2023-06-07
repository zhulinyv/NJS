from pydantic import BaseSettings


# 其他地方出现的类似 from .. import config，均是从 __init__.py 导入的 Config 实例
class Config(BaseSettings):

    bilibili_template: str = "1"

    class Config:
        extra = "ignore"
