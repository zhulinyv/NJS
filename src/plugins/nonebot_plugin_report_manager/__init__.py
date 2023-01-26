from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, Message

report = on_command("反馈开发者", priority=50, block=True)

@report.handle()
async def report_handle(bot: Bot, event: Event):
    for id in bot.config.superusers:
        await bot.send_private_msg(user_id = int(id), message=Message(f"用户{event.get_user_id()}反馈：{event.get_message()}"))
    await report.finish("已反馈，感谢支持哦~")