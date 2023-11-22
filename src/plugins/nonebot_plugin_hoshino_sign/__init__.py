import time
import httpx
import base64
import random
import textwrap

import ujson as json

from io import BytesIO
from typing import Union
from pil_utils import Text2Image
from PIL import Image, ImageFont, ImageDraw, ImageFilter

from nonebot import require
require("nonebot_plugin_guild_patch")
from nonebot.plugin import PluginMetadata
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed

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

from .base import *
from .utils import *
from .config import *

__plugin_meta__ = PluginMetadata(
    name="签到",
    description="从 hoshino 搬来的 pcr 签到",
    usage=("""
签到/盖章/妈!: 签到(获得好感和 pcr 的印章)
收集册(+QQ号/艾特): 查看自己或他人的收集进度
"""
    ),
    extra={
        "author": "zhulinyv <zhulinyv2005@outlook.com>",
        "version": "2.3.2",
    },
    config=Config
)



give_okodokai = on_command("盖章", aliases={"签到", "妈!"}, priority=30, block=True)
@give_okodokai.handle()
async def _(event: Union[GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent], bot: Bot):
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

    # 日期
    time_tuple = time.localtime(time.time())
    last_time = f"{time_tuple[0]}年{time_tuple[1]}月{time_tuple[2]}日"

    # 签到
    with open(GOODWILL_PATH + "goodwill.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        try:
            if data[str(gid)][str(uid)][1] == last_time:
                await give_okodokai.finish('今天已经签到过啦，明天再来叭~', at_sender=True)
        except KeyError:
            pass

    # 发癫待办
    todo = random.choice(todo_list)
    # 增加好感
    goodwill = random.randint(1, 10)
    # 随机图案
    stamp = random.choice(card_file_names_all)
    path = STAMP_PATH / stamp
    if sign_config.bg_mode == 1:
        # 下载背景
        res = httpx.get(url='https://dev.iw233.cn/api.php?sort=mp&type=json', headers={'Referer':'http://www.weibo.com/'})
        res = res.text
        pic_url = json.loads(res)["pic"][0]
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{pic_url}", headers={'Referer':'http://www.weibo.com/',}, timeout=10)
            with open(os.path.dirname(os.path.abspath(__file__)) + "/sign_bg.png", 'wb') as f:
                f.write(response.content)
        # 调整大小
        sign_bg = Image.open(os.path.dirname(os.path.abspath(__file__)) + "/sign_bg.png").convert("RGBA")
        weight, height = sign_bg.size
        if (weight / height) >= (928 / 1133):
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            sign_bg = sign_bg.resize((int(weight * (1133 / height)), 1133))
            print(sign_bg.size)
            print((int((int(weight * (1133 / height)) - 928) / 2), 0, int((int(weight * (1133 / height)) - 928) / 2 + 928), 1133))
            sign_bg = sign_bg.crop((int((int(weight * (1133 / height)) - 928) / 2), 0, int((int(weight * (1133 / height)) - 928) / 2 + 928), 1133))
        elif (weight / height) < (928 / 1133):
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            sign_bg = sign_bg.resize((928, int(height * (928 / weight))))
            print(sign_bg.size)
            print((0, int((int(height * (928 / weight)) - 1133) / 2), 928, int((int(height * (928 / weight)) - 1133) / 2 + 1133)))
            sign_bg = sign_bg.crop((0, int((int(height * (928 / weight)) - 1133) / 2), 928, int((int(height * (928 / weight)) - 1133) / 2 + 1133)))
        sign_bg = sign_bg.resize((928, 1133))
        # 模糊背景
        sign_bg = sign_bg.filter(ImageFilter.GaussianBlur(8))
        # 背景阴影
        shadow = Image.open(os.path.dirname(os.path.abspath(__file__)) + "/image/shadow.png").convert("RGBA")
    else:
        sign_bg_list = os.listdir(os.path.dirname(os.path.abspath(__file__)) + "/image/sign_bg")
        sign_bg = Image.open(os.path.dirname(os.path.abspath(__file__)) + f"/image/sign_bg/{random.choice(sign_bg_list)}")

    draw = ImageDraw.Draw(sign_bg)
    # 调整样式
    stamp_img = Image.open(path)
    stamp_img = stamp_img.resize((502, 502))
    w, h = stamp_img.size
    mask = Image.new('RGBA', (w, h), color=(0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, w, h), fill=(0, 0, 0, 255))
    sign_bg.paste(stamp_img, (208, 43, 208+w, 43+h), mask)

    # 收集册
    card_id = stamp[:-4]
    db.add_card_num(gid, uid, card_id)

    # 一言
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://v1.hitokoto.cn/?c=f&encode=text")
            status_code = response.status_code
            if status_code == 200:
                response_text = response.text
            else:
                response_text = f"请求错误: {status_code}"
    except Exception as error:
        logger.warning(error)

    # 读写数据
    with open(GOODWILL_PATH + "goodwill.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        try:
            user_goodwill = data[str(gid)][str(uid)][0]
        except:
            user_goodwill = 0
    with open(GOODWILL_PATH + "goodwill.json", "w", encoding="utf-8") as f:
        if str(gid) in data:
            data[str(gid)][str(uid)] = [user_goodwill + goodwill, last_time]
        else:
            data[str(gid)] = {str(uid): [user_goodwill + goodwill, last_time]}
        json.dump(data, f, indent=4, ensure_ascii=False)

    # 计算排行
    data = data[f"{gid}"]
    new_dictionary = {}
    rank_num = 1
    for user_data in data:
        new_dictionary[f"{user_data}"] = int(f"{data[f'{user_data}'][0]}")
    for i in sorted(new_dictionary.items(), key=lambda x:x[1], reverse=True):
        q, g = i
        try:
            if q != str(uid):
                rank_num += 1
            else:
                rank_user = await get_user_card(bot, gid, q)
                break
        except Exception:
            pass

    # 绘制文字
    with open(sign_config.font_path, "rb") as draw_font:
        bytes_font = BytesIO(draw_font.read())
        text_font = ImageFont.truetype(font=bytes_font, size=45)
    draw.text(xy=(98, 580), text=f"欢迎回来, {rank_user}~!", font=text_font)
    draw.text(xy=(98, 633), text=f"好感 + {goodwill} !  当前好感: {g}", font=text_font)
    draw.text(xy=(98, 686), text=f"当前群排名: 第 {rank_num} 位", fill=(200, 255, 255), font=text_font)
    draw.text(xy=(98, 739), text=f"发送\"收集册\"查看收集进度", fill=(255, 180, 220), font=text_font)
    para = textwrap.wrap(f"主人今天要{todo}吗?", width=16)
    for i, line in enumerate(para):
        draw.text((98, 53 * i + 792), line, 'white', text_font)
    para = textwrap.wrap(f"今日一言: {response_text}", width=16)
    for i, line in enumerate(para):
        draw.text((98, 53 * i + 898), line, 'white', text_font)

    output = BytesIO()
    if sign_config.bg_mode == 1:
        # 合并图片
        final = Image.new("RGBA", (928, 1133))
        final = Image.alpha_composite(final, sign_bg)
        final = Image.alpha_composite(final, shadow)
        final.save(output, format="png")
    else:
        sign_bg.save(output, format="png")

    await give_okodokai.send(MessageSegment.image(output), at_sender=True, reply_message=True)


storage = on_command('收集册', aliases={"排行榜", "图鉴"}, priority=30, block=True)
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
            await storage.finish("格式错误, 请检查后重试, 格式应为:\n收集册+艾特(或qq号)", at_sender=True)

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
    base = base.resize((40 + COL_NUM * 80 + (COL_NUM - 1) * 10, 150 + row_num * 80 + (row_num - 1) * 10), Image.LANCZOS)
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

    with open(GOODWILL_PATH + "goodwill.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    data = data[f"{gid}"]
    new_dictionary = {}
    rank_text = ""
    rank_num = 1
    for user_data in data:
        new_dictionary[f"{user_data}"] = int(f"{data[f'{user_data}'][0]}")
    for i in sorted(new_dictionary.items(), key=lambda x:x[1], reverse=True):
        q, g = i
        try:
            rank_user = await get_user_card(bot, gid, q)
            rank_text += f"{rank_num}. {rank_user} 好感:{g}\n"
            rank_num += 1
        except Exception:
            pass
        if rank_num > 10:
            break
    rank_num = 1
    for i in sorted(new_dictionary.items(), key=lambda x:x[1], reverse=True):
        q, g = i
        try:
            if q != str(uid):
                rank_num += 1
            else:
                break
        except Exception:
            pass
    rank_text = f"好感排行: \n{rank_text}......\n当前排名: {rank_num}"
    rank_img = Text2Image.from_text(rank_text, 15, fill="black").to_image(bg_color="white")
    output = BytesIO()
    rank_img.save(output, format="png")

    # 整合信息并发送
    if isinstance(event, GroupMessageEvent):
        lucky_user_card = await get_user_card(bot, gid, uid)
        try:
            await storage.finish(f'\n『{lucky_user_card}』的收集册:\n' + img + f'\n图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}\n' + MessageSegment.image(output), reply_message=True)
        except ActionFailed:
            logger.warning("直接发送失败, 尝试以转发形式发送!")
            msgs = []
            message_list = []
            message_list.append(f'『{lucky_user_card}』的收集册:\n' + img + f'\n图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}\n' + MessageSegment.image(output))
            for msg in message_list:
                msgs.append({
                    'type': 'node',
                    'data': {
                        'name': f"{Config.NICKNAME}",
                        'uin': bot.self_id,
                        'content': msg
                    }
                })
            await bot.call_api('send_group_forward_msg', group_id=gid, messages=msgs)
            logger.success("发送成功!")
    elif isinstance(event, GuildMessageEvent):
        await storage.finish(f'的收集册:\n' + img + f'\n图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}\n' + MessageSegment.image(output), at_sender=True)
    elif isinstance(event, PrivateMessageEvent):
        await storage.finish(f'你的收集册:\n' + img + f'\n图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}\n' + MessageSegment.image(output), reply_message=True)
    else:
        return