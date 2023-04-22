import json
from typing import Dict, List, Iterator, Optional
from pathlib import Path

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message

from .util import compare_msg
from .models import MatchType, IncludeCQCodeError
from .word_entry import WordEntry

NULL_BANK = {t.name: {"0": []} for t in MatchType}


class WordBank(object):
    def __init__(self):
        self.data_dir = Path("data/word_bank").absolute()
        self.bank_path = self.data_dir / "bank.json"
        self.img_dir = self.data_dir / "img"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.__data: Dict[str, Dict[str, List[WordEntry]]] = {}
        self.__load()

    def __load(self):
        if self.bank_path.exists() and self.bank_path.is_file():
            with self.bank_path.open("r", encoding="utf-8") as f:
                data: Dict[str, Dict[str, Dict[str, List[str]]]] = json.load(f)
            for t in MatchType:
                self.__data[t.name] = {}
                for user_id in data.get(t.name, {}).keys():
                    self.__data[t.name][user_id] = []
                    for key, value in data[t.name][user_id].items():
                        self.__data[t.name][user_id].append(WordEntry.load(key, value))
            logger.success("读取词库位于 " + str(self.bank_path))
        else:
            self.__data = NULL_BANK
            self.__save()
            logger.success("创建词库位于 " + str(self.bank_path))

    def __save(self):
        data: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        for t in self.__data.keys():
            data[t] = {}
            for user_id in self.__data[t].keys():
                data[t][user_id] = {}
                for entry in self.__data[t][user_id]:
                    key, values = entry.dump()
                    data[t][user_id][key] = values
        with self.bank_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def match(
        self,
        index: str,
        msg: Message,
        match_type: Optional[MatchType] = None,
        to_me: bool = False,
    ) -> List[Message]:
        """
        :说明: `match`
        > 匹配词条

        :参数:
          * `index: str`: 为0时是全局词库
          * `msg: Message`: 需要匹配的消息

        :可选参数:
          * `match_type: Optional[MatchType] = None`: 为空表示依次尝试所有匹配方式\n
                MatchType.congruence: 全匹配(==)
                MatchType.include: 模糊匹配(in)
                MatchType.regex: 正则匹配(regex)
          * `to_me: bool = False`: 匹配 @bot

        :返回:
          - `List[Message]`: 首先匹配成功的消息列表
        """
        if match_type is None:
            for type_ in MatchType:
                res = self.__match(index, msg, type_, to_me)
                if res:
                    return res
            return []
        else:
            return self.__match(index, msg, match_type, to_me)

    def __get_entries(self, index: str, match_type: MatchType) -> Iterator[WordEntry]:
        for entry in self.__data[match_type.name].get(index, []):
            yield entry
        if index != "0":
            for entry in self.__data[match_type.name].get("0", []):  # 加入全局词库
                yield entry

    def __match(
        self, index: str, msg: Message, match_type: MatchType, to_me: bool = False
    ) -> List[Message]:
        for entry in self.__get_entries(index, match_type):
            if entry.match(msg, match_type, to_me):
                return entry.get_values()
        return []

    def set(
        self,
        index: str,
        match_type: MatchType,
        key: Message,
        value: Message,
        require_to_me: bool = False,
    ) -> bool:
        """
        :说明: `set`
        > 新增词条

        :参数:
          * `index: str`: 为0时是全局词库
          * `match_type: MatchType`: 匹配方式\n
                MatchType.congruence: 全匹配(==)
                MatchType.include: 模糊匹配(in)
                MatchType.regex: 正则匹配(regex)
          * `key: Message`: 需要匹配的消息
          * `value: Message`: 触发后发送的短语

        :可选参数:
          * `require_to_me: bool = False`: 匹配 @bot

        :返回:
          - `bool`: 是否新增成功
        """
        name = match_type.name
        add = False

        # 如果为正则词条，检查是否为纯文本，否则抛出异常
        if match_type == MatchType.regex:
            for i in key:
                if i.type != "text":
                    raise IncludeCQCodeError("正则词条只能包含纯文本")

        if index in self.__data[name]:
            for entry in self.__data[name][index]:
                if entry.require_to_me != require_to_me:
                    continue
                if compare_msg(entry.key, key):
                    entry.add_value(value)
                    add = True
                    break
        else:
            self.__data[name][index] = []
        if not add:
            self.__data[name][index].append(WordEntry(key, [value], require_to_me))
        self.__save()
        return True

    def select(
        self,
        index: str,
        match_type: MatchType,
        key: Message,
        require_to_me: bool = False,
    ) -> List[WordEntry]:
        """
        :说明: `select`
        > 获取词条

        :参数:
          * `index: str`: 为0时是全局词库
          * `match_type: MatchType`: 匹配方式\n
                MatchType.congruence: 全匹配(==)
                MatchType.include: 模糊匹配(in)
                MatchType.regex: 正则匹配(regex)

        :可选参数:
          * `require_to_me: bool = False`: 匹配 @bot

        :返回:
          - `list`: 获取到的词条
        """
        return [
            entry
            for entry in list(self.__data[match_type.name].get(index, []))
            if entry.require_to_me == require_to_me
            and (not key or compare_msg(entry.key, key))
        ]

    def delete(
        self,
        index: str,
        match_type: MatchType,
        key: Message,
        require_to_me: bool = False,
    ) -> bool:
        """
        :说明: `delete`
        > 删除词条

        :参数:
          * `index: str`: 为0时是全局词库
          * `match_type: MatchType`: 匹配方式\n
                MatchType.congruence: 全匹配(==)
                MatchType.include: 模糊匹配(in)
                MatchType.regex: 正则匹配(regex)
          * `key: Message`: 触发短语

        :可选参数:
          * `require_to_me: bool = False`: 匹配 @bot

        :返回:
          - `bool`: 是否删除成功
        """
        name = match_type.name
        for entry in list(self.__data[name].get(index, [])):
            if entry.require_to_me != require_to_me:
                continue
            if compare_msg(entry.key, key):
                text = entry.get_values()
                text_str = str(text[0])
                k = 0
                n = text_str.count("file:///")
                if n != 0:
                    for i in range(n):
                        path2 = text_str.find(".image", k)
                        if path2 != -1:
                            path1 = text_str.find("file:///", k)
                            img_path = Path(text_str[path1 + 8:path2 + 6])
                            if img_path.is_file():
                                img_path.unlink()
                                if not img_path.is_file():
                                    logger.info("成功删除对应图片文件")
                            k = path2 + 6
                        else:
                            logger.info("不存在对应图片文件")
                self.__data[name][index].remove(entry)
                self.__save()
                return True
        return False

    def clear(self, index: str) -> bool:
        """
        :说明: `clear`
        > 清空词库

        :参数:
          * `index: str`: 为0时是全局词库, 为空时清空所有词库

        :返回:
          - `bool`: 是否清空成功
        """
        if index is None:
            self.__data = NULL_BANK
        else:
            for type_ in MatchType:
                name = type_.name
                if index in self.__data[name]:
                    del self.__data[name][index]
        self.__save()
        return True

    def keys(self, index: str, match_type: MatchType) -> List[Message]:
        """
        :说明: `keys`
        > 获取词库的触发短语列表

        :参数:
          * `index: str`: 为0时是全局词库
          * `match_type: MatchType`: 匹配方式\n
                MatchType.congruence: 全匹配(==)
                MatchType.include: 模糊匹配(in)
                MatchType.regex: 正则匹配(regex)

        :返回:
          - `List[Message]`: 触发短语列表
        """
        name = match_type.name
        keys: List[Message] = []
        for entry in self.__data[name][index]:
            keys.append(entry.get_key())
        return keys


word_bank = WordBank()
