"""数据库相关"""
from pathlib import Path

import tortoise.exceptions
from tortoise import Tortoise
from aiofiles import open as aopen
import json
import asyncio
import re
from aiofiles import os as aos
from nonebot import get_driver, logger

from ..configs.path_config import PathConfig
from ..core.database import *


driver = get_driver()
pcfg = PathConfig.parse_obj(driver.config.dict())
db_url = Path(pcfg.arknights_db_url).absolute()
gamedata_path = Path(pcfg.arknights_gamedata_path).absolute()
# pcfg = PathConfig()

class ArknightsDB:
    """初始化"""
    @staticmethod
    async def init_db():
        """建库，建表"""
        logger.info("##### ARKNIGHTS-SQLITE CONNECTING ...")
        await aos.makedirs(db_url.parent, exist_ok=True)
        await Tortoise.init(
            {
                "connections": {
                    "arknights": {
                        "engine": "tortoise.backends.sqlite",
                        "credentials": {
                            "file_path": f"{db_url}"
                        }
                    }
                },
                "apps": {
                    "arknights": {
                        "models": [
                            f"{GAME_SQLITE_MODEL_MODULE_NAME}",
                            f"{PLUGIN_SQLITE_MODEL_MODULE_NAME}"
                        ],
                        "default_connection": "arknights"
                    }
                },
                "timezone": "Asia/Shanghai"
            }
        )
        logger.info("===== ARKNIGHTS-SQLITE CONNECTED.")
        await Tortoise.generate_schemas(safe=True)
        await ArknightsDB.init_data()

    @staticmethod
    async def close_connection():
        logger.info("##### ARKNIGHTS-SQLITE CONNECTION CLOSING ...")
        await Tortoise.close_connections()
        logger.info("===== ARKNIGHTS-SQLITE CONNECTION CLOSED.")

    @staticmethod
    async def init_data():
        """填充数据"""
        logger.info("##### ARKNIGHTS-SQLITE DATA ALL INITIATING ...")
        await ArknightsDB._init_building_buff()
        await ArknightsDB._init_character()
        await ArknightsDB._init_constance()
        await ArknightsDB._init_equip()
        await ArknightsDB._init_gacha_pool()
        await ArknightsDB._init_handbook_info()
        await ArknightsDB._init_item()
        await ArknightsDB._init_skill()
        await ArknightsDB._init_skin()
        logger.info("===== ARKNIGHTS-SQLITE DATA ALL INITIATED")

    @staticmethod
    async def _init_building_buff():
        async with aopen(gamedata_path / "excel" / "building_data.json", "r", encoding="utf-8") as fp:
            data = await fp.read()
        data = json.loads(data)
        buff_data = data["buffs"]
        tasks = {
            BuildingBuffModel.update_or_create(**v)
            for k, v in buff_data.items()
        }
        await asyncio.gather(*tasks)
        logger.info("\t- BuildingBuff data initiated.")
        await ArknightsDB._init_building_workshop_formula(data)

    @staticmethod
    async def _init_building_workshop_formula(data: dict):
        data = data["workshopFormulas"]
        tasks = {
            WorkshopFormulaModel.update_or_create(**v)
            for _, v in data.items()
        }
        await asyncio.gather(*tasks)
        logger.info("\t- WorkshopFormula data initiated.")

    @staticmethod
    async def _init_character():
        async with aopen(gamedata_path / "excel" / "character_table.json", "r", encoding="utf-8") as fp:
            data = await fp.read()
        async with aopen(gamedata_path / "excel" / "char_patch_table.json", "r", encoding="utf-8") as fp:
            data_ = await fp.read()
        data = json.loads(data)
        data_ = json.loads(data_)["patchChars"]
        data_["char_1001_amiya2"]["name"] = "近卫阿米娅"
        data.update(data_)

        amiya = await CharacterModel.filter(charId="char_1001_amiya2", name='阿米娅').first()
        if amiya:
            await amiya.delete()

        tasks = {
            CharacterModel.update_or_create(charId=k, **v)
            for k, v in data.items()
        }
        await asyncio.gather(*tasks)
        logger.info("\t- Character data initiated.")

    @staticmethod
    async def _init_constance():
        async with aopen(gamedata_path / "excel" / "gamedata_const.json", "r", encoding="utf-8") as fp:
            data = await fp.read()
        data = json.loads(data)
        tasks = {
            ConstanceModel.update_or_create(
                maxLevel=data["maxLevel"],
                characterExpMap=data["characterExpMap"],
                characterUpgradeCostMap=data["characterUpgradeCostMap"],
                evolveGoldCost=data["evolveGoldCost"],
                attackMax=data["attackMax"],
                defMax=data["defMax"],
                hpMax=data["hpMax"],
                reMax=data["reMax"],
            )
        }
        await asyncio.gather(*tasks)
        logger.info("\t- Constance data initiated.")

        await ArknightsDB._init_constance_rich_text_style(data)
        await ArknightsDB._init_constance_term_description(data)

    @staticmethod
    async def _init_constance_rich_text_style(data: dict):
        tasks = {
            RichTextStyleModel.update_or_create(text=k, style=v)
            for k, v in data["richTextStyles"].items()
        }
        await asyncio.gather(*tasks)
        logger.info("\t\t- RichTextStyle data initiated.")

    @staticmethod
    async def _init_constance_term_description(data: dict):
        tasks = {
            TermDescriptionModel.update_or_create(**v)
            for k, v in data["termDescriptionDict"].items()
        }
        await asyncio.gather(*tasks)
        logger.info("\t\t- TermDescription data initiated.")

    @staticmethod
    async def _init_equip():
        async with aopen(gamedata_path / "excel" / "uniequip_table.json", "r", encoding="utf-8") as fp:
            data = await fp.read()
        data = json.loads(data)
        equip_dict = data["equipDict"]
        mission_list = data["missionList"]
        char_equip = data["charEquip"]
        tasks: set = {
            EquipModel.update_or_create(**v)
            for k, v in equip_dict.items()
        }
        await asyncio.gather(*tasks)

        tasks = {
            EquipModel.filter(uniEquipId=v["uniEquipId"]).update(**v)
            for k, v in mission_list.items()
        }
        await asyncio.gather(*tasks)

        tasks = set()
        for k, v in char_equip.items():
            tasks = tasks.union({
                EquipModel.filter(uniEquipId=i).update(character=k)
                for i in v
            })

        await asyncio.gather(*tasks)
        logger.info("\t- Equip data initiated")

    @staticmethod
    async def _init_gacha_pool():
        async with aopen(gamedata_path / "excel" / "gacha_table.json", "r", encoding="utf-8") as fp:
            data = await fp.read()
        data = json.loads(data)["gachaPoolClient"]
        tasks = {
            GachaPoolModel.update_or_create(**pool)
            for pool in data
        }
        await asyncio.gather(*tasks)
        logger.info("\t- GachaPool data initiated")

    @staticmethod
    async def _init_handbook_info():
        async with aopen(gamedata_path / "excel" / "handbook_info_table.json", "r", encoding="utf-8") as fp:
            data = await fp.read()
        data = json.loads(data)["handbookDict"]
        tasks = {
            HandbookInfoModel.update_or_create(
                infoId=k,
                sex=re.findall(r"性别】\s*(.*?)\s*\n", v["storyTextAudio"][0]["stories"][0]["storyText"])[0].strip(),
                **v
            )
            for k, v in data.items()
            if "npc_" not in k
        }
        await asyncio.gather(*tasks)
        logger.info("\t- HandbookInfo data initiated.")

    @staticmethod
    async def _init_item():
        async with aopen(gamedata_path / "excel" / "item_table.json", "r", encoding="utf-8") as fp:
            data = await fp.read()
        data = json.loads(data)["items"]
        tasks = {
            ItemModel.update_or_create(**v)
            for _, v in data.items()
        }
        await asyncio.gather(*tasks)
        logger.info("\t- Item data initiated")

    @staticmethod
    async def _init_skill():
        async with aopen(gamedata_path / "excel" / "skill_table.json", "r", encoding="utf-8") as fp:
            data = await fp.read()
        data = json.loads(data)
        tasks = {
            SkillModel.update_or_create(
                name=v["levels"][0]["name"],
                skillType=v["levels"][0]["skillType"],
                durationType=v["levels"][0]["skillType"],
                prefabId=v["levels"][0]["prefabId"],
                **v
            )
            for _, v in data.items()
        }
        await asyncio.gather(*tasks)
        logger.info("\t- Skill data initiated")

    @staticmethod
    async def _init_skin():
        async with aopen(gamedata_path / "excel" / "skin_table.json", "r", encoding="utf-8") as fp:
            data = await fp.read()
        data = json.loads(data)["charSkins"]
        tasks = {
            SkinModel.update_or_create(**v)
            for _, v in data.items()
        }
        await asyncio.gather(*tasks)
        logger.info("\t- Skin data initiated")


@driver.on_bot_connect  # 不能 on_startup, 要先下资源再初始化数据库
async def _init_db():
    try:
        await ArknightsDB.init_db()
    except FileNotFoundError as e:
        logger.error("初始化数据库失败：所需的数据文件未找到，请手动下载:")
        logger.error("https://github.com/NumberSir/nonebot_plugin_arktools#%E5%90%AF%E5%8A%A8%E6%B3%A8%E6%84%8F")
        logger.warning("***** ARKNIGHTS-SQLITE DATA INITIATING FAILED")
    except tortoise.exceptions.BaseORMException as e:
        logger.error("初始化数据库失败：请检查是否与其它使用 Tortoise-ORM 的插件初始化冲突")
        logger.warning("***** ARKNIGHTS-SQLITE CONNECTING FAILED")

@driver.on_bot_disconnect
async def _close_db():
    await ArknightsDB.close_connection()


__all__ = [
    "ArknightsDB",

    "_init_db",
    "_close_db"
]

