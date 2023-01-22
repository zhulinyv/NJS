from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """新活动数据/图片相关配置"""
    activities_img_path: str = "data/arktools/activity/img"
    activities_data_path: str = "data/arktools/activity/data"
