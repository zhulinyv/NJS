"""代理设置"""
from pydantic import BaseModel, Extra


class ProxyConfig(BaseModel, extra=Extra.ignore):
    """github代理相关配置"""
    github_raw: str = "https://raw.githubusercontent.com"  # 资源网址
    github_site: str = "https://github.com"  # 访问网址
    rss_site: str = "https://rsshub.app"


__all__ = [
    "ProxyConfig"
]
