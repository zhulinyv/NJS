from pydantic import BaseSettings
from nonebot import get_driver
from nonebot.rule import to_me
import yaml
from pathlib import Path

class Config(BaseSettings):
    # Your Config Here
    gpt3_api_key_path: str = "config/chatgpt_api_key.yml"
    gpt3_command_prefix: str = 'chat2'
    gpt3_need_at: bool = False
    gpt3_image_render: bool = False
    gpt3_image_limit: int = 100
    gpt3_max_tokens: int = 400


    class Config:
        extra = "ignore"

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

gpt3_api_key_path = config.gpt3_api_key_path
gpt3_command_prefix = config.gpt3_command_prefix
gpt3_need_at = config.gpt3_need_at
gpt3_image_render = config.gpt3_image_render
gpt3_image_limit = config.gpt3_image_limit
gpt3_max_tokens = config.gpt3_max_tokens


# 如果不存在则创建
LOCAL = Path() / "config"
LOCAL.mkdir(exist_ok=True)
if not Path(gpt3_api_key_path).exists():
    with open(gpt3_api_key_path, 'w', encoding='utf-8') as f:
        yaml.dump({"api_keys": []}, f, allow_unicode=True)

with open(gpt3_api_key_path, 'r', encoding='utf-8') as f:
    api_key_list = yaml.load(f, Loader=yaml.FullLoader).get('api_keys')

from nonebot.log import logger
logger.info(f"加载 {len(api_key_list)}个 APIKeys")

# 基本会话
matcher_params = {}
matcher_params['cmd'] = gpt3_command_prefix
"""if gpt3_need_at:
    matcher_params['rule'] = to_me()"""

# 其他命令
need_at = {}
if gpt3_need_at:
    need_at['rule'] = to_me()
