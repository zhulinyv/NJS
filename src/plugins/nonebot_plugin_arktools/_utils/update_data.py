"""更新数据"""
from pathlib import Path

import httpx
from nonebot import require
from .http_utils import async_get
from aiofiles import open
from aiofiles import os
from nonebot import on_command
from nonebot import logger
from nonebot import get_driver
from urllib.parse import quote

from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message


IMAGE_DIRS = {
    "avatar", "item", "skill", "skin",
    "elite", "equip"
}
JSON_FILES = {
    "character_table.json",
    "gacha_table.json",
    "handbook_info_table.json",
    "item_table.json",
    "skill_table.json",
    "uniequip_table.json"
}


update = on_command("更新方舟游戏数据")
driver = get_driver()


@driver.on_bot_connect
async def _():
    flag, version = await is_game_data_update()
    if flag:
        try:
            await download_game_data()
        except Exception as e:
            logger.error(f"方舟游戏数据更新出错: {e}")
        else:
            logger.debug("方舟游戏数据更新完毕！")
            await write_in_version(version)
    else:
        logger.debug("方舟游戏数据当前为最新！")


@update.handle()
async def _(arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    flag, version = await is_game_data_update()
    if arg and arg == "-f":  # 强制更新
        flag = True
    if flag:
        await update.send("开始更新方舟游戏数据，视网络情况可能需要20~30分钟，如果中途出错可以重新输入指令从断点处继续下载")
        try:
            await download_game_data()
        except Exception as e:
            logger.error(f"方舟游戏数据更新出错: {e}")
        else:
            await update.finish("方舟游戏数据更新完毕！")
            await write_in_version(version)
    else:
        await update.finish("方舟游戏数据当前为最新！")

scheduler = require("nonebot_plugin_apscheduler").scheduler
@scheduler.scheduled_job(
    "cron",
    hour=4,
    minute=30,
)
async def check_update():
    flag, version = await is_game_data_update()
    if flag:
        try:
            await download_game_data()
        except Exception as e:
            logger.error(f"方舟游戏数据更新出错: {e}")
        else:
            logger.debug("方舟游戏数据更新完毕！")
            await write_in_version(version)
    else:
        logger.debug("方舟游戏数据当前为最新！")


async def is_game_data_update():
    """T 更新, F 不更新"""
    logger.debug("开始检查方舟游戏数据更新...")
    version = (await async_get(url="https://ghproxy.com/https://raw.githubusercontent.com/yuanyan3060/Arknights-Bot-Resource/main/version")).text

    local_version = Path(__file__).parent.parent / "_data" / "version.txt"
    if not local_version.exists():
        return True, version
    async with open(local_version, "r") as f:
        local_version = await f.read()
    return (local_version != version, version) if local_version else (True, version)


async def write_in_version(version: str):
    local_version = Path(__file__).parent.parent / "_data" / "version.txt"
    async with open(local_version, "w") as f:
        await f.write(version)


async def init_dir():
    test_dirs = set()
    test_dirs.update({Path(__file__).parent.parent / "_data" / "operator_info" / "json"})
    test_dirs.update({Path(__file__).parent.parent / "_data" / "operator_info" / "font"})
    test_dirs.update({Path(__file__).parent.parent / "_data" / "operator_info" / "image" / _ for _ in IMAGE_DIRS})
    for d in test_dirs:
        if not d.exists():
            await os.makedirs(d)


# @retry(attempts=5, delay=3)
async def download_game_data():
    await init_dir()
    logger.debug("开始更新方舟游戏数据，视网络情况可能需要20~30分钟，如果中途出错可以重新输入指令从断点处继续下载")

    async with open(file=Path(__file__).parent.parent / "_data" / "operator_info" / "json" / "recruitment_tags.json", mode="wb") as fp:
        await fp.write(recruitment_tags.encode("utf-8"))

    try:
        async with httpx.AsyncClient() as client:
            all_files: dict = (await client.get(url="https://ghproxy.com/https://raw.githubusercontent.com/yuanyan3060/Arknights-Bot-Resource/main/file_dict.json")).json()

            for font in {"Arknights-en.ttf", "Arknights-zh.otf"}:
                font_cont = (await client.get(url=f"https://ghproxy.com/https://raw.githubusercontent.com/NumberSir/nonebot_plugin_arktools/main/nonebot_plugin_arktools/_data/operator_info/font/{font}")).content
                async with open(Path(__file__).parent.parent / "_data" / "operator_info" / "font" / font, "wb") as fp:
                    await fp.write(font_cont)
                    logger.debug(f"字体下载完成 {font}")

            for lvl in {"skill_lvl1", "skill_lvl2", "skill_lvl3"}:
                lvl_cont = (await client.get(url=f"https://ghproxy.com/https://raw.githubusercontent.com/NumberSir/nonebot_plugin_arktools/main/nonebot_plugin_arktools/_data/operator_info/image/skill/{lvl}.png")).content
                async with open(Path(__file__).parent.parent / "_data" / "operator_info" / "image" / "skill" / f"{lvl}.png", "wb") as fp:
                    await fp.write(lvl_cont)
                    logger.debug(f"技能专精图标下载完成 {lvl}")

            for lvl in {"elite1", "elite2"}:
                lvl_cont = (await client.get(url=f"https://ghproxy.com/https://raw.githubusercontent.com/NumberSir/nonebot_plugin_arktools/main/nonebot_plugin_arktools/_data/operator_info/image/elite/{lvl}.png")).content
                async with open(Path(__file__).parent.parent / "_data" / "operator_info" / "image" / "elite" / f"{lvl}.png", "wb") as fp:
                    await fp.write(lvl_cont)
                    logger.debug(f"精英化图标下载完成 {lvl}")

            for lvl in {"equip_lvl1", "equip_lvl2", "equip_lvl3"}:
                lvl_cont = (await client.get(url=f"https://ghproxy.com/https://raw.githubusercontent.com/NumberSir/nonebot_plugin_arktools/main/nonebot_plugin_arktools/_data/operator_info/image/equip/{lvl}.png")).content
                async with open(Path(__file__).parent.parent / "_data" / "operator_info" / "image" / "equip" / f"{lvl}.png", "wb") as fp:
                    await fp.write(lvl_cont)
                    logger.debug(f"模组图标下载完成 {lvl}")

            for file in all_files:
                if file.split("/")[0] in IMAGE_DIRS:
                    if (Path(__file__).parent.parent / "_data" / "operator_info" / "image" / file).exists():
                        logger.debug(f"跳过图片 {file}")
                        continue
                    content = (await client.get(url=f"https://raw.githubusercontent.com/yuanyan3060/Arknights-Bot-Resource/main/{quote(file)}")).content
                    async with open(Path(__file__).parent.parent / "_data" / "operator_info" / "image" / file, "wb") as fp:
                        await fp.write(content)
                        logger.debug(f"图片下载完成 {file}")

                elif file.split("/")[-1] in JSON_FILES:
                    name = file.split("/")[-1]
                    content = (await client.get(url=f"https://ghproxy.com/https://raw.githubusercontent.com/yuanyan3060/Arknights-Bot-Resource/main/{quote(file)}")).content
                    async with open(Path(__file__).parent.parent / "_data" / "operator_info" / "json" / name, "wb") as fp:
                        await fp.write(content)
                        logger.debug(f"json下载完成 {file}")
                continue
    except Exception as e:
        logger.warning(f"更新方舟游戏数据出错: {e}")
        raise e
    logger.debug("方舟游戏数据更新完毕")

recruitment_tags = """{
    "职业": ["近卫干员", "狙击干员", "重装干员", "医疗干员", "辅助干员", "术师干员", "特种干员", "先锋干员"],
    "性别": ["男性干员", "女性干员"],
    "位置": ["近战位", "远程位"],
    "资质": ["高级资深干员", "资深干员", "支援机械", "新手"],
    "普通": ["控场", "爆发", "治疗", "支援", "费用回复", "输出", "生存", "群攻", "防护", "减速", "削弱", "快速复活", "位移", "召唤"]
}"""

