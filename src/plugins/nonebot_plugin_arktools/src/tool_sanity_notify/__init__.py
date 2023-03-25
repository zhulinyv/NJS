"""理智恢复提醒"""
from datetime import datetime

import tortoise.exceptions
from nonebot import on_command, get_bot, logger, get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler

from ..configs.scheduler_config import SchedulerConfig
from ..core.database import UserSanityModel

scfg = SchedulerConfig.parse_obj(get_driver().config.dict())

add_notify = on_command("理智提醒", aliases={"ADDSAN"})
check_notify = on_command("理智查看", aliases={"CHECKSAN"})


@add_notify.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().strip().split()
    uid = event.user_id
    gid = event.group_id
    now = datetime.now()

    if not args:
        notify_time = datetime.fromtimestamp(now.timestamp() + 135 * 360, tz=now.tzinfo)
        data = await UserSanityModel.filter(gid=gid, uid=uid).first()
        if not data:
            await UserSanityModel.create(
                gid=gid, uid=uid, record_time=now, notify_time=notify_time, status=1
            )
        else:
            await UserSanityModel.filter(gid=gid, uid=uid).update(
                record_san=0, notify_san=135,
                record_time=now, notify_time=notify_time, status=1
            )
    elif len(args) == 2:
        record_san, notify_san = args
        notify_time = datetime.fromtimestamp(now.timestamp() + (int(notify_san) - int(record_san)) * 360, tz=now.tzinfo)
        data = await UserSanityModel.filter(gid=gid, uid=uid).first()
        if not data:
            await UserSanityModel.create(
                gid=gid, uid=uid, record_san=record_san, notify_san=notify_san,
                record_time=now, notify_time=notify_time, status=1
            )
        else:
            await UserSanityModel.filter(gid=gid, uid=uid).update(
                record_san=record_san, notify_san=notify_san,
                record_time=now, notify_time=notify_time, status=1
            )
    else:
        await add_notify.finish("小笨蛋，命令的格式是：“理智提醒 [当前理智] [回满理智]” 或 “理智提醒” 哦！",
                                at_sender=True)

    await add_notify.finish(f"记录成功！将在 {notify_time.__str__()[:-7]} 提醒博士哦！", at_sender=True)


@check_notify.handle()
async def _(event: GroupMessageEvent):
    uid = event.user_id
    gid = event.group_id

    data = await UserSanityModel.filter(gid=gid, uid=uid, status=1).first()
    if not data:
        await check_notify.finish("小笨蛋，你还没有记录过理智提醒哦！", at_sender=True)

    data = data.__dict__

    record_time: datetime = data["record_time"]
    notify_time: datetime = data["notify_time"]
    now = datetime.now(tz=record_time.tzinfo)

    elapsed_time = now - record_time
    remain_time = notify_time - now

    recoverd_san: int = elapsed_time.seconds // 360 if elapsed_time.seconds >= 360 else 0
    now_san: int = data["record_san"] + recoverd_san

    await check_notify.finish(f"距离理智恢复完毕还有 {remain_time.__str__()[:-7]}，当前理智：{now_san}(+{recoverd_san})")


@scheduler.scheduled_job(
    "interval",
    minutes=scfg.sanity_notify_interval,
)
async def _():
    if scfg.sanity_notify_switch:
        logger.debug("checking sanity...")
        try:
            bot: Bot = get_bot()
        except ValueError:
            pass
        else:
            now = datetime.now()
            try:
                data = await UserSanityModel.filter(notify_time__lt=now, status=1).all()
            except tortoise.exceptions.BaseORMException:
                logger.error("检查理智提醒失败，数据库未初始化")
            else:
                if data:
                    for model in data:
                        await bot.send_group_msg(
                            group_id=model.gid,
                            message=Message(MessageSegment.at(model.uid) + f"你的理智已经恢复到{model.notify_san}了哦！")
                        )
                        await UserSanityModel.filter(gid=model.gid, uid=model.uid).update(status=0)


__plugin_meta__ = PluginMetadata(
    name="理智提醒",
    description="在理智回满时@用户提醒",
    usage=(
        "命令:"
        "\n    理智提醒 => 默认记当前理智为0，回满到135时提醒"
        "\n    理智提醒 [当前理智] [回满理智] => 同上，不过手动指定当前理智与回满理智"
        "\n    理智查看 => 查看距离理智回满还有多久，以及当期理智为多少"
    ),
    extra={
        "name": "sanity_notify",
        "author": "NumberSir<number_sir@126.com>",
        "version": "0.1.0"
    }
)
