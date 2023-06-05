from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_datastore import get_plugin_data
from sqlalchemy import JSON, Index, BigInteger, UniqueConstraint

Model = get_plugin_data().Model


class Comment(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    user_name: Mapped[str]
    content: Mapped[str]
    time: Mapped[datetime] = mapped_column(default=datetime.now())

    bottle_id: Mapped[int]


class Report(Model):
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "bottle_id",
            name="unique_report",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)

    bottle_id: Mapped[int]


class Bottle(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    group_id: Mapped[int] = mapped_column(BigInteger)
    user_name: Mapped[str]
    group_name: Mapped[str]
    content: Mapped[List[Dict[str, Any]]] = mapped_column(JSON)
    report: Mapped[int] = mapped_column(default=0)
    picked: Mapped[int] = mapped_column(default=0)
    is_del: Mapped[bool] = mapped_column(default=False)
    time: Mapped[datetime] = mapped_column(default=datetime.now())


Index(None, Bottle.user_id, Bottle.group_id)
