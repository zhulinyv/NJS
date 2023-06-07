from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    novelai_retry: int = 3 # post失败后重试的次数
    # 翻译API设置
    bing_key: str = None  # bing的翻译key
    deepl_key: str = None  # deepL的翻译key
    baidu_translate_key: dict = None # 例:{"SECRET_KEY": "", "API_KEY": ""} # https://console.bce.baidu.com/ai/?_=1685076516634#/ai/machinetranslation/overview/index
    novelai_todaygirl = 1 # 可选值 1 和 2 两种不同的方式
    novelai_tagger_site: str = None # 分析功能的地址 例如 127.0.0.1:7860
    vits_site: str = None


global_config = get_driver().config
config = Config.parse_obj(global_config)

