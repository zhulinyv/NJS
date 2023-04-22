import nonebot
from pathlib import Path
from . import animalvoice_main,cheru_main

_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "plugins").
    resolve()))