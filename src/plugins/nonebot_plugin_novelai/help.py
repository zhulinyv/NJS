from nonebot import on_command
# from .utils import cs, aliases

help = on_command("help", aliases={"帮助"}, block=True, priority=9)
help.handle()
async def help_handle():
    help.finish()