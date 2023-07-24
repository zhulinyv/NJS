import io
import os
import sys
from pathlib import Path
from time import sleep
from typing import Callable, List
from zipfile import ZipFile

import rarfile
from nonebot.log import logger
from pyunpack import Archive
from rarfile import RarFile

from ..l4d2_utils.config import systems
from ..l4d2_utils.utils import get_file, get_vpk


async def updown_l4d2_vpk(map_paths: Path, name: str, url: str):
    """从url下载压缩包并解压到位置"""
    original_vpk_files = get_vpk(map_paths)
    down_file = Path(map_paths, name)
    if await get_file(url, down_file) == None:
        return None
    sleep(1)
    msg = open_packet(name, down_file)
    logger.info(msg)

    sleep(1)
    extracted_vpk_files = get_vpk(map_paths)
    # 获取新增vpk文件的list
    vpk_files = list(set(extracted_vpk_files) - set(original_vpk_files))
    return vpk_files


import zipfile
from pathlib import Path
from typing import Dict

import rarfile
from pyunpack import Archive

SUPPORTED_EXTENSIONS = (".zip", ".7z", ".rar")


def unzip_zipfile(down_file: Path, down_path: Path):
    """解压zip文件"""
    with support_gbk(zipfile.ZipFile(down_file, "r")) as z:
        z.extractall(down_path)
    os.remove(down_file)


def unpack_7zfile(down_file: Path, down_path: Path):
    """解压7z文件"""
    Archive(str(down_file)).extractall(str(down_path))
    os.remove(down_file)


def unpack_rarfile(down_file: Path, down_path: Path):
    """解压rar文件"""
    with rarfile.RarFile(down_file, "r") as z:
        z.extractall(down_path)
    os.remove(down_file)


def open_packet(name: str, down_file: Path) -> str:
    """解压压缩包"""
    down_path = down_file.parent
    logger.info("文件名为：" + name)
    logger.info(f"系统为{systems}")

    if name.endswith(".vpk"):
        return "vpk文件已下载"

    for ext in SUPPORTED_EXTENSIONS:
        if name.endswith(ext):
            mes = f"{ext[1:]}文件已下载,正在解压"
            unpack_funcs: Dict[str, Callable] = {
                ".zip": unzip_zipfile,
                ".7z": unpack_7zfile,
                ".rar": unpack_rarfile,
            }
            unpack_func = unpack_funcs.get(ext, None)
            if not unpack_func:
                raise ValueError(f"不支持的拓展名: {ext}")
            unpack_func(down_file, down_path)
            return mes

    raise ValueError(f"不支持的文件: {name}")


def support_gbk(zip_file: ZipFile):
    """
    压缩包中文恢复
    """
    if type(zip_file) == ZipFile:
        name_to_info = zip_file.NameToInfo
        # copy map first
        for name, info in name_to_info.copy().items():
            real_name = name.encode("cp437").decode("gbk")
            if real_name != name:
                info.filename = real_name
                del name_to_info[name]
                name_to_info[real_name] = info
    return zip_file


async def all_zip_to_one(data_list: List[bytes]):
    """多压缩包文件合并"""
    file_list = [io.BytesIO(data).getbuffer() for data in data_list]
    data_file = io.BytesIO()

    with ZipFile(data_file, mode="w") as zf:
        for i, file in enumerate(file_list):
            filename = f"file{i}.zip"
            zf.writestr(filename, file)

    return data_file.getbuffer()
