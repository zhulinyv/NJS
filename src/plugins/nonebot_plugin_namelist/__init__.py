from pathlib import Path
from typing import Literal

from nonebot import get_driver, logger, on_fullmatch, on_startswith
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.permission import SUPERUSER

try:
    import ujson as json
except ModuleNotFoundError:
    import json

superusers = get_driver().config.superusers

file_path = Path(__file__).parent / "namelist.json"

namelist = (
    json.loads(file_path.read_text("utf-8"))
    if file_path.is_file()
    else {"type": "blacklist", "blacklist": [], "whitelist": []}
)


def is_blacklist() -> bool:
    return namelist["type"] == "blacklist"


def save_namelist() -> None:
    file_path.write_text(json.dumps(namelist), encoding="utf-8")


def handle_namelist(
    event: MessageEvent,
    type: Literal["blacklist", "whitelist"],
    mode: Literal["add", "del"],
) -> str:
    msg = event.get_message()
    uids = [at.data["qq"] for at in msg["at"]]
    if mode == "add":
        namelist[type].extend(uids)
        _mode = "添加"
    elif mode == "del":
        namelist[type] = [uid for uid in namelist[type] if uid not in uids]
        _mode = "删除"
    save_namelist()
    _type = "黑名单" if type == "blacklist" else "白名单"
    return f"已{_mode} {len(uids)} 个{_type}用户: {', '.join(uids)}"


@event_preprocessor
def namelist_processor(event: MessageEvent):
    uid = str(event.user_id)
    if uid in superusers:
        return
    if is_blacklist() and uid in namelist["blacklist"]:
        logger.debug(f"用户 {uid} 在黑名单中, 忽略本次消息")
        raise IgnoredException("黑名单用户")
    elif not (is_blacklist() or uid in namelist["whitelist"]):
        logger.debug(f"用户 {uid} 不在白名单中, 忽略本次消息")
        raise IgnoredException("非白名单用户")


add_blacklist = on_startswith(("拉黑", "添加黑名单"), permission=SUPERUSER)


@add_blacklist.handle()
async def add_black_list(event: MessageEvent):
    msg = handle_namelist(event, "blacklist", "add")
    await add_blacklist.send(msg)


add_whitelist = on_startswith(("添加白名单"), permission=SUPERUSER)


@add_whitelist.handle()
async def add_white_list(event: MessageEvent):
    msg = handle_namelist(event, "whitelist", "add")
    await add_whitelist.send(msg)


del_blacklist = on_startswith(("删除黑名单", "解除黑名单"), permission=SUPERUSER)


@del_blacklist.handle()
async def del_black_list(event: MessageEvent):
    msg = handle_namelist(event, "blacklist", "del")
    await del_blacklist.send(msg)


del_whitelist = on_startswith(("删除白名单", "解除白名单"), permission=SUPERUSER)


@del_whitelist.handle()
async def del_white_list(event: MessageEvent):
    msg = handle_namelist(event, "whitelist", "del")
    await del_whitelist.send(msg)


check_blacklist = on_startswith(("查看黑名单", "查看黑名单用户"), permission=SUPERUSER)


@check_blacklist.handle()
async def check_black_list():
    await check_blacklist.send(f"当前黑名单用户: {', '.join(namelist['blacklist'])}")


check_whitelist = on_startswith(("查看白名单", "查看白名单用户"), permission=SUPERUSER)


@check_whitelist.handle()
async def check_white_list():
    await check_whitelist.send(f"当前白名单用户: {', '.join(namelist['whitelist'])}")


change_namelist = on_fullmatch(
    ("切换黑名单", "更改黑名单", "切换白名单", "更改白名单", "切换名单"), permission=SUPERUSER
)


@change_namelist.handle()
async def change_black_list():
    namelist["type"] = "whitelist" if is_blacklist() else "blacklist"
    save_namelist()
    await change_namelist.send(f'已切换为 {"黑名单" if is_blacklist() else "白名单"} 模式')
