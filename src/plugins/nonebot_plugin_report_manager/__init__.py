from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent, GroupMessageEvent
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.message import event_preprocessor
from nonebot import get_driver, logger
from nonebot.exception import IgnoredException
from .import blacklist

superusers = get_driver().config.superusers
report = on_command("反馈开发者", priority=50)


@report.handle()
async def report_handle(bot: Bot, event: Event):
    msg = str(event.get_message()).split("反馈开发者", 1)[1].strip()
    if msg == "":
        await report.finish("反馈内容不能为空！")
    if isinstance(event, GroupMessageEvent):
        group_info = await bot.get_group_info(group_id=event.group_id)
        group_name = group_info["group_name"]
        for id in superusers:
            await bot.send_private_msg(user_id=int(id), message=f"来自群【{group_name}】的用户 {event.get_user_id()} 反馈：{msg}")
        await report.finish("已反馈，感谢您的支持！")
    for id in superusers:
        await bot.send_private_msg(user_id=int(id), message=f"用户 {event.get_user_id()} 反馈：{msg}")
    await report.finish("已反馈，感谢您的支持！")


# add_blacklist = on_command("拉黑", permission=SUPERUSER)
# 
# 
# @add_blacklist.handle()
# async def add_black_list(event: MessageEvent):
#     msg = blacklist.handle_blacklist(event, "add")
#     await add_blacklist.send(msg)
# 
# 
# del_blacklist = on_command("解除拉黑", permission=SUPERUSER)
# 
# 
# @del_blacklist.handle()
# async def del_black_list(event: MessageEvent):
#     msg = blacklist.handle_blacklist(event, "del")
#     await del_blacklist.send(msg)
# 
# 
# check_blacklist = on_command("查看黑名单", permission=SUPERUSER)
# 
# 
# @check_blacklist.handle()
# async def check_black_list():
#     if len(blacklist.blacklist["blacklist"]) == 0:
#         await check_blacklist.finish("当前无黑名单用户")
#     await check_blacklist.send(f"当前黑名单用户: {', '.join(blacklist.blacklist['blacklist'])}")
# 
# 
# @event_preprocessor
# def blacklist_processor(event: MessageEvent):
#     uid = str(event.user_id)
#     if uid in superusers:
#         return
#     if uid in blacklist.blacklist["blacklist"]:
#         logger.debug(f"用户 {uid} 在黑名单中, 忽略本次消息")
#         raise IgnoredException("黑名单用户")