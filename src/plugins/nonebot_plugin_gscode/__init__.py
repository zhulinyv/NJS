from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, MessageEvent
from nonebot.plugin import on_command
from nonebot.typing import T_State

from .data_source import getCodes

codeMatcher = on_command("gscode", aliases={"兑换码"}, priority=5, block=True)


@codeMatcher.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    if event.get_plaintext() not in ["gscode", "兑换码"]:
        await codeMatcher.finish()
    codes = await getCodes()
    if isinstance(event, GroupMessageEvent):
        await bot.send_group_forward_msg(group_id=event.group_id, messages=codes)  # type: ignore
    else:
        await bot.send_private_forward_msg(user_id=event.user_id, messages=codes)  # type: ignore
