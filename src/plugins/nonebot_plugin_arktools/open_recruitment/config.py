from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """公招识别相关配置"""
    tencent_cloud_secret_id: str  # 腾讯云 SecretId
    tencent_cloud_secret_key: str  # 腾讯云 SecretKey

    recruitment_save_path: str = "data/arktools/operator_info/build_image"