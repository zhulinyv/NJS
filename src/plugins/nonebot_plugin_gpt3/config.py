from pydantic import BaseSettings, Field
from nonebot import get_driver
from nonebot.log import logger
from nonebot.rule import to_me


class Config(BaseSettings):
    # Your Config Here
    # gpt3_api_key_path: str = "config/chatgpt_api_key.yml"
    openai_api_key: str = ''
    gpt3_command_prefix: str = 'gpt3'
    gpt3_default_preset: str = ''
    gpt3_need_at: bool = False
    gpt3_image_render: bool = False
    gpt3_image_limit: int = 200
    gpt3_max_tokens: int = 1000
    gpt3_model: str = 'gpt-3.5-turbo'
    gpt3_chat_count_per_day: int = 200
    gpt3_proxy: str = ''

    class Config:
        extra = "ignore"


driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

# gpt3_api_key_path = config.gpt3_api_key_path
openai_api_key = config.openai_api_key
gpt3_command_prefix = config.gpt3_command_prefix
gpt3_need_at = config.gpt3_need_at
gpt3_image_render = config.gpt3_image_render
gpt3_image_limit = config.gpt3_image_limit
gpt3_max_tokens = config.gpt3_max_tokens
gpt3_model = config.gpt3_model
gpt3_default_preset = config.gpt3_default_preset
gpt3_proxy = config.gpt3_proxy
gpt3_chat_count_per_day = config.gpt3_chat_count_per_day



if openai_api_key:
    logger.info(f"加载api keys: {openai_api_key}")
else:
    logger.warning('没有配置api key')
logger.info(f"加载代理: {gpt3_proxy if gpt3_proxy else '无'}")
logger.info(f"加载默认人格: {gpt3_default_preset}")

# 基本会话
matcher_params = {}
matcher_params['cmd'] = gpt3_command_prefix
if gpt3_need_at:
    matcher_params['rule'] = to_me()

# 其他命令
need_at = {}
if gpt3_need_at:
    need_at['rule'] = to_me()
