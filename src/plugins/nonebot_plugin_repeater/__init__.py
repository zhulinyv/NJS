from nonebot import on_message, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from . import config
import re

repeater_group = config.repeater_group
shortest = config.shortest_length

m = on_message(priority=100, block=False)

last_message = {}
message_times = {}


# 消息预处理
def messagePreprocess(message: str):
    raw_message = message
    contained_images = {}
    images = re.findall(r'\[CQ:image.*?]', message)
    for i in images:
        contained_images.update({i: [re.findall(r'url=(.*?)[,\]]', i)[0][0], re.findall(r'file=(.*?)[,\]]', i)[0][0]]})
    for i in contained_images:
        message = message.replace(i, f'[{contained_images[i][1]}]')
    return message, raw_message


@m.handle()
async def repeater(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    if gid in repeater_group or "all" in repeater_group:
        global last_message, message_times
        message, raw_message = messagePreprocess(str(event.message))
        logger.debug(f'这一次消息: {message}')
        logger.debug(f'上一次消息: {last_message.get(gid)}')
        if last_message.get(gid) != message:
            message_times[gid] = 1
        else:
            message_times[gid] += 1
        logger.debug(f'已重复次数: {message_times.get(gid)}/{config.shortest_times}')
        if message_times.get(gid) == config.shortest_times:
            logger.debug(f'原始的消息: {str(event.message)}')
            logger.debug(f"欲发送信息: {raw_message}")
            await bot.send_group_msg(group_id=event.group_id, message=raw_message, auto_escape=False)
        last_message[gid] = message
