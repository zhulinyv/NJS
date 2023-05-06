"""通用功能"""
import json
import os
from pathlib import Path
from typing import Union, Dict, List
from nonebot import get_driver
from aiofiles import open as aopen
from nonebot import logger

from ..configs import PathConfig


pcfg = PathConfig.parse_obj(get_driver().config.dict())
data_path = Path(pcfg.arknights_data_path).absolute()
gamedata_path = Path(pcfg.arknights_gamedata_path).absolute()
# pcfg = PathConfig()

CHARACTER_FILE = gamedata_path / "excel" / "character_table.json"
ITEM_FILE = gamedata_path / "excel" / "item_table.json"
SUB_PROF_FILE = gamedata_path / "excel" / "uniequip_table.json"
EQUIP_FILE = SUB_PROF_FILE
TEAM_FILE = gamedata_path / "excel" / "handbook_team_table.json"
SWAP_PATH = data_path / "arknights" / "processed_data"
GACHA_PATH = gamedata_path / "excel" / "gacha_table.json"
STAGE_PATH = gamedata_path / "excel" / "stage_table.json"
HANDBOOK_STAGE_PATH = gamedata_path / "excel" / "handbook_info_table.json"


async def _name_code_swap(
        value: str,
        swap_file: Path,
        source_file: Path,
        type_: str = "name2code",
        *,
        layer: tuple = (0, None),
        name_key: str = "name",
        code_key: str = None,
        data: Union[Dict, List] = None
):
    """
    草，写了一坨屎山参数，自己都看不懂了

    :param value: 值
    :param swap_file: 保存的映射文件名
    :param source_file: 源文件
    :param type_: name2code / code2name
    :param layer: 有些源文件不是一层映射，如 arknights_item_table，需要向深 1 层进入 "items"，对应 (1, "items")
    :param name_key: 有些源文件表示名字的键不叫 name，如 uniequip_table 的叫 "subProfessionName",
    :param code_key: 有些文件要转换的代码名不是键名，如 handbook_stage 的在值中，名为 code
    :param data: 没有源文件的，直接用data写入
    :return:
    """
    if not value:
        return ""

    if swap_file.exists():
        async with aopen(swap_file, "r", encoding="utf-8") as fp:
            mapping = json.loads(await fp.read())
        return mapping[type_].get(value, value)

    if data:
        async with aopen(swap_file, "w", encoding="utf-8") as fp:
            await fp.write(json.dumps(data, ensure_ascii=False))
        return data[type_].get(value, value)

    os.makedirs(swap_file.parent, exist_ok=True)
    mapping = {"name2code": {}, "code2name": {}}
    async with aopen(source_file, "r", encoding="utf-8") as fp:
        data = json.loads(await fp.read())
    for i in range(layer[0]):
        data = data[layer[i+1]]

    codes = [_[code_key] for _ in data.values()] if code_key else list(data.keys())
    names = [_[name_key] for _ in data.values()]
    mapping["name2code"] = dict(zip(names, codes))
    mapping["code2name"] = dict(zip(codes, names))
    async with aopen(swap_file, "w", encoding="utf-8") as fp:
        await fp.write(json.dumps(mapping, ensure_ascii=False))

    return mapping[type_].get(value, value)


async def character_swap(value: str, type_: str = "name2code") -> str:
    """干员的名字-id互相查询，默认名字查id"""
    swap_file = SWAP_PATH / "character_swap.json"
    source_file = CHARACTER_FILE
    return await _name_code_swap(value, swap_file, source_file, type_)


async def item_swap(value: str, type_: str = "name2code") -> str:
    """物品的名字-id互相查询，默认名字查id"""
    swap_file = SWAP_PATH / "item_swap.json"
    source_file = ITEM_FILE
    return await _name_code_swap(value, swap_file, source_file, type_, layer=(1, "items"))


async def sub_prof_swap(value: str, type_: str = "name2code") -> str:
    """子职业的名字-id互相查询，默认名字查id"""
    swap_file = SWAP_PATH / "sub_prof_swap.json"
    source_file = SUB_PROF_FILE
    return await _name_code_swap(value, swap_file, source_file, type_, layer=(1, "subProfDict"), name_key="subProfessionName")


async def equip_swap(value: str, type_: str = "name2code") -> str:
    """模组的名字-id互相查询，默认名字查id"""
    swap_file = SWAP_PATH / "equip_swap.json"
    source_file = EQUIP_FILE
    return await _name_code_swap(value, swap_file, source_file, type_, layer=(1, "equipDict"), name_key="uniEquipName")


async def faction_swap(value: str, type_: str = "name2code") -> str:
    """阵营的名字-id互相查询，默认名字查id"""
    swap_file = SWAP_PATH / "faction_swap.json"
    source_file = TEAM_FILE
    return await _name_code_swap(value, swap_file, source_file, type_, name_key="powerName")


async def prof_swap(value: str, type_: str = "name2code") -> str:
    """职业的名字-id互相查询，默认名字查id"""
    data = {
        "name2code": {
            "先锋干员": "PIONEER",
            "近卫干员": "WARRIOR",
            "狙击干员": "SNIPER",
            "治疗干员": "MEDIC",
            "重装干员": "TANK",
            "术师干员": "CASTER",
            "辅助干员": "SUPPORT",
            "特种干员": "SPECIAL"
        },
        "code2name": {
            "PIONEER": "先锋干员",
            "WARRIOR": "近卫干员",
            "SNIPER": "狙击干员",
            "MEDIC": "治疗干员",
            "TANK": "重装干员",
            "CASTER": "术师干员",
            "SUPPORT": "辅助干员",
            "SPECIAL": "特种干员"
        }
    }
    return data[type_][value]


async def gacha_rule_swap(value: str, type_: str = "name2code") -> str:
    """池子类型"""
    data = {
        "name2code": {
            "春节": "ATTAIN",
            "限定": "LIMITED",
            "联动": "LINKAGE",
            "普通": "NORMAL"
        },
        "code2name": {
            "ATTAIN": "春节",
            "LIMITED": "限定",
            "LINKAGE": "联动",
            "NORMAL": "普通"
        }
    }
    return data[type_][value]


async def stage_swap(value: str, type_: str = "name2code") -> str:
    """关卡的名字-id互相查询，默认名字查id"""
    swap_file = SWAP_PATH / "stage_swap.json"
    source_file = STAGE_PATH
    return await _name_code_swap(value, swap_file, source_file, type_, layer=(1, "stages"))


async def handbook_stage_swap(value: str, type_: str = "name2code") -> str:
    """悖论模拟的名字-id互相查询，默认名字查id"""
    swap_file = SWAP_PATH / "handbook_stage_swap.json"
    source_file = HANDBOOK_STAGE_PATH
    return await _name_code_swap(value, swap_file, source_file, type_, layer=(1, "handbookStageData"), code_key="code")


async def nickname_swap(value: str) -> str:
    """干员昵称/外号转换"""
    swap_file = SWAP_PATH / "nicknames.json"
    async with aopen(swap_file, "r", encoding="utf-8") as fp:
        data = json.loads(await fp.read())

    for k, v in data.items():
        if value == k or value in v:
            logger.info(f"{value} -> {k}")
            return k
    return value


async def get_recruitment_available() -> List[str]:
    """获取可以公招获取的干员id们"""
    async with aopen(GACHA_PATH, "r", encoding="utf-8") as fp:
        text = json.loads(await fp.read())["recruitDetail"]

    # 处理这堆字
    text = text.replace("\\n", "\n").replace("<@rc.eml>", "\n").replace("</>", "\n").split("\n")
    text = [_ for _ in text if _ and "<" not in _ and "--" not in _ and "★" not in _ and _ != " / "][1:]
    text = [" ".join(_.split(" / ")) for _ in text]
    text = " ".join(_.strip() for _ in text).split()
    result = [await character_swap(_) for _ in text]
    return result


__all__ = [
    "character_swap",
    "item_swap",
    "sub_prof_swap",
    "equip_swap",
    "prof_swap",
    "faction_swap",
    "gacha_rule_swap",
    "stage_swap",
    "handbook_stage_swap",

    "nickname_swap",

    "get_recruitment_available"
]
