import httpx
import base64
import random
import nonebot
from io import BytesIO

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
async def _(event: GroupMessageEvent):
    uid = event.user_id
    gid = event.group_id
    if not lmt.check(f"{uid}@{gid}"):
        await give_okodokai.finish('今天已经签到过啦，明天再来叭~', at_sender=True)
    lmt.increase(f"{uid}@{gid}")
    present = random.choice(login_presents)
    todo = random.choice(todo_list)
    stamp = random.choice(card_file_names_all)
    path = DIR_PATH / stamp
    image = MessageSegment.image(path)
    card_id = stamp[:-4]
    db.add_card_num(gid, uid, card_id)

    async with httpx.AsyncClient() as client:
            response = await client.get("https://api.vvhan.com/api/ian")
            response_text = response.text
    goodwill = random.randint(1,10)

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

    await give_okodokai.send(f'\n欢迎回来, 主人~!' + image + f'\n好感 + {goodwill}! 当前好感: {data[str(gid)][str(uid)]}\n' + f'主人今天要{todo}吗? \n\n今日一言: {response_text}', at_sender=True)



storage = on_command('收集册', priority=30, block=True)
@storage.handle()
async def _(bot:Bot, ev: GroupMessageEvent, msg: Message = CommandArg()):
    # 获取 QQ 号
    message = msg.extract_plain_text().strip()
    variable_list = message.split(' ')
    variable_list = [word.strip() for word in variable_list if word.strip()]
    uid = await get_at(ev)
    if uid == -1:
        if variable_list == []:
            uid = ev.user_id
        elif len(variable_list) == 1:
            uid = int(variable_list[0])
        else:
            await storage.finish("格式错误，请检查后重试\n收集册+艾特(或qq号)", at_sender=True)

    # 收集册
    row_num = len_card//COL_NUM if len_card % COL_NUM !=0 else len_card//COL_NUM-1
    base = Image.open(FRAME_DIR_PATH + '/frame.png')
    base = base.resize((40 + COL_NUM * 80 + (COL_NUM - 1) * 10, 150 + row_num * 80 + (row_num - 1) * 10), Image.ANTIALIAS)
    cards_num = db.get_cards_num(ev.group_id, uid)
    row_index_offset = 0
    row_offset = 0
    cards_list = card_file_names_all
    for index, c_id in enumerate(cards_list):
        row_index = index // COL_NUM + row_index_offset
        col_index = index % COL_NUM
        f = get_pic(c_id, False) if int(c_id[:-4]) in cards_num else get_pic(c_id, True)
        base.paste(f, (30 + col_index * 80 + (col_index - 1) * 10, row_offset + 40 + row_index * 80 + (row_index - 1) * 10))
    row_offset += 30
    ranking = db.get_group_ranking(ev.group_id, uid)
    ranking_desc = f'第{ranking}位' if ranking != -1 else '未上榜'
    buf = BytesIO()
    base = base.convert('RGB')
    base.save(buf, format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'

    # 整合信息并发送
    lucky_user_card = await get_user_card(bot, ev.group_id, uid)
    if isinstance(ev, GroupMessageEvent):
        msgs = []
        message_list = []
        message_list.append(f'『{lucky_user_card}』的收集册:[CQ:image,file={base64_str}]\n' + f'图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}' + f'\n当前群排名: {ranking_desc}')
        for msg in message_list:
            msgs.append({
                'type': 'node',
                'data': {
                    'name': f"{NICKNAME}",
                    'uin': bot.self_id,
                    'content': msg
                }
            })
        await bot.call_api('send_group_forward_msg', group_id=ev.group_id, messages=msgs)
    else:
        await storage.finish(f'『{lucky_user_card}』的收集册:[CQ:image,file={base64_str}]\n' + f'图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}' + f'\n当前群排名: {ranking_desc}')