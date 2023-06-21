from typing import Dict, List, Optional

from nonebot import require
from sqlalchemy import ForeignKey, delete, select
from sqlalchemy.orm import Mapped, relationship, selectinload, mapped_column

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import create_session, get_plugin_data

Model = get_plugin_data().Model


class OriginMessage(Model):
    message_id: Mapped[str] = mapped_column(primary_key=True)
    adapter_name: Mapped[str]
    channel_id: Mapped[Optional[str]]
    follow_messages: Mapped[List["FollowMessage"]] = relationship(
        back_populates="origin_message", cascade="all, delete-orphan"
    )


class FollowMessage(Model):
    message_id: Mapped[str] = mapped_column(primary_key=True)
    adapter_name: Mapped[str]
    channel_id: Mapped[Optional[str]]
    origin_message_id: Mapped[str] = mapped_column(
        ForeignKey("nonebot_plugin_follow_withdraw_originmessage.message_id")
    )
    origin_message: Mapped[OriginMessage] = relationship(
        back_populates="follow_messages"
    )


async def get_follow_message(
    adapter_name: str, message_id: str, channel_id: Optional[str] = None
) -> Optional[List[FollowMessage]]:
    async with create_session() as session:
        statement = (
            select(OriginMessage)
            .where(OriginMessage.adapter_name == adapter_name)
            .where(OriginMessage.channel_id == channel_id)
            .where(OriginMessage.message_id == message_id)
        ).options(selectinload(OriginMessage.follow_messages))
        if result := await session.scalar(statement):
            return result.follow_messages


async def save_message(
    adapter_name: str, origin_message_dict: Dict[str, str], message_dict: Dict[str, str]
) -> None:
    async with create_session() as session:
        statement = (
            select(OriginMessage)
            .where(OriginMessage.adapter_name == adapter_name)
            .where(OriginMessage.message_id == origin_message_dict["message_id"])
            .where(OriginMessage.channel_id == origin_message_dict.get("channel_id"))
        ).options(selectinload(OriginMessage.follow_messages))
        if result := await session.scalar(statement):
            follow_message = FollowMessage(
                message_id=message_dict["message_id"],
                channel_id=message_dict.get("channel_id"),
                adapter_name=adapter_name,
                origin_message_id=origin_message_dict["message_id"],
            )
            result.follow_messages.append(follow_message)
            await session.commit()
        else:
            origin_message = OriginMessage(
                message_id=origin_message_dict["message_id"],
                channel_id=origin_message_dict.get("channel_id"),
                adapter_name=adapter_name,
            )
            follow_message = FollowMessage(
                message_id=message_dict["message_id"],
                channel_id=origin_message_dict.get("channel_id"),
                adapter_name=adapter_name,
                origin_message_id=origin_message_dict["message_id"],
                origin_message=origin_message,
            )
            session.add(origin_message)
            await session.commit()


async def clear_message():
    async with create_session() as session:
        await session.execute(delete(OriginMessage))
        await session.execute(delete(FollowMessage))
        await session.commit()
