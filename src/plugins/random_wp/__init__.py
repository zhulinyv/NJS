import time
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageSegment,
    GroupMessageEvent,
    PrivateMessageEvent
    )
from nonebot.params import CommandArg
from nonebot.log import logger
import random
import requests

from .api import *



picture = on_command("来点", aliases={"来份"}, priority=50, block=True)

@picture.handle()
async def _(msg: Message = CommandArg()):
    types = msg.extract_plain_text().strip()

    if types == "二次元":
        pic = get_pic(random.choice(random_acg))
        await picture.finish(MessageSegment.image(file=pic), at_sender=True)

    elif types == "壁纸推荐":
        pic = get_pic(random.choice(wp_top))
        await picture.finish(MessageSegment.image(file=pic), at_sender=True)

    elif types == "白毛":
        pic = get_pic(random.choice(white))
        await picture.finish(MessageSegment.image(file=pic), at_sender=True)
    
    elif types == "兽耳":
        pic = get_pic(random.choice(cat))
        await picture.finish(MessageSegment.image(file=pic), at_sender=True)

    elif types == "星空":
        pic = get_pic(random.choice(star))
        await picture.finish(MessageSegment.image(file=pic), at_sender=True)

    elif types == "竖屏壁纸":
        pic = get_pic(random.choice(phone))
        await picture.finish(MessageSegment.image(file=pic), at_sender=True)

    elif types == "横屏壁纸":
        pic = get_pic(random.choice(pc))
        await picture.finish(MessageSegment.image(file=pic), at_sender=True)

    elif types == "萝莉":
        pic = get_pic(random.choice(loli))
        await picture.finish(MessageSegment.image(file=pic), at_sender=True)

    elif types == "必应壁纸":
        # await picture.finish(MessageSegment.image(file=f'{random.choice(bing)}'), at_sender=True)
        d_url = str(getBingImageURL())
        description = getBingDescription()
        msg_img = MessageSegment.image(d_url)
        logger.info("图片获取成功!")
        msg_title = Message(str(description['title']))
        msg_headline = Message(str("图片主题：" + description['headline']))
        msg_desc = Message(str("图片故事：" + description['description']))
        msg_maintext = Message(str("图片介绍：" + description['main_text']))
        msg = msg_title + Message("\n") + Message("\n") + msg_headline + Message("\n") + Message(
            "\n") + msg_maintext + Message("\n") + Message("\n") + msg_desc + Message("\n") + Message("\n") + Message(
            msg_img)
        await picture.send(msg)
        logger.info("消息发送成功!")

    elif types == "必应电脑壁纸":
        d_url = str(getBingImageURL())
        msg_img = MessageSegment.image(d_url)
        logger.info("图片获取成功!")
        msg = Message(msg_img)
        await picture.send(msg)
        logger.info("消息发送成功!")
        
    elif types == "必应手机壁纸":
        d_url = str(getBingVerticalImageURL())
        msg_img = MessageSegment.image(d_url)
        logger.info("图片获取成功!")
        msg = Message(msg_img)
        await picture.send(msg)
        logger.info("消息发送成功!")
        


PUID = on_command("PUID", aliases={"puid"}, priority=50, block=True)
@PUID.handle()
async def _(bot: Bot, event: Event, msg: Message = CommandArg()):
    user_id = msg.extract_plain_text().strip()

    url = f"https://sex.nyan.xyz/api/v2/?author_uuid={user_id}"
    res = requests.get(url).json()

    try:
        # 图片信息
        pid = str(res["data"][0]["pid"])
        page = res["data"][0]["page"]
        author = res["data"][0]["author"]
        author_uid = str(res["data"][0]["author_uid"])
        title = res["data"][0]["title"]
        # 时间戳类型的时间
        upload_date = int(res["data"][0]["upload_date"])
        # 这里转换一下
        upload_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(upload_date/1000))
        # 图片链接
        pic = res["data"][0]["url"]
        logger.info("获取图片成功！")
        
        message = f"\nPID: {pid}\n链接: {page}\n作者: {author}\n作者ID: {author_uid}\n标题: {title}\n上传日期: {upload_date}"
        pic = MessageSegment.image(file=pic)
        msg = pic + message

    except Exception:
        msg = '没找到该画师的插图哦~'

    # 私聊直接发送
    if isinstance(event, PrivateMessageEvent):
        # 咱也不知道为什么发送了个寂寞捏...
        await PUID.send(msg)
    # 群聊转发
    elif isinstance(event, GroupMessageEvent):
        msgs = []
        message_list = []
        message_list.append(msg)
        for msg in message_list:
            msgs.append({
                'type': 'node',
                'data': {
                    'name': "脑积水",
                    'uin': bot.self_id,
                    'content': msg
                }
            })
        await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)