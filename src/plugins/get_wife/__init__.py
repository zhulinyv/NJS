import asyncio
from random import choice
from nonebot.plugin.on import on_command
from nonebot.adapters.onebot.v11 import Bot,  GroupMessageEvent
from nonebot.adapters.onebot.v11.helpers import Cooldown
from nonebot.adapters.onebot.v11.message import MessageSegment
import random
from base64 import b64encode
from PIL import Image
import io
import os
from pathlib import Path
random.seed(1)
from .json_manager import read_json, remove_json, write_json
cdTime = 3600

get_wife = on_command("抽老婆", aliases={"选妃"}, priority=10, block=True)

sendmessage = [
    "醒醒你没有老婆",
    "连美少女都想让他当你老婆吗？",
    "肥宅好好看清楚你自己啊！",
    "肥宅也配选老婆？",
    "喂喂喂！清醒清醒！谁要当你老婆啊",
    "肥宅就应该孤独一生啊"
]

@get_wife.handle()
async def _get_wife(bot: Bot, event: GroupMessageEvent):
    qid = event.get_user_id()
    data = read_json()
    mid = event.message_id
    try:
        cd = event.time - data[qid][0]
    except Exception:
        cd = cdTime + 1
    if(cd > cdTime):
        write_json(qid, event.time, mid, data)
        if(random.random() < 0.3):
            await get_wife.finish(message=f"{random.choice(sendmessage)}"+MessageSegment.image(Path(os.path.join(os.path.dirname(__file__), "resource")) / "img.jpg"))

        user_id = event.get_user_id()
        group_id = event.group_id
        req_user_info: dict = await bot.get_group_member_info(
            group_id=group_id, user_id=int(user_id)
        )
        req_user_card = req_user_info["card"]
        if not req_user_card:
            req_user_card = req_user_info["nickname"]
        req_user_sex = req_user_info["sex"]
        is_nick = "老婆" if req_user_sex == "male" else "老公"
        repo_0 = f"现在人家将随机抽取一位幸运裙友\n成为{req_user_card}的{is_nick}！"
        await bot.send(event, repo_0)
        await asyncio.sleep(5)

        # 获取群成员列表
        prep_list = await bot.get_group_member_list(group_id=group_id)
        prep_list = [prep.get("user_id", 114514) for prep in prep_list]

        # 随机抽取群友
        lucky_user = choice(prep_list)
        lucky_user_info: dict = await bot.get_group_member_info(
            group_id=group_id, user_id=lucky_user
        )

        # 获取幸运群友信息
        lucky_user_card = lucky_user_info["card"]
        if not lucky_user_card:
            lucky_user_card = lucky_user_info["nickname"]

        url = f"http://q1.qlogo.cn/g?b=qq&nk={lucky_user}&s=640"

        repo_1 = (
            f"好欸！{lucky_user_card}({lucky_user}) \n"
        )
        repo_2 = (
            f" 成为了 {req_user_card}({user_id}) 的 {is_nick}"
        )
        await get_wife.finish(repo_1+MessageSegment.image(url)+repo_2)
    else:
        time_last = cdTime - cd
        hours, minutes, seconds = 0, 0, 0
        if time_last >= 60:
            minutes, seconds = divmod(time_last, 60)
            hours, minutes = divmod(minutes, 60)
        else:
            seconds = time_last
        cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"

        await get_wife.send(f"你选妃的CD还有{cd_msg}", at_sender=True)
