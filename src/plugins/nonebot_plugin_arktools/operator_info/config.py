from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """干员信息相关配置"""
    operator_save_path: str = "data/arktools/operator_info/build_image"