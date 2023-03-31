from nonebot import get_bot, get_bots, get_driver
from nonebot.log import logger
from pydantic import BaseModel, Extra
from nonebot.adapters import Bot
from typing import Optional, List, Dict, Tuple


class Config(BaseModel, extra=Extra.ignore):
    # 机器人的QQ号（如果写了就按优先级响应，否则就第一个连上的响应） ['1234','5678','6666']
    easy_translate_bot_qqnum_list: List[str] = []  # 可选


class Var:
    # 处理消息的bot
    handle_bot: Optional[Bot] = None


driver = get_driver()

pc = Config.parse_obj(driver.config)
var = Var()

# qq机器人连接时执行
@driver.on_bot_connect
async def on_bot_connect(bot: Bot):
    # 是否有写bot qq，如果写了只处理bot qq在列表里的
    if (
        pc.easy_translate_bot_qqnum_list
        and bot.self_id in pc.easy_translate_bot_qqnum_list
    ):
        # 如果已经有bot连了
        if var.handle_bot:
            # 当前bot qq 下标
            handle_bot_id_index = pc.easy_translate_bot_qqnum_list.index(
                var.handle_bot.self_id
            )
            # 连过俩的bot qq 下标
            new_bot_id_index = pc.easy_translate_bot_qqnum_list.index(bot.self_id)
            # 判断优先级，下标越低优先级越高
            if new_bot_id_index < handle_bot_id_index:
                var.handle_bot = bot

        # 没bot连就直接给
        else:
            var.handle_bot = bot

    # 不写就给第一个连的
    elif not var.handle_bot:
        var.handle_bot = bot


# qq机器人断开时执行
@driver.on_bot_disconnect
async def on_bot_disconnect(bot: Bot):
    # 判断掉线的是否为handle bot
    if bot == var.handle_bot:
        # 如果有写bot qq列表
        if pc.easy_translate_bot_qqnum_list:
            # 获取当前连着的bot列表(需要bot是在bot qq列表里)
            available_bot_id_list = [
                bot_id
                for bot_id in get_bots()
                if bot_id in pc.easy_translate_bot_qqnum_list
            ]
            if available_bot_id_list:
                # 打擂台排序？
                new_bot_index = pc.easy_translate_bot_qqnum_list.index(
                    available_bot_id_list[0]
                )
                for bot_id in available_bot_id_list:
                    now_bot_index = pc.easy_translate_bot_qqnum_list.index(bot_id)
                    if now_bot_index < new_bot_index:
                        new_bot_index = now_bot_index
                # 取下标在qq列表里最小的bot qq为新的handle bot
                var.handle_bot = get_bot(
                    pc.easy_translate_bot_qqnum_list[new_bot_index]
                )
            else:
                var.handle_bot = None

        # 不写就随便给一个连着的(如果有)
        elif var.handle_bot:
            try:
                new_bot = get_bot()
                var.handle_bot = new_bot
            except ValueError:
                var.handle_bot = None
