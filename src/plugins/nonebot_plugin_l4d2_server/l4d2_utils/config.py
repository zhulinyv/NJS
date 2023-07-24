import platform
from pathlib import Path
from typing import Any, Dict, List

from nonebot import get_driver
from nonebot.adapters.onebot.v11.permission import (
    GROUP_ADMIN,
    GROUP_OWNER,
    PRIVATE_FRIEND,
)
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from pydantic import BaseModel, Field
from ruamel import yaml

file_format = (".vpk", ".zip", ".7z", "rar")
# 权限

driver = get_driver()
COMMAND_START = list(driver.config.command_start)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
}

try:
    NICKNAME: str = list(driver.config.nickname)[0]
except Exception:
    NICKNAME = "bot"
CHECK_FILE: int = 0


reMaster = SUPERUSER | GROUP_OWNER
Master = SUPERUSER | GROUP_ADMIN | GROUP_OWNER
ADMINISTRATOR = SUPERUSER | GROUP_ADMIN | GROUP_OWNER | PRIVATE_FRIEND
# file 填写求生服务器所在路径


CONFIG_PATH = Path() / "data" / "L4D2" / "l4d2.yml"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


class L4d2GroupConfig(BaseModel):
    enable: bool = Field(True, alias="是否启用求生功能")
    map_master: List[str] = Field([], alias="分群地图管理员")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__fields__:
                self.__setattr__(key, value)


class L4d2Config(BaseModel):
    total_enable: bool = Field(True, alias="是否全局启用求生功能")
    l4_image: bool = Field(False, alias="是否启用图片")
    web_username: str = Field("l4d2", alias="后台管理用户名")
    web_password: str = Field("admin", alias="后台管理密码")
    l4_style: str = Field("standard", alias="图片风格")
    l4_ipall: List[Dict[str, Any]] = Field(
        [
            {
                "id_rank": "1",
                "place": False,
                "location": "C:\\l4d2",
                "host": "127.0.0.1",
                "port": "20715",
                "rcon": "114514",
                "server_id": "本地地图",
            },
            {
                "id_rank": "2",
                "place": True,
                "location": "/home/unbuntu/coop",
                "host": "11.4.51.4",
                "port": "20715",
                "rcon": "9191810",
                "account": "root",
                "password": "114514",
                "server_id": "远程地图",
            },
        ],
        alias="l4服务器ip集合",
    )
    l4_zl_tag: List[str] = Field(["云"], alias="坐牢三指令")
    l4_number: int = Field(1, alias="第几个地图路径")
    web_secret_key: str = Field(
        "49c294d32f69b732ef6447c18379451ce1738922a75cd1d4812ef150318a2ed0",
        alias="后台管理token密钥",
    )
    l4_master: List[str] = Field(["114514919"], alias="求生地图全局管理员qq")
    # l4_ip:bool = Field(False, alias='查询地图是否显示ip')
    l4_font: str = Field("simsun.ttc", alias="字体")
    l4_only: bool = Field(False, alias="下载地图是是否阻碍其他指令")
    l4_push_interval: int = Field(3, alias="定时任务间隔")
    l4_push_times: int = Field(10, alias="定时任务次数")
    l4_connect: bool = Field(True, alias="是否在查服命令后加入connect ip")
    group_config: Dict[int, L4d2GroupConfig] = Field({}, alias="分群配置")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__fields__:
                self.__setattr__(key, value)


class L4d2ConfigManager:
    def __init__(self):
        self.file_path = CONFIG_PATH
        if self.file_path.exists():
            self.config = L4d2Config.parse_obj(
                yaml.load(
                    self.file_path.read_text(encoding="utf-8"), Loader=yaml.Loader
                )
            )
        else:
            self.config = L4d2Config()  # type: ignore
        self.save()

    def get_group_config(self, group_id: int) -> L4d2GroupConfig:
        if group_id not in self.config.group_config:
            self.config.group_config[group_id] = L4d2GroupConfig()  # type: ignore
            self.save()
        return self.config.group_config[group_id]

    @property
    def config_list(self) -> List[str]:
        return list(self.config.dict(by_alias=True).keys())

    def save(self):
        with self.file_path.open("w", encoding="utf-8") as f:
            yaml.dump(
                self.config.dict(by_alias=True),
                f,
                indent=2,
                Dumper=yaml.RoundTripDumper,
                allow_unicode=True,
            )


# 参数设置为全局变量
global config_manager, l4_config
config_manager = L4d2ConfigManager()
l4_config = config_manager.config


class UserModel(BaseModel):
    username: str
    password: str


"""
地图路径
"""
vpk_path = "left4dead2/addons"


PLAYERSDATA = Path() / "data/L4D2/image/players"
"""用户数据路径"""
TEXT_PATH = Path(__file__).parent.parent / "data/L4D2/image"
"""图片存储路径"""
TEXT_XPATH = Path() / "data/L4D2/image"
"""内置图片路径"""


PLAYERSDATA = Path() / "data/L4D2/sql"
"""数据库路径"""
DATASQLITE = Path().parent.parent / "data/L4D2/sql/L4D2.db"
"""数据库！"""

table_data = ["L4d2_players", "L4D2_server"]
"""数据库表"""
L4d2_players_tag = ["qq", "nickname", "steamid"]
"""数据库表1"""
L4d2_server_tag = ["id", "qqgroup", "host", "port", "rcon"]
"""数据库表2"""
L4d2_INTEGER = ["id", "qq", "qqgroup", "port"]
"""INITEGER的表头"""
L4d2_TEXT = ["nickname", "steamid", "host", "rcon", "path"]
"""TEXT的表头"""
L4d2_BOOLEAN = ["use"]
"""BOOLEAN的表头"""

tables_columns = {table_data[0]: L4d2_players_tag, table_data[1]: L4d2_server_tag}

# 求生anne服务器
anne_url = "https://sb.trygek.com/"


# 系统
if platform.system() == "Windows":
    systems: str = "win"
elif platform.system() == "Linux":
    systems: str = "linux"
else:
    systems: str = "others"
ANNE_IP: Dict[str, List[Dict[str, str]]] = {}
