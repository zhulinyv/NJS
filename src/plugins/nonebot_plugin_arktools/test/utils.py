
"""
Fork from: https://github.com/nonebot/nonebot2/blob/master/tests/utils.py
"""
from typing import TYPE_CHECKING, Type, Optional

from pydantic import create_model

if TYPE_CHECKING:
    from nonebot.adapters import Event, Message


def make_fake_message() -> Type["Message"]:
    from nonebot.adapters import Message, MessageSegment

    class FakeMessageSegment(MessageSegment):
        @classmethod
        def get_message_class(cls):
            return FakeMessage

        def __str__(self) -> str:
            return self.data["text"] if self.type == "text" else f"[fake:{self.type}]"

        @classmethod
        def text(cls, text: str):
            return cls("text", {"text": text})

        @classmethod
        def image(cls, url: str):
            return cls("image", {"url": url})

        def is_text(self) -> bool:
            return self.type == "text"

    class FakeMessage(Message):
        @classmethod
        def get_segment_class(cls):
            return FakeMessageSegment

        @staticmethod
        def _construct(msg: str):
            yield FakeMessageSegment.text(msg)

    return FakeMessage


def make_fake_event(
    _type: str = "message",
    _name: str = "test",
    _description: str = "test",
    _user_id: str = "test",
    _session_id: str = "test",
    _message: Optional["Message"] = None,
    _to_me: bool = True,
    **fields,
) -> Type["Event"]:
    from nonebot.adapters import Event

    _Fake = create_model("_Fake", __base__=Event, **fields)

    class FakeEvent(_Fake):
        def get_type(self) -> str:
            return _type

        def get_event_name(self) -> str:
            return _name

        def get_event_description(self) -> str:
            return _description

        def get_user_id(self) -> str:
            return _user_id

        def get_session_id(self) -> str:
            return _session_id

        def get_message(self) -> "Message":
            if _message is not None:
                return _message
            raise NotImplementedError

        def is_tome(self) -> bool:
            return _to_me

        class Config:
            extra = "forbid"

    return FakeEvent
