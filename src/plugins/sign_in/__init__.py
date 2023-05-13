import httpx
import base64
import random
import nonebot
from io import BytesIO
from typing import Union
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed

from .base import *
from .text import *
from .utils import *

from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.plugin.on import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    GroupMessageEvent,
    PrivateMessageEvent,
)

try:
    import ujson as json
except:
    import json

try:
    NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]
except Exception:
    NICKNAME: str = "脑积水"



give_okodokai = on_command("盖章", aliases={"签到", "妈!"}, priority=30, block=True)
@give_okodokai.handle()
async def _(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
    # 获取 QQ 号和群号
    uid = event.user_id
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    else:
        await give_okodokai.finish()

    # 签到
    if not lmt.check(f"{uid}@{gid}"):
        await give_okodokai.finish('今天已经签到过啦，明天再来叭~', at_sender=True)
    lmt.increase(f"{uid}@{gid}")
    todo = random.choice(todo_list)
    stamp = random.choice(card_file_names_all)
    path = DIR_PATH / stamp
    image = MessageSegment.image(path)
    card_id = stamp[:-4]
    db.add_card_num(gid, uid, card_id)

    # 一言
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.vvhan.com/api/ian")
        response_text = response.text
    goodwill = random.randint(1,10)

    # 读写数据
    with open(GOODWILL_PATH / "goodwill.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        try:
            user_goodwill = data[str(gid)][str(uid)]
        except:
            user_goodwill = 0
    f.close()
    with open(GOODWILL_PATH / "goodwill.json", "w", encoding="utf-8") as f:
        if str(gid) in data:
            data[str(gid)][str(uid)] = user_goodwill + goodwill
        else:
            data[str(gid)] = {str(uid): user_goodwill + goodwill}
        json.dump(data, f, indent=4, ensure_ascii=False)
    f.close()

    await give_okodokai.send(f'\n欢迎回来, 主人 ~ !' + image + f'\n好感 + {goodwill} ! 当前好感: {data[str(gid)][str(uid)]}\n' + f'主人今天要{todo}吗? \n\n今日一言: {response_text}', at_sender=True)



storage = on_command('收集册', priority=30, block=True)
@storage.handle()
async def _(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent], msg: Message = CommandArg()):
    # 获取 QQ 号
    message = msg.extract_plain_text().strip()
    variable_list = message.split(' ')
    variable_list = [word.strip() for word in variable_list if word.strip()]
    uid = await get_at(event)
    if uid == -1:
        if variable_list == []:
            uid = event.user_id
        elif len(variable_list) == 1:
            uid = int(variable_list[0])
        else:
            await storage.finish("格式错误，请检查后重试\n收集册+艾特(或qq号)", at_sender=True)

    # 获取群号
    if isinstance(event, GroupMessageEvent):
        gid = event.group_id
    elif isinstance(event, GuildMessageEvent):
        gid = event.guild_id
    elif isinstance(event, PrivateMessageEvent):
        gid = uid
    else:
        await give_okodokai.finish()

    # 收集册
    row_num = len_card//COL_NUM if len_card % COL_NUM !=0 else len_card//COL_NUM-1
    base = Image.open(FRAME_DIR_PATH + '/frame.png')
    base = base.resize((40 + COL_NUM * 80 + (COL_NUM - 1) * 10, 150 + row_num * 80 + (row_num - 1) * 10), Image.ANTIALIAS)
    cards_num = db.get_cards_num(gid, uid)
    row_index_offset = 0
    row_offset = 0
    cards_list = card_file_names_all
    for index, c_id in enumerate(cards_list):
        row_index = index // COL_NUM + row_index_offset
        col_index = index % COL_NUM
        f = get_pic(c_id, False) if int(c_id[:-4]) in cards_num else get_pic(c_id, True)
        base.paste(f, (30 + col_index * 80 + (col_index - 1) * 10, row_offset + 40 + row_index * 80 + (row_index - 1) * 10))
    row_offset += 30
    ranking = db.get_group_ranking(gid, uid)
    ranking_desc = f'第{ranking}位' if ranking != -1 else '未上榜'
    buf = BytesIO()
    base = base.convert('RGB')
    base.save(buf, format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    img = MessageSegment.image(base64_str)

    # 整合信息并发送
    if isinstance(event, GroupMessageEvent):
        lucky_user_card = await get_user_card(bot, gid, uid)
        try:
            storage.finish(f'『{lucky_user_card}』的收集册:\n' + img + f'图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}', at_sender=True)
        except ActionFailed:
            logger.warning("直接发送失败, 尝试以转发形式发送!")
            msgs = []
            message_list = []
            message_list.append(f'『{lucky_user_card}』的收集册:\n' + img + f'图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}')
            for msg in message_list:
                msgs.append({
                    'type': 'node',
                    'data': {
                        'name': f"{NICKNAME}",
                        'uin': bot.self_id,
                        'content': msg
                    }
                })
            await bot.call_api('send_group_forward_msg', group_id=gid, messages=msgs)
            logger.success("发送成功!")
    elif isinstance(event, GuildMessageEvent):
        await storage.finish(f'的收集册:\n' + img + f'图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}', at_sender=True)
    elif isinstance(event, PrivateMessageEvent):
        await storage.finish(f'你的收集册:\n' + img + f'图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}')
    else:
        await storage.finish()