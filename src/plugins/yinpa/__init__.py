import os
import random
import nonebot
import asyncio
from re import I
from pathlib import Path
from random import choice
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.plugin.on import on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message

# ------------------------------ 一些容器 ----------------------------------------------------
cdTime = 3600    # 分手后需要cdTime秒才能再次开始配对                                          |
cd_time = 1      # 几乎没有了
cd_dir = {}      # cd_dir存储配对的QQ号和时间戳         {qq:time}                             |
wife_dir = {}    # wife_dir存储配对的对象               {qq:[qq,nickname1,nickname2]}         |
ejaculation_CD={} # 射精CD                                                                   |
# -------------------------------------------------------------------------------------------



# ------------------------------- 响应器部分 --------------------------------------------------
get_wife = on_command(                                                                      #|
    "抽老婆", aliases={"选妃"}, priority=10, block=True)              #|
break_up = on_command("分手", priority=10, block=True)                    #|
"""yin_pa = on_regex(r"^(透|日群主|透群主|日管理|透管理)",                             #|
                  flags=I, priority=30, block=True)   """                                     #|
yin_pa = on_command("透", priority=30, block=True)
# -------------------------------------------------------------------------------------------


sendmessage = [
    "醒醒你没有老婆",
    "神经病，凡是美少女都想让他当你老婆吗？",
    "死肥猪好好看清楚你自己啊！",
    "死肥宅也配选老婆？",
    "喂喂喂！清醒清醒！谁要当你老婆啊",
    "死肥宅就应该孤独一生啊"
]

@break_up.handle()
async def _(event: GroupMessageEvent):
    qid = event.user_id
    if qid in wife_dir:
        reply = f"坏欸, {wife_dir[qid][1]}({qid}) 与 {wife_dir[qid][2]}({wife_dir[qid][0]})分手了"
        wife_dir.pop(qid)
        await break_up.send(reply)
    else:
        await break_up.send('你都没对象你和谁分手呢?')

@get_wife.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qid = event.user_id                    # 用户ID
    group_id = event.group_id              # 群ID
    await pretreatment(event, qid)         # 前置处理
    req_user_card = await get_user_card(bot, group_id,qid)       # 请求者的昵称

    # 获取群成员列表
    prep_list = await bot.get_group_member_list(group_id=group_id)
    prep_list = [prep.get("user_id", 114514) for prep in prep_list]
    prep_list.remove(qid)
    # 随机抽取幸运成员
    lucky_user = choice(prep_list)
    lucky_user_card = await get_user_card(bot, group_id, lucky_user)
    # sleep三秒
    repo_0 = f"现在咱将随机抽取一位幸运裙友\n成为{req_user_card}的老婆！"
    await get_wife.send(repo_0)
    await asyncio.sleep(3)
    # 构造消息
    url = f"http://q1.qlogo.cn/g?b=qq&nk={lucky_user}&s=640"
    repo_1 = f"好欸！{lucky_user_card}({lucky_user}) \n"
    repo_2 = f" 成为了 {req_user_card}({qid}) 的老婆" 
    wife_dir.update({qid: [lucky_user, req_user_card, lucky_user_card]})
    cd_dir.update({qid: event.time})
    await get_wife.finish(repo_1 + MessageSegment.image(url) + repo_2)


@yin_pa.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, msg: Message = CommandArg()):
    qid = event.user_id                    # 用户ID
    group_id = event.group_id              # 群ID
    # 获取用户输入的参数
    """不会用，换掉了（"""
    # args = list(state["_matched_groups"])
    # command = args[0]
    # CD处理
    try:
        cd = event.time - ejaculation_CD[qid]
    except KeyError:
        cd = cd_time + 1
    if cd > cd_time or event.get_user_id() in nonebot.get_driver().config.superusers:
        ejaculation_CD.update({qid: event.time})
        req_user_card = await get_user_card(bot, group_id,qid)       # 请求者的昵称 
        # 获取群成员列表
        prep_list = await bot.get_group_member_list(group_id=group_id)
        # 被透的成员身份
        who = msg.extract_plain_text().strip()

        if who == "群主":
            for prep in prep_list:
                if prep['role']=='owner':
                    lucky_user = prep['user_id']
                    break
            if int(lucky_user) == qid:
                await yin_pa.finish("你透你自己?")
            # await yin_pa.send(f"现在咱将把群主\n送给{req_user_card}色色！")
        elif who == "管理":
            admin_id = []
            for prep in prep_list:
                if prep['role']=='admin':
                    group_admin_id = prep['user_id']
                    admin_id.append(group_admin_id)
            if qid in admin_id:
                admin_id.remove(qid)
            if admin_id==[]:
                await yin_pa.finish("喵喵喵? 找不到群管理!")
            lucky_user = choice(admin_id)
            # await yin_pa.send(f"现在咱将随机抽取一位幸运管理\n送给{req_user_card}色色！")
        elif who == "自己":
            await yin_pa.finish("你透你自己? 还是找个人来帮忙叭🤣👉")
        else:
            prep_list = [prep.get("user_id", 114514) for prep in prep_list]
            target = await get_at(event)
            probability = random.random()
            if probability < 0.15:
                await yin_pa.finish("冲不出来啦，休息一下叭＞﹏＜", at_sender=True)
            elif probability < 0.3:
                semen = round(random.uniform(0, 2), 3)
                await yin_pa.finish(f"行不行吖，小细狗🐕，才出来{semen}毫升,,ԾㅂԾ,,", at_sender=True)
            elif probability < 0.85:
                if target == None:
                    # 随机抽取幸运成员
                    prep_list.remove(qid)
                    lucky_user = choice(prep_list)
                    # await yin_pa.send(f"现在咱将随机抽取一位幸运裙友\n送给{req_user_card}色色！")
                else:
                    lucky_user = target
            else:
                lucky_user = target
                lucky_user_card = await get_user_card(bot, group_id, lucky_user)
                await yin_pa.finish(f"Hen...Hentai! 你怎么能对『{lucky_user_card}』🐍这么多！！", at_sender=True)
        
        lucky_user_card = await get_user_card(bot, group_id, lucky_user)
        # 休眠
        fuckingTime = random.randint(1,300)
        """砍掉了，有点太过真实（"""
        # await asyncio.sleep(fuckingTime)

        # 容量
        capacity = random.uniform(2,6)
        url = f"http://q1.qlogo.cn/g?b=qq&nk={lucky_user}&s=640"
        repo_1 = f"好欸!『{req_user_card}』用时{fuckingTime}秒 \n给『{lucky_user_card}』注入了{round(capacity,3)}毫升的脱氧核糖核酸"
        await yin_pa.send(repo_1 + MessageSegment.image(url))
    else:
        await yin_pa.finish(f"你已经榨不出来任何东西了\nCD剩余时间：{round(cd_time - cd,3)}s")
                



async def get_user_card(bot: Bot, group_id, qid):
    # 返还用户nickname
    user_info: dict = await bot.get_group_member_info(group_id=group_id, user_id=qid)
    user_card = user_info["card"]
    if not user_card:
        user_card = user_info["nickname"]
    return user_card


async def pretreatment(event: GroupMessageEvent, qid: int):
    # 如果有对象了的话，就不能再次配对
    if qid in wife_dir:
        url = f"http://q1.qlogo.cn/g?b=qq&nk={wife_dir[qid][0]}&s=640"
        head_portrait = MessageSegment.image(url)
        await get_wife.finish(f"你当前亲爱的是{wife_dir[qid][2]}({wife_dir[qid][0]})"+head_portrait+"进行新的配对需要先分手", at_sender=True)
    await CD_check(event, qid)
    # random一下准备挨骂吧!
    if(random.random() < 0.3):
        await get_wife.finish(message=f"{random.choice(sendmessage)}"+MessageSegment.image(Path(os.path.join(os.path.dirname(__file__), "resource")) / "img.jpg"))


async def CD_check(event: GroupMessageEvent, qid: int):
    # cd处理部分
    try:
        cd = event.time - cd_dir[qid]
    except KeyError:
        cd = cdTime + 1
    if cd < cdTime:
        time_last = cdTime - cd
        hours, minutes, seconds = 0, 0, 0
        if time_last >= 60:
            minutes, seconds = divmod(time_last, 60)
            hours, minutes = divmod(minutes, 60)
        else:
            seconds = time_last
        cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"
        await get_wife.finish(f"臭东西！你换对象的CD还有{cd_msg}", at_sender=True)



async def get_at(event: GroupMessageEvent) -> int:
    msg=event.get_message()
    for msg_seg in msg:
        if msg_seg.type == "at":
            return int(msg_seg.data["qq"])

