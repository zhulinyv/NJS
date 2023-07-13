import asyncio
import contextlib
import random
import time
from re import sub
from typing import Tuple

import nonebot
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import RegexGroup

from .get_data import get_data
from .permission_manager import pm
from .setu_message import setu_sendmessage


class SendSetu:
    def __init__(self) -> None:
        ...
        # ⡆⣐⢕⢕⢕⢕⢕⢕⢕⢕⠅⢗⢕⢕⢕⢕⢕⢕⢕⠕⠕⢕⢕⢕⢕⢕⢕⢕⢕⢕
        # ⢐⢕⢕⢕⢕⢕⣕⢕⢕⠕⠁⢕⢕⢕⢕⢕⢕⢕⢕⠅⡄⢕⢕⢕⢕⢕⢕⢕⢕⢕
        # ⢕⢕⢕⢕⢕⠅⢗⢕⠕⣠⠄⣗⢕⢕⠕⢕⢕⢕⠕⢠⣿⠐⢕⢕⢕⠑⢕⢕⠵⢕
        # ⢕⢕⢕⢕⠁⢜⠕⢁⣴⣿⡇⢓⢕⢵⢐⢕⢕⠕⢁⣾⢿⣧⠑⢕⢕⠄⢑⢕⠅⢕
        # ⢕⢕⠵⢁⠔⢁⣤⣤⣶⣶⣶⡐⣕⢽⠐⢕⠕⣡⣾⣶⣶⣶⣤⡁⢓⢕⠄⢑⢅⢑
        # ⠍⣧⠄⣶⣾⣿⣿⣿⣿⣿⣿⣷⣔⢕⢄⢡⣾⣿⣿⣿⣿⣿⣿⣿⣦⡑⢕⢤⠱⢐
        # ⢠⢕⠅⣾⣿⠋⢿⣿⣿⣿⠉⣿⣿⣷⣦⣶⣽⣿⣿⠈⣿⣿⣿⣿⠏⢹⣷⣷⡅⢐
        # ⣔⢕⢥⢻⣿⡀⠈⠛⠛⠁⢠⣿⣿⣿⣿⣿⣿⣿⣿⡀⠈⠛⠛⠁⠄⣼⣿⣿⡇⢔
        # ⢕⢕⢽⢸⢟⢟⢖⢖⢤⣶⡟⢻⣿⡿⠻⣿⣿⡟⢀⣿⣦⢤⢤⢔⢞⢿⢿⣿⠁⢕
        # ⢕⢕⠅⣐⢕⢕⢕⢕⢕⣿⣿⡄⠛⢀⣦⠈⠛⢁⣼⣿⢗⢕⢕⢕⢕⢕⢕⡏⣘⢕
        # ⢕⢕⠅⢓⣕⣕⣕⣕⣵⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣷⣕⢕⢕⢕⢕⡵⢀⢕⢕
        # ⢑⢕⠃⡈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢃⢕⢕⢕
        # ⣆⢕⠄⢱⣄⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢁⢕⢕⠕⢁
        # ⣿⣦⡀⣿⣿⣷⣶⣬⣍⣛⣛⣛⡛⠿⠿⠿⠛⠛⢛⣛⣉⣭⣤⣂⢜⠕⢑⣡⣴⣿

    @staticmethod
    def session_id(event: MessageEvent) -> str:
        """根据会话类型生成session_id, 一般返回str而不是None, 一般消息事件不是私聊就是群聊"""
        if isinstance(event, GroupMessageEvent):
            return f"group_{str(event.group_id)}"
        else:
            return f"user_{str(event.user_id)}"

    @staticmethod
    async def setu_handle(
        bot: Bot, matcher: Matcher, event: MessageEvent, args: Tuple = RegexGroup()
    ) -> None:  # sourcery skip: low-code-quality
        """发送色图的处理函数"""
        # 获取用户输入的参数
        r18flag = args[2]
        key = sub("['\"]", "", args[3])  # 去掉引号防止sql注入
        num = int(sub(r"[张|个|份|x|✖️|×|X|*]", "", args[1])) if args[1] else 1

        # 根据会话类型生成session_id
        if isinstance(event, GroupMessageEvent):
            session_id = f"group_{str(event.group_id)}"
            user_type = "group"
        else:
            session_id = f"user_{str(event.user_id)}"
            user_type = "private"

        # 权限检查
        try:
            user_type = (
                "SU"
                if (str(event.user_id) in nonebot.get_driver().config.superusers)
                else user_type
            )
            r18, num, withdraw_time = pm.check_permission(
                session_id, r18flag, num, user_type
            )
        except PermissionError as e:
            await matcher.finish(str(e), at_sender=True)

        # 色图图片质量, 如果num为3-6质量为70,如果num为7-max质量为50,其余为95(图片质量太高发起来太费时间了)
        # quality = 95就是原图
        if num >= 3 and num <= 6:
            quality = 70
        elif num >= 7:
            quality = 50
        else:
            quality = 95
        if num >= 3:
            await matcher.send(
                f"由于数量过多请等待\n当前图片质量为{quality}\n3-6:quality = 70\n7+:quality = 50"
            )

        # key按照空格切割为数组, 用于多关键词搜索, 并且把数组中的空元素去掉
        key = key.split(" ")
        key = [word.strip() for word in key if word.strip()]

        # 控制台输出
        flag_log = f"\nR18 == {str(r18)}\nkeyword == {key}\nnum == {num}\n"
        logger.info(f"key = {key}\tr18 = {r18}\tnum = {num}")
        # 记录时间, 计算CD用
        pm.update_last_send(session_id)

        # data是数组套娃, 数组中的每个元素内容为: [图片, 信息, True/False, url]
        try:
            data = await get_data.get_setu(matcher, key, num, r18, quality)
        except Exception as e:
            await matcher.finish(repr(e), at_sender=True)

        # 发送的消息列表
        message_list = []
        for pic in data:
            # 如果状态为True,说明图片拿到了
            if pic[2]:
                message = (
                    f"{random.choice(setu_sendmessage)}{flag_log}"
                    + Message(pic[1])
                    + MessageSegment.image(pic[0])
                )  # type: ignore
                message_list.append(message)
                flag_log = ""
            # 状态为false的消息,图片没拿到
            else:
                message = pic[0] + pic[1]
                message_list.append(message)

        # 为后面撤回消息做准备
        setu_msg_id = []

        # 尝试发送
        try:
            start_time = time.time()  # 记录开始发送的时间
            if isinstance(event, PrivateMessageEvent):
                # 私聊直接发送
                for msg in message_list:
                    setu_msg_id.append((await matcher.send(msg))["message_id"])
                    await asyncio.sleep(0.5)
            elif isinstance(event, GroupMessageEvent):
                msgs = [
                    {
                        "type": "node",
                        "data": {
                            "name": "setu-bot",
                            "uin": bot.self_id,
                            "content": msg,
                        },
                    }
                    for msg in message_list
                ]
                # 发送转发消息, 并且记录消息id, 撤回用
                setu_msg_id.append(
                    (
                        await bot.call_api(
                            "send_group_forward_msg",
                            group_id=event.group_id,
                            messages=msgs,
                        )
                    )["message_id"]
                )
        except Exception as e:
            logger.warning(repr(e))
            await matcher.finish(
                message=Message(f"消息可能被风控了，图发不出来，错误信息{repr(e)}"),
                at_sender=True,
            )

        # 自动撤回涩图
        if withdraw_time != 0:
            with contextlib.suppress(Exception):
                time_left = (
                    withdraw_time + start_time - time.time()
                )  # 计算从开始发送到目前仍剩余的保留时间
                await asyncio.sleep(1 if time_left <= 0 else time_left)
                for msg_id in setu_msg_id:
                    await bot.delete_msg(message_id=msg_id)


send_setu = SendSetu()
