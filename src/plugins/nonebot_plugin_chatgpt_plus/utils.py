import json

from collections import defaultdict, deque
from pathlib import Path
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
)

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.rule import to_me
from pydantic import root_validator

from .data import setting
from .config import config


def convert_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}小时{minutes}分钟{seconds}秒"
    elif minutes > 0:
        return f"{minutes}分钟{seconds}秒"
    else:
        return f"{seconds}秒"

def cooldow_checker(cd_time: int) -> Any:
    cooldown = defaultdict(int)

    async def check_cooldown(
        matcher: Matcher, event: MessageEvent
    ) -> AsyncGenerator[None, None]:
        cooldown_time = cooldown[event.user_id] + cd_time
        if event.time < cooldown_time:
            await matcher.finish(
                f"ChatGPT 冷却中，剩余 {cooldown_time - event.time} 秒", at_sender=True
            )
        yield
        cooldown[event.user_id] = event.time

    return Depends(check_cooldown)

lockers = defaultdict(bool)
def single_run_locker() -> Any:
    async def check_running(
        matcher: Matcher, event: MessageEvent
    ) -> AsyncGenerator[None, None]:
        lockers[event.user_id] = lockers[event.user_id]
        if lockers[event.user_id]:
            await matcher.finish(
                "我知道你很急，但你先别急", reply_message=True
            )
        yield

    return Depends(check_running)

def create_matcher(
    command: Union[str, List[str]],
    only_to_me: bool = True,
    private: bool = True,
    priority: int = 999,
    block: bool = True,
) -> Type[Matcher]:
    params: Dict[str, Any] = {
        "priority": priority,
        "block": block,
    }

    if command:
        on_matcher = on_command
        command = [command] if isinstance(command, str) else command
        params["cmd"] = command.pop(0)
        params["aliases"] = set(command)
    else:
        on_matcher = on_message

    if only_to_me:
        params["rule"] = to_me()
    if not private:
        params["permission"] = GROUP

    return on_matcher(**params)


class Session(dict):
    __file_path: Path = config.chatgpt_data / "sessions.json"

    @property
    def file_path(self) -> Path:
        return self.__class__.__file_path

    def __init__(self, scope: Literal["private", "public"]) -> None:
        super().__init__()
        self.is_private = scope == "private"
        if self.__file_path.is_file():
            self.update(json.loads(self.__file_path.read_text("utf-8")))

    def __getitem__(self, event: MessageEvent) -> Dict[str, Any]:
        return super().__getitem__(self.id(event))

    def __setitem__(
        self,
        event: MessageEvent,
        value: Union[Tuple[Optional[str], Optional[str]], Dict[str, Any]],
    ) -> None:
        if isinstance(value, tuple):
            conversation_id, parent_id = value
        else:
            conversation_id = value["conversation_id"]
            parent_id = value["parent_id"]
        if self.__getitem__(event):
            if isinstance(value, tuple):
                self.__getitem__(event)["conversation_id"].append(conversation_id)
                self.__getitem__(event)["parent_id"].append(parent_id)
                if self.count(event) > config.chatgpt_max_rollback:
                    self[event]["conversation_id"] = self[event]["conversation_id"][-config.chatgpt_max_rollback:]
                    self[event]["parent_id"] = self[event]["parent_id"][-config.chatgpt_max_rollback:]
        else:
            super().__setitem__(
                self.id(event),
                {
                    # "conversation_id": deque(
                    #     [conversation_id], maxlen=config.chatgpt_max_rollback
                    # ),
                    # "parent_id": deque([parent_id], maxlen=config.chatgpt_max_rollback),
                    "conversation_id": [conversation_id],
                    "parent_id": [parent_id],
                },
            )

    def __delitem__(self, event: MessageEvent) -> None:
        return super().__delitem__(self.id(event))

    def __missing__(self, _) -> Dict[str, Any]:
        return {}

    def id(self, event: MessageEvent) -> str:
        if self.is_private:
            return event.get_session_id()
        return str(
            event.group_id if isinstance(event, GroupMessageEvent) else event.user_id
        )

    def save(self, name: str, event: MessageEvent) -> None:
        sid = self.id(event)
        if setting.session.get(sid) is None:
            setting.session[sid] = {}
        setting.session[sid][name] = {
            "conversation_id": self[event]["conversation_id"][-1],
            "parent_id": self[event]["parent_id"][-1],
        }
        setting.save()
        self.save_sessions()

    def save_sessions(self) -> None:
        self.file_path.write_text(json.dumps(self), encoding="utf-8")

    def find(self, event: MessageEvent) -> Dict[str, Any]:
        sid = self.id(event)
        return setting.session[sid]

    def count(self, event: MessageEvent):
        return len(self[event]["conversation_id"])

    def pop(self, event: MessageEvent):
        conversation_id = self[event]["conversation_id"].pop()
        parent_id = self[event]["parent_id"].pop()
        return conversation_id, parent_id
