from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """每日资源关相关配置"""
    daily_levels_path: str = "data/arktools/daily_source"
