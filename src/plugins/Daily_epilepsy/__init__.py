import random
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, Event, Bot, GroupMessageEvent
from nonebot.plugin.on import on_command

from .utils import *

aya = on_command("每日发癫", aliases={"发癫"}, priority=5, block=True)

@aya.handle()
async def _(bot: Bot, event: Event, arg: Message = CommandArg()):
    lucky_user = await get_at(bot, event)
    if lucky_user == "寄":
        msg = arg.extract_plain_text().strip()
        if msg == "" or msg.isspace():
            await aya.finish("你要对谁发癫")
        randomPost = random.choice(post).replace("阿咪", msg).replace("嘉然小姐", msg).replace(
            "嘉然", msg).replace("然然", msg).replace("纳西妲", msg).replace("草神", msg).replace("胡桃", msg)
        await aya.finish(randomPost)
    else:
        randomPost = random.choice(post).replace("阿咪", lucky_user).replace("嘉然小姐", lucky_user).replace(
            "嘉然", lucky_user).replace("然然", lucky_user).replace("纳西妲", lucky_user).replace("草神", lucky_user).replace("胡桃", lucky_user)
        await aya.finish(randomPost)

async def get_at(bot:Bot, event:Message) -> str:
    if isinstance(event, GroupMessageEvent):
        msg=event.get_message()
        for msg_seg in msg:
            if msg_seg.type == "at":
                return(await get_user_card(bot, event.group_id, int(msg_seg.data["qq"])))
        return "寄"
    else:
        return "寄"

async def get_user_card(bot:Bot, group_id, qid) -> str:
    # 返回用户nickname
    user_info: dict = await bot.get_group_member_info(group_id=group_id, user_id=qid)
    user_card = user_info["card"]
    if not user_card:
        user_card = user_info["nickname"]
    return user_card