"""杂七杂八小功能"""
import contextlib
from pathlib import Path

from nonebot import on_command
from nonebot import require, get_bot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, Bot, MessageSegment
import aiofiles
import time
import json
import os

scheduler = require("nonebot_plugin_apscheduler").scheduler
san_recover = on_command("方舟理智恢复", aliases={"方舟理智记录", "方舟理智提醒", "理智恢复", "理智记录", "理智提醒"})
my_san = on_command("我的理智", aliases={"查看理智"})


@san_recover.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    # sourcery skip: dict-assign-update-to-union
    None if (Path(__file__).parent.parent.absolute() / "_data" / "operator_info").exists() else os.makedirs( Path(__file__).parent.parent.absolute() / "_data" / "operator_info")
    tmp_file = (Path(__file__).parent.parent.absolute() / "_data" / "san_check.json")
    start_time = int(time.time())
    arg: list = arg.extract_plain_text().strip().split()
    now_san, goal_san = 0, 135
    if len(arg) == 1:  # 只有现在理智
        now_san = int(arg[0])
    elif len(arg) == 2:
        now_san, goal_san = int(arg[0]), int(arg[1])
    data_ = {
        f"{event.user_id}": {
            "uid": event.user_id,
            "start": start_time,
            "end": (goal_san - now_san) * 360 + start_time,
            "now": now_san,
            "goal": goal_san,
            "group": event.group_id
        }
    }
    async with aiofiles.open(tmp_file, "r", encoding="utf-8") as fp:
        with contextlib.suppress(json.JSONDecodeError):
            data_.update(json.loads(await fp.read()))

    async with aiofiles.open(tmp_file, "w", encoding="utf-8") as fp:
        await fp.write(str(data_).replace("'", '"'))
    await san_recover.finish(
        f"记录成功！将在 {(goal_san - now_san) * 6} 分钟后提醒你",
        at_sender=True
    )


@my_san.handle()
async def _(event: GroupMessageEvent):
    # sourcery skip: dict-assign-update-to-union
    uid = event.user_id
    now = int(time.time())
    None if (Path(__file__).parent.parent.absolute() / "_data" / "operator_info").exists() else os.makedirs( Path(__file__).parent.parent.absolute() / "_data" / "operator_info")
    tmp_file = (Path(__file__).parent.parent.absolute() / "_data" / "san_check.json")
    if not tmp_file.exists():
        await my_san.finish("小笨蛋，你还没有设置过理智提醒哦！", at_sender=True)

    data_ = {}
    async with aiofiles.open(tmp_file, "r", encoding="utf-8") as fp:
        with contextlib.suppress(json.JSONDecodeError):
            data_.update(json.loads(await fp.read()))
    if not data_ or str(uid) not in data_:
        await my_san.finish("小笨蛋，你还没有设置过理智提醒哦！", at_sender=True)

    start = data_[uid]["start"]
    end = data_[uid]["end"]
    await my_san.finish(f"你现在的理智已经恢复到了 {(now - start) / 360 + data_['now']} 哦！", at_sender=True)


@scheduler.scheduled_job(
    "interval",
    seconds=10
)
async def _():
    try:
        bot: Bot = get_bot()
    except ValueError:
        return
    if not bot:
        return

    now = time.time()
    data = None
    None if (Path(__file__).parent.parent.absolute() / "_data" / "operator_info").exists() else os.makedirs( Path(__file__).parent.parent.absolute() / "_data" / "operator_info")
    tmp_file = (Path(__file__).parent.parent.absolute() / "_data" / "san_check.json")
    if not tmp_file.exists():
        return
    async with aiofiles.open(tmp_file, "r", encoding="utf-8") as fp:
        with contextlib.suppress(json.JSONDecodeError):
            data = json.loads(await fp.read())
    if not data:
        return
    data_copy = {}
    for uid, value in data.items():
        if now < float(value["end"]):
            data_copy[uid] = value
            continue
        await bot.send_group_msg(
            group_id=value["group"],
            message=Message(f"{MessageSegment.at(value['uid'])} 你的理智已经回到 {value['goal']} 了！")
        )
    async with aiofiles.open(tmp_file, "w", encoding="utf-8") as fp:
        await fp.write(str(data_copy).replace("'", '"'))