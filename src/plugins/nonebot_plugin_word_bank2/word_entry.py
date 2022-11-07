import re
from typing import List, Tuple

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, unescape

from .util import compare_msg, include_msg
from .models import MatchType


class WordEntry:
    def __init__(
        self,
        key: Message,
        values: List[Message],
        require_to_me: bool = False,
    ):
        self.key = key
        self.values = values
        self.require_to_me = require_to_me  # 是否需要to_me

    def add_value(self, value: Message):
        if value not in self.values:
            self.values.append(value)

    def get_values(self) -> List[Message]:
        return self.values

    def get_key(self) -> Message:
        return self.key

    @staticmethod
    def load(key: str, values: List[str]) -> "WordEntry":
        require_to_me = False
        if key.startswith("/atme "):
            key = key[6:]
            require_to_me = True
        return WordEntry(Message(key), [Message(v) for v in values], require_to_me)

    def dump(self) -> Tuple[str, List[str]]:
        key = f"/atme {self.key}" if self.require_to_me else str(self.key)
        return key, [str(v) for v in self.values]

    def match(self, msg: Message, match_type: MatchType, to_me: bool = False) -> bool:
        msg = Message(str(msg).strip())  # 去除前后空格
        if self.require_to_me and not to_me:
            return False

        if match_type == MatchType.congruence:
            if len(self.key) != len(msg):
                return False
            return compare_msg(self.key, msg)

        elif match_type == MatchType.include:
            msg = Message(str(msg).strip())
            diff_len = len(msg) - len(self.key)
            if diff_len < 0:
                return False
            for start in range(diff_len + 1):
                if include_msg(msg[start : start + len(self.key)], self.key):
                    return True
            return False

        elif match_type == MatchType.regex:
            _msg = unescape(str(msg))
            _key = unescape(str(self.key))
            try:
                return bool(re.search(_key, _msg, re.S))
            except re.error:
                logger.error(f"正则匹配错误 - pattern: {_key}, string: {_msg}")
                return False

        return False
