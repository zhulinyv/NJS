import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

import httpx
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent
from nonebot.log import logger
from nonebot.matcher import Matcher

from ..l4d2_anne import anne_message, del_player, write_player
from ..l4d2_image.steam import url_to_byte
from ..l4d2_server.rcon import rcon_server, read_server_cfg_rcon
from ..l4d2_server.workshop import workshop_to_dict
from .config import *
from .rule import *
from .txt_to_img import mode_txt_to_img


async def get_file(url: str, down_file: Path):
    """
    下载指定Url到指定位置
    """
    try:
        if l4_config.l4_only:
            maps = await url_to_byte(url)
        else:
            maps = httpx.get(url).content
        logger.info("已获取文件，尝试新建文件并写入")
        if maps:
            with open(down_file, "wb") as mfile:
                mfile.write(maps)
            logger.info("下载成功")
            return "文件已下载，正在解压"
    except Exception as e:
        logger.info(f"文件获取不到/已损坏:原因是{e}")
        return None


def get_vpk(map_path: Path, file_: str = ".vpk") -> List[str]:
    """
    获取路径下所有vpk文件名，并存入vpk_list列表中
    """
    vpk_list: List[str] = [str(file) for file in map_path.glob(f"*{file_}")]
    return vpk_list


def mes_list(mes: str, name_list: List[str]) -> str:
    if name_list:
        for idx, name in enumerate(name_list):
            mes += f"\n{idx+1}、{name}"
    return mes


def del_map(num: int, map_path: Path) -> str:
    """
    删除指定的地图
    """
    map = get_vpk(map_path)
    map_name = map[num - 1]
    del_file = map_path / map_name
    os.remove(del_file)
    return map_name


def rename_map(num: int, rename: str, map_path: Path) -> str:
    """
    改名指定的地图
    """
    map = get_vpk(map_path)
    map_name = map[num - 1]
    old_file = map_path / map_name
    new_file = map_path / rename
    os.rename(old_file, new_file)
    logger.info("改名成功")
    return map_name


def solve(msg: str):
    """删除str最后一行"""
    lines = msg.splitlines()
    lines.pop()
    return "\n".join(lines)


async def search_anne(name: str, usr_id: str):
    """获取anne成绩"""
    return await anne_message(name, usr_id)


async def bind_steam(id: str, msg: str, nickname: str):
    """绑定qq-steam"""
    return await write_player(id, msg, nickname)


def name_exist(id: str):
    """删除绑定信息"""
    return del_player(id)


async def get_message_at(datas: str) -> List[int]:
    data: Dict[str, Any] = json.loads(datas)
    return [int(msg["data"]["qq"]) for msg in data["message"] if msg["type"] == "at"]


def at_to_usrid(at: List[int]):
    return at[0] if at else None


async def rcon_command(rcon, cmd):
    return await rcon_server(rcon, cmd.strip())


async def command_server(msg: str):
    rcon = await read_server_cfg_rcon()
    msg = await rcon_command(rcon, msg)
    if not msg:
        msg = "你可能发送了一个无用指令，或者换图导致服务器无响应"
    elif msg.startswith("Unknown command"):
        msg = "无效指令：" + msg.replace("Unknown command", "").strip()
    return msg.strip().replace("\n", "")


async def workshop_msg(msg: str):
    """url变成id，拼接post请求"""
    if msg.startswith("https://steamcommunity.com/sharedfiles/filedetails/?id"):
        try:
            msg = msg.split("&")[0]
        except:
            pass
        msg = msg.replace("https://steamcommunity.com/sharedfiles/filedetails/?id=", "")
    if msg.isdigit():
        data: Union[dict, List[dict]] = await workshop_to_dict(msg)
        return data
    else:
        return None


async def save_file(file: bytes, path_name):
    """保存文件"""
    with open(path_name, "wb") as files:
        files.write(file)


async def upload_file(bot: Bot, event: MessageEvent, file_data: bytes, filename: str):
    """上传临时文件"""
    if systems == "win" or "other":
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(Path(temp_dir) / filename, "wb") as f:
                f.write(file_data)
            if isinstance(event, GroupMessageEvent):
                await bot.call_api(
                    "upload_group_file",
                    group_id=event.group_id,
                    file=f.name,
                    name=filename,
                )
            else:
                await bot.call_api(
                    "upload_private_file",
                    user_id=event.user_id,
                    file=f.name,
                    name=filename,
                )
        os.remove(Path().joinpath(filename))
    elif systems == "linux":
        with tempfile.NamedTemporaryFile("wb+") as f:
            f.write(file_data)
            if isinstance(event, GroupMessageEvent):
                await bot.call_api(
                    "upload_group_file",
                    group_id=event.group_id,
                    file=f.name,
                    name=filename,
                )
            else:
                await bot.call_api(
                    "upload_private_file",
                    user_id=event.user_id,
                    file=f.name,
                    name=filename,
                )


sub_menus = []


def register_menu_func(
    func: str,
    trigger_condition: str,
    brief_des: str,
    trigger_method: str = "指令",
    detail_des: Optional[str] = None,
):
    sub_menus.append(
        {
            "func": func,
            "trigger_method": trigger_method,
            "trigger_condition": trigger_condition,
            "brief_des": brief_des,
            "detail_des": detail_des or brief_des,
        }
    )


def register_menu(*args, **kwargs):
    def decorator(f):
        register_menu_func(*args, **kwargs)
        return f

    return decorator


async def extract_last_digit(msg: str) -> tuple[str, str]:
    "分离str和数字"
    for i in range(len(msg) - 1, -1, -1):
        if msg[i].isdigit():
            last_digit = msg[i]
            new_msg = msg[:i]
            return new_msg, last_digit
    return msg, ""


async def str_to_picstr(push_msg: str, matcher: Matcher, keyword: Optional[str] = None):
    """判断图片输出还是正常输出"""
    if l4_config.l4_image:
        lines = push_msg.splitlines()
        first_str = lines[0]
        last_str = lines[-1]
        push_msg = "\n".join(lines[1:-1])
        if l4_config.l4_connect:
            await matcher.finish(mode_txt_to_img(first_str, push_msg, last_str))
        else:
            await matcher.finish(mode_txt_to_img(first_str, push_msg))
    else:
        if l4_config.l4_connect or keyword == "connect":
            await matcher.send(push_msg)
        else:
            await matcher.send("\n".join(push_msg.splitlines()[1:-2]))


def split_maohao(msg: str) -> List[str]:
    """分割大小写冒号"""
    if ":" in msg:
        msgs: List[str] = msg.split(":")
    elif "：" in msg:
        msgs: List[str] = msg.split("：")
    elif msg.replace(".", "").isdigit():
        msgs: List[str] = [msg, "20715"]
    else:
        msgs = []
    mse = [msgs[0], msgs[-1]]
    return mse
