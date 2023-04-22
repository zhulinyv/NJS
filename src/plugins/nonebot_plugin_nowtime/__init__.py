from nonebot.plugin import on_regex
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.params import Matcher, RegexGroup
from nonebot import require,get_bot,get_driver
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
    GroupMessageEvent,
    ActionFailed,
)
from nonebot.log import logger
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from .config import Config
import asyncio
import aiofiles
import os
import json
import requests


config_path = Path("config/nowtime.json")
config_path.parent.mkdir(parents=True, exist_ok=True)
if config_path.exists():
    with open(config_path, "r", encoding="utf8") as f:
        CONFIG: Dict[str, List] = json.load(f)
else:
    CONFIG: Dict[str, List] = {"opened_groups": []}
    with open(config_path, "w", encoding="utf8") as f:
        json.dump(CONFIG, f, ensure_ascii=False, indent=4)

try:
    scheduler = require("nonebot_plugin_apscheduler").scheduler
except Exception:
    scheduler = None




time_now = on_regex(r"(现在|当前|北京)时间", block=True, priority=5)
trun_on_nowtime = on_regex(r"^(开启|关闭)整点报时([0-9]*)$", priority=99, block=True, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
list_matcher = on_regex(r"^查看整点报时列表$", priority=99, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@time_now.handle()
async def _():
    await time_now.send(message = "正在查看当前时间……")
    get_json = requests.get(url='https://v.api.aa1.cn/api/time-tx/index.php',timeout=30)
    get_msg = json.loads(get_json.text)
    msg = (f"⭐{get_msg['msg']}⭐\n"
    +f"\n现在是北京时间:\n{get_msg['nowtime']}"
    +f"送你一句：\n⭐{get_msg['nxyj']}⭐"
    )
    await time_now.send(message=(msg))

@list_matcher.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    if not scheduler:
        await matcher.finish("未安装软依赖nonebot_plugin_apscheduler，不能使用定时发送功能")
    msg = "当前打开整点报时的群聊有：\n"
    for group_id in CONFIG["opened_groups"]:
        msg += f"{group_id}\n"
    await matcher.finish(msg.strip())

#为群聊添加整点报时
@trun_on_nowtime.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    args: Tuple[Optional[str], ...] = RegexGroup(),
):
    if not scheduler:
        await matcher.finish("未安装软依赖nonebot_plugin_apscheduler，不能使用定时发送功能")
    mode = args[0]
    if isinstance(event, GroupMessageEvent):
        group_id = args[1] if args[1] else str(event.group_id)
    else:
        if args[1]:
            group_id = args[1]
        else:
            await matcher.finish("私聊开关需要输入指定群号")
    if mode == "开启":
        if group_id in CONFIG["opened_groups"]:
            await matcher.finish("该群已经开启，无需重复开启")
        else:
            CONFIG["opened_groups"].append(group_id)
    else:
        if group_id in CONFIG["opened_groups"]:
            CONFIG["opened_groups"].remove(group_id)
        else:
            await matcher.finish("该群尚未开启，无需关闭")
    async with asyncio.Lock():
        async with aiofiles.open(config_path, "w", encoding="utf8") as f:
            await f.write(json.dumps(CONFIG, ensure_ascii=False, indent=4))
    await matcher.finish(f"已成功{mode}{group_id}的整点报时")

#读取配置的开始和结束时间
star_time = Config.parse_obj(get_driver().config.dict()).start_time
end_time = Config.parse_obj(get_driver().config.dict()).end_time

#发送报时
async def post_scheduler():
    bot: Bot = get_bot()
    delay = 2 * 0.5
    if datetime.now().hour in range(star_time,end_time):   
        for group_id in CONFIG["opened_groups"]:
            try:
            #整点语音
                url = 'https://v.api.aa1.cn/api/api-baoshi/data/baoshi/'
                url = url +str(datetime.now().hour)+ '.mp3'
                record = MessageSegment.record(url)
                await bot.send_group_msg(group_id=int(group_id), message=record)
            except ActionFailed as e:
                logger.warning(f'{repr(e)}')
            await asyncio.sleep(delay)
            try:
                msg = await get_word_result()
                await bot.send_group_msg(group_id=int(group_id), message= msg) 
            except ActionFailed as e:
                logger.warning(f"定时发送整点报时到 {group_id} 失败，可能是风控或机器人不在该群聊 {repr(e)}")
            await asyncio.sleep(delay)



#加载整点报时词库
words_for_time = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "resource")) / "time_words.json", "r", encoding="utf8"))

#匹配词库
async def get_word_result() -> str:
    keys = words_for_time.keys()
    for key in keys:
        try:
            if int(datetime.now().hour) == int(key):
                return words_for_time[key]
        except: 
            return '整点报时出错了！'


#添加定时任务
try:
    scheduler.add_job(
        post_scheduler, "cron", hour='*', id="everyday_nowtime"
    )
except ActionFailed as e:
    logger.warning(f"定时任务添加失败，{repr(e)}")   

