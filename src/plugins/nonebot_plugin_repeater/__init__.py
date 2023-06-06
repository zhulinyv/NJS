import re

from nonebot import on_message, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from . import config

repeater_group = config.repeater_group
shortest = config.shortest_length
blacklist = config.blacklist

m = on_message(priority=10, block=False)

last_message = {}
message_times = {}


# 消息预处理
def message_preprocess(message: str):
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
    # 检查是否在黑名单中
    if event.raw_message in blacklist:
        logger.debug(f'[复读姬] 检测到黑名单消息: {event.raw_message}')
        return
    gid = str(event.group_id)
    if gid in repeater_group or "all" in repeater_group:
        global last_message, message_times
        message, raw_message = message_preprocess(str(event.message))
        logger.debug(f'[复读姬] 这一次消息: {message}')
        logger.debug(f'[复读姬] 上一次消息: {last_message.get(gid)}')
        if last_message.get(gid) != message:
            message_times[gid] = 1
        else:
            message_times[gid] += 1
        logger.debug(f'[复读姬] 已重复次数: {message_times.get(gid)}/{config.shortest_times}')
        if message_times.get(gid) == config.shortest_times:
            logger.debug(f'[复读姬] 原始的消息: {str(event.message)}')
            logger.debug(f"[复读姬] 欲发送信息: {raw_message}")
            await bot.send_group_msg(group_id=event.group_id, message=raw_message, auto_escape=False)
        last_message[gid] = message
