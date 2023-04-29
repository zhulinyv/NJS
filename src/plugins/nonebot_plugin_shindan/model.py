from nonebot_plugin_datastore import get_plugin_data
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

Model = get_plugin_data().Model


class ShindanRecord(Model):
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    shindan_id: Mapped[str] = mapped_column(String(32))
    command: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, default="")
    mode: Mapped[str] = mapped_column(String(32), default="image")
