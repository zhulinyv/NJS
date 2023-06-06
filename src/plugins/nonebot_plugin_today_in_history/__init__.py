import re

from nonebot import get_bot, get_driver, on_command, require
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    MessageSegment,
    GroupMessageEvent
)
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")
from nonebot_plugin_apscheduler import scheduler

from .config import Config, PUSHDATA_ENV, HOUR_ENV, MINUTE_ENV, GROUP_ALL_ENV
from .utils import *

__plugin_meta__ = PluginMetadata(
    name="历史上的今天",
    description="发送每日历史上的今天",
    usage="指令：历史上的今天",
    config=Config
)

driver = get_driver()


@driver.on_startup
async def subscribe_jobs():
    PUSHDATA = read_json()
    PUSHDATA_ENV.update(PUSHDATA)
    write_json(PUSHDATA_ENV)
    logger.info(f"history_env: {PUSHDATA_ENV}")
    logger.info(f"history_env_all_group: {GROUP_ALL_ENV}")

    for id, times in PUSHDATA_ENV.items():
        scheduler.add_job(
            push_send,
            "cron",
            args=[id],
            id=f"history_push_{id}",
            replace_existing=True,
            hour=times["hour"],
            minute=times["minute"],
        )
        logger.debug(f"history_push_{id},{times['hour']}:{times['minute']}")

@driver.on_bot_connect
async def _(bot:Bot):
    if GROUP_ALL_ENV:
        scheduler.add_job(
            push_all_group_scheduler,
            "cron",
            args=[bot],
            id=f"history_push_group_all",
            replace_existing=True,
            hour=HOUR_ENV,
            minute=MINUTE_ENV,
        )
        logger.info(f"history_push_group_all,{HOUR_ENV}:{MINUTE_ENV}")


async def push_send(id: str):
    bot = get_bot()
    if id[0:2] == "g_":
        msg = await get_history_info("image")
        await bot.call_api("send_group_msg", group_id=int(id[2:]), message=msg)
    else:
        msg = await get_history_info("text")
        await bot.call_api("send_private_msg", user_id=id[2:], message=msg)


def calendar_subscribe(id: str, hour: int, minute: int) -> None:
    PUSHDATA_NEW = {}
    PUSHDATA_NEW.setdefault(
        id,
        {
            "hour": hour,
            "minute": minute
        }
    )
    PUSHDATA = read_json()
    PUSHDATA.update(PUSHDATA_NEW)
    write_json(PUSHDATA)

    scheduler.add_job(
        push_send,
        "cron",
        args=[id],
        id=f"history_push_{id}",
        replace_existing=True,
        hour=hour,
        minute=minute,
    )
    logger.info(f"[{id}]设置历史上的今天推送时间为：{hour}:{minute}")


push_matcher = on_command("历史上的今天")


@push_matcher.handle()
async def _(
    event: MessageEvent,
    matcher: Matcher,
    args: Message = CommandArg()
):
    if isinstance(event, GroupMessageEvent):
        id = "g_{}".format(event.group_id)
    else:
        id = "f_{}".format(event.user_id)
    if cmdarg := args.extract_plain_text():
        if "状态" in cmdarg:
            push_state = scheduler.get_job(f"history_push_{id}")
            if push_state:
                PUSHDATA = read_json()
                push_data = PUSHDATA.get(id)
                msg = (
                    f"推送时间: {push_data['hour']}:{push_data['minute']}"
                )
                await matcher.finish(msg)
        elif "设置" in cmdarg or "推送" in cmdarg:
            if ":" in cmdarg or "：" in cmdarg:
                matcher.set_arg("time_arg", args)
        elif "取消" in cmdarg or "关闭" in cmdarg:
            PUSHDATA = read_json()
            PUSHDATA.pop(id)
            write_json(PUSHDATA)
            scheduler.remove_job(f"history_push_{id}")
            logger.info(f"[{id}] 取消历史上的今天推送")
            await matcher.finish("历史上的今天推送已禁用")
        else:
            await matcher.finish("历史上的今天的推送参数不正确")
    else:
        msg = await get_history_info("image")
        await matcher.finish(msg)


@push_matcher.got("time_arg", prompt="请发送每日定时推送日历的时间，格式为：小时:分钟")
async def handle_time(
    event: MessageEvent,
    matcher: Matcher,
    state: T_State,
    time_arg: Message = Arg()
):
    state.setdefault("max_times", 0)
    time = time_arg.extract_plain_text()
    if any(cancel in time for cancel in ["取消", "放弃", "退出"]):
        await matcher.finish("已退出历史上的今天推送时间设置")
    match = re.search(r"(\d*)[:：](\d*)", time)
    if match and match[1] and match[2]:
        if isinstance(event, GroupMessageEvent):
            calendar_subscribe("g_{}".format(event.group_id), int(match[1]), int(match[2]))
        else:
            calendar_subscribe("f_{}".format(event.user_id), int(match[1]), int(match[2]))
        await matcher.finish(f"历史上的今天的每日推送时间已设置为：{match[1]}:{match[2]}")
    else:
        state["max_times"] += 1
        if state["max_times"] >= 3:
            await matcher.finish("你的错误次数过多，已退出历史上的今天推送时间设置")
        await matcher.reject("设置时间失败，请输入正确的格式，格式为：小时:分钟")


async def push_all_group_scheduler(bot:Bot):
    """为bot所在全部群聊添加推送任务"""
    group_list = await refresh_group_list(bot)
    PUSHDATA = read_json()
    for group in group_list:
        id = "g_{}".format(group)
        # 如果群聊未被自定义，使用全局定时时间
        if id not in PUSHDATA.keys():
            PUSHDATA_NEW = {}
            PUSHDATA_NEW.setdefault(
                id,
                {
                    "hour": int(HOUR_ENV),
                    "minute": int(MINUTE_ENV)
                }
            )
            PUSHDATA.update(PUSHDATA_NEW)

            # 不支持创建此刻定时任务
            await push_send(id)
            scheduler.add_job(
                push_send,
                "cron",
                args=[id],
                id=f"history_push_{id}",
                replace_existing=True,
                hour=int(HOUR_ENV),
                minute=int(MINUTE_ENV),
            )
            logger.debug(f"history_push_{id},{HOUR_ENV}:{MINUTE_ENV}")

    write_json(PUSHDATA)