from nonebot import logger
from nonebot.params import CommandArg

from nonebot import on_startswith, on_command, require
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    MessageSegment,
    Message
)

from PIL import Image

from .utils import course_manager, get_weekday
from nonebot_plugin_PicMenu.img_tool import img2b64
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='课表查询',
    description="查询课表，今天还有什么课",
    usage=f"""本周课表：查看这周的课表\n
完整课表：查看完整的课表\n
下周课表：查看下周的课表\n
查看课表 + 周数：查询指定周的课表\n
设置周数 + 周数：设定当前是第几周\n
上课：查询当前是否有课，及今天的下一节课是什么，还有多久上""".strip(),
)

scheduler = require("nonebot_plugin_apscheduler").scheduler

check_full_timetable = on_startswith("完整课表", permission=GROUP, priority=5, block=False)

week_timetable = on_startswith("本周课表", permission=GROUP, priority=5, block=True)

next_week_timetable = on_startswith("下周课表", permission=GROUP, priority=5, block=True)

now_course = on_command("上课", permission=GROUP, priority=5, block=True)

set_now_week = on_command("设置周数", permission=GROUP, priority=5, block=True)

check_timetable = on_command("查看课表", permission=GROUP, priority=5, block=True)

tomo_course = on_command("明日早八", permission=GROUP, priority=5, block=True)


# 每周一凌晨定时更新当前周数
@scheduler.scheduled_job("cron", hour=1, minute=25)
async def auto_update_current_week():
    if get_weekday() == 1:
        course_manager.auto_update_week()
        logger.info("更新周数成功")


@check_full_timetable.handle()
async def _(event: GroupMessageEvent):
    img = course_manager.generate_timetable_image(event)
    if not isinstance(img, Image.Image):
        await check_full_timetable.finish(img)
    else:
        await check_full_timetable.finish(MessageSegment.image('base64://' + img2b64(img)))


@week_timetable.handle()
async def _(event: GroupMessageEvent):
    img = course_manager.generate_week_image(event, week=course_manager.get_week(event))
    if not isinstance(img, Image.Image):
        await week_timetable.finish(img)
    else:
        await week_timetable.finish(MessageSegment.image('base64://' + img2b64(img)))


@next_week_timetable.handle()
async def _(event: GroupMessageEvent):
    img = course_manager.generate_week_image(event, week=course_manager.get_week(event) + 1)
    if not isinstance(img, Image.Image):
        await next_week_timetable.finish(img)
    else:
        await next_week_timetable.finish(MessageSegment.image('base64://' + img2b64(img)))


@now_course.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    msg = course_manager.now_course(event)
    args = arg.extract_plain_text().strip()
    if args == "":
        await now_course.finish(msg)


@tomo_course.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    msg = course_manager.tomo_course(event)
    args = arg.extract_plain_text().strip()
    if args == "":
        await tomo_course.finish(msg)


@set_now_week.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    user_id = str(event.user_id)
    args = arg.extract_plain_text().strip()
    if args == "":
        await check_timetable.finish("请输入周数")
    if int(args) < 1:
        await set_now_week.finish("设置周数不能小于1")
    else:
        course_manager.set_week(event, int(args))
        await set_now_week.finish(f"设置成功,{user_id}当前周数{args}")


@check_timetable.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip()
    if args == "":
        await check_timetable.finish("请输入周数")
    else:
        week = int(args)
        if week < 1:
            await check_timetable.finish("周数不能小于1")
        img = course_manager.generate_week_image(event, week)
        if not isinstance(img, Image.Image):
            await check_timetable.finish(img)
        else:
            await check_timetable.finish(MessageSegment.image('base64://' + img2b64(img)))


