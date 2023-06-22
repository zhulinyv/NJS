from pathlib import Path
from typing import List
from pydantic import BaseModel,Field
from ruamel import yaml
from nonebot.permission import SUPERUSER
from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11.permission import (
    GROUP_ADMIN,
    GROUP_OWNER,
)

CONFIG_PATH = Path().joinpath('data/al/config.yml')

driver = get_driver()
COMMAND_START = list[driver.config.command_start]
try:
    NICKNAME: str = list(driver.config.nickname)[0]
except Exception:
    NICKNAME = 'bot'


ADMIN = SUPERUSER | GROUP_ADMIN | GROUP_OWNER 
# ADMINISTRATOR = SUPERUSER | GROUP_ADMIN | GROUP_OWNER | PRIVATE_FRIEND


class AzurConfig(BaseModel):
    online: bool = Field(False, alias='是否启用离线资源')


    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__fields__:
                self.__setattr__(key, value)
                
class AzurConfigManager:

    def __init__(self):
        self.file_path = CONFIG_PATH
        if self.file_path.exists():
            self.config = AzurConfig.parse_obj(
                yaml.load(self.file_path.read_text(encoding='utf-8'), Loader=yaml.Loader))
        else:
            self.config = AzurConfig()
        self.save()

    @property
    def config_list(self) -> List[str]:
        return list(self.config.dict(by_alias=True).keys())

    def save(self):
        with self.file_path.open('w', encoding='utf-8') as f:
            yaml.dump(
                self.config.dict(by_alias=True),
                f,
                indent=2,
                Dumper=yaml.RoundTripDumper,
                allow_unicode=True)

# 参数设置为全局变量
global config_manager,azur_config            
config_manager = AzurConfigManager()
azur_config = config_manager.config
