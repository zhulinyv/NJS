import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Literal, Set

from nonebot import get_driver
from pydantic import BaseModel, Field, root_validator
from tortoise import Tortoise, fields
from tortoise.models import Model
from tortoise.queryset import QuerySet

from .config import data_path

try:
    import ujson as json
except ModuleNotFoundError:
    import json


class Setting(BaseModel):
    type: Literal["blacklist", "whitelist"] = "blacklist"
    """名单类型"""
    blacklist: Set[int] = Field(default_factory=set)
    """黑名单"""
    whitelist: Set[int] = Field(default_factory=set)
    """白名单"""
    shield: Set[str] = Field(default_factory=set)
    """过滤词"""

    __file_path: Path = data_path / "setting.json"

    @property
    def file_path(self) -> Path:
        return self.__class__.__file_path

    @root_validator(pre=True)
    def init(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if cls.__file_path.is_file():
            return json.loads(cls.__file_path.read_text("utf-8"))
        return values

    def save(self) -> None:
        self.file_path.write_text(self.json(), encoding="utf-8")


setting = Setting()


class DrawCount(Model):
    uid: int = fields.IntField(index=True)
    """用户QQ"""
    gid: int = fields.IntField(index=True)
    """群号"""
    count: Dict[str, int] = fields.JSONField(default=dict)
    """计数字典"""

    @classmethod
    async def count_tags(cls, uid: int, gid: int, tags: str) -> None:
        tag = re.sub(r"[{[\]}]", "", tags)
        tag_count = Counter(tag.split(","))
        counter, _ = await cls.get_or_create(uid=uid, gid=gid)
        counter.count = dict(Counter(counter.count) + Counter(tag_count))
        await counter.save()

    @classmethod
    async def _get_count(cls, queryset: QuerySet) -> Counter:
        counts = queryset.values_list("count", flat=True)
        counter = Counter()
        async for count in counts:
            counter += Counter(count)
        return counter

    @classmethod
    async def get_user_count(cls, uid: int) -> Counter:
        return await cls._get_count(cls.filter(uid=uid))

    @classmethod
    async def get_group_count(cls, gid: int) -> Counter:
        return await cls._get_count(cls.filter(gid=gid))


driver = get_driver()


@driver.on_startup
async def init():
    sqlite_path = data_path / "aidraw.sqlite"

    config = {
        "connections": {
            "aidraw": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": sqlite_path},
            },
        },
        "apps": {
            "aidraw": {
                "models": [__name__],
                "default_connection": "aidraw",
            }
        },
    }

    await Tortoise.init(config)
    await Tortoise.generate_schemas()


@driver.on_shutdown
async def finish():
    await Tortoise.close_connections()
