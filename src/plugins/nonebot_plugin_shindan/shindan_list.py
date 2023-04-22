import json
from pathlib import Path
from typing import Dict

data_path = Path() / "data" / "shindan" / "shindan_list.json"


default_list = {
    "162207": {"command": "今天是什么少女", "title": "你的二次元少女化形象"},
    "917962": {"command": "人设生成", "title": "人设生成器"},
    "790697": {"command": "中二称号", "title": "奇妙的中二称号生成器"},
    "587874": {"command": "异世界转生", "title": "異世界轉生—∩開始的種族∩——"},
    "1098085": {"command": "特殊能力", "title": "测测你的特殊能力是什么？"},
    "940824": {"command": "魔法人生", "title": "魔法人生：我在霍格沃兹读书时发生的两三事"},
    "1075116": {"command": "抽老婆", "title": "あなたの二次元での嫁ヒロイン", "mode": "text"},
    "400813": {"command": "抽舰娘", "title": "【艦これ】あなたの嫁になる艦娘は？"},
    "361845": {"command": "抽高达", "title": "マイ・ガンダム診断"},
    "595068": {"command": "英灵召唤", "title": "Fate 英霊召喚"},
    "1098152": {"command": "选秀剧本", "title": "你的选秀剧本"},
    "360578": {"command": "卖萌", "title": "顔文字作るよ(  ﾟдﾟ )", "mode": "text"},
}


def load_shindan_list() -> Dict[str, dict]:
    try:
        return json.load(data_path.open("r", encoding="utf-8"))
    except FileNotFoundError:
        return default_list


_shindan_list = load_shindan_list()


def dump_shindan_list():
    data_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        _shindan_list,
        data_path.open("w", encoding="utf-8"),
        indent=4,
        separators=(",", ": "),
        ensure_ascii=False,
    )


dump_shindan_list()


def get_shindan_list() -> Dict[str, dict]:
    return _shindan_list


def add_shindan(id: str, cmd: str, title: str) -> bool:
    if id in _shindan_list:
        return False
    _shindan_list[id] = {"command": cmd, "title": title}
    dump_shindan_list()
    return True


def del_shindan(id: str) -> bool:
    if id not in _shindan_list:
        return False
    _shindan_list.pop(id)
    dump_shindan_list()
    return True


def set_shindan(id: str, mode: str) -> bool:
    if id not in _shindan_list:
        return False
    _shindan_list[id]["mode"] = mode
    dump_shindan_list()
    return True
