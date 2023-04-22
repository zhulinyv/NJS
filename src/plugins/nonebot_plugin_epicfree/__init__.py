from typing import Dict

from nonebot import get_bot, get_driver, on_regex
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot_plugin_apscheduler import scheduler

try:
    from nonebot.adapters.onebot.v11 import Bot, Event, Message  # type: ignore
    from nonebot.adapters.onebot.v11.event import (  # type: ignore
        GroupMessageEvent,
        MessageEvent,
    )
except ImportError:
    from nonebot.adapters.cqhttp import Bot, Event, Message  # type: ignore
    from nonebot.adapters.cqhttp.event import GroupMessageEvent, MessageEvent  # type: ignore

from .data_source import getEpicFree, subscribeHelper

try:
    epicScheduler = get_driver().config.epic_scheduler
    assert epicScheduler is not None
except (AttributeError, AssertionError):
    epicScheduler = "5 8 8 8"
day_of_week, hour, minute, second = epicScheduler.split(" ")


epicMatcher = on_regex(r"((E|e)(P|p)(I|i)(C|c))?喜(加一|\+1)", priority=2)


@epicMatcher.handle()
async def onceHandle(bot: Bot, event: Event):
    imfree = await getEpicFree()
    await epicMatcher.finish(Message(imfree))


epicSubMatcher = on_regex(r"喜(加一|\+1)(私聊)?订阅", priority=1)


@epicSubMatcher.handle()
async def subHandle(bot: Bot, event: MessageEvent, state: T_State):
    if isinstance(event, GroupMessageEvent):
        if event.sender.role not in ["admin", "owner"] or "私聊" in event.get_plaintext():
            # 普通群员只会启用私聊订阅
            # state["targetId"] = event.get_user_id()
            state["subType"] = "私聊"
        else:
            # 管理员用户询问需要私聊订阅还是群聊订阅
            pass
    else:
        state["subType"] = "私聊"


@epicSubMatcher.got("subType", prompt="回复「私聊」启用私聊订阅，回复其他内容启用群聊订阅：")
async def subEpic(bot: Bot, event: MessageEvent, state: T_State):
    if any("私聊" in i for i in [event.get_plaintext().strip(), state["subType"]]):
        state["targetId"] = event.get_user_id()
        state["subType"] = "私聊"
    else:
        state["targetId"] = str(event.group_id)  # type: ignore
        state["subType"] = "群聊"
    msg = await subscribeHelper("w", state["subType"], state["targetId"])
    assert isinstance(msg, str)
    await epicSubMatcher.finish(msg)


@scheduler.scheduled_job(
    "cron", day_of_week=day_of_week, hour=hour, minute=minute, second=second
)
async def weeklyEpic():
    bot = get_bot()
    whoSubscribe = await subscribeHelper()
    imfree = await getEpicFree()
    try:
        assert isinstance(whoSubscribe, Dict)
        for group in whoSubscribe["群聊"]:
            await bot.send_group_msg(group_id=group, message=Message(imfree))
        for private in whoSubscribe["私聊"]:
            await bot.send_private_msg(user_id=private, message=Message(imfree))
    except FinishedException:
        pass
    except Exception as e:
        logger.error(f"Epic 限免游戏资讯定时任务出错 {type(e)}：{e}")
