from nonebot.plugin.on import on_command, on_message
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    GROUP_ADMIN,
    GROUP_OWNER,
    Bot,
    GroupMessageEvent,
    Message,
    MessageSegment,
)

import nonebot
import os
import random
import asyncio
import time

from pathlib import Path

from .utils import *
from .config import Config

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="娶群友", description="娶群友", usage="娶群友", config=Config, extra={}
)

# 加载全局配置
global_config = nonebot.get_driver().config
waifu_config = Config.parse_obj(global_config.dict())
waifu_cd_bye = waifu_config.waifu_cd_bye
waifu_save = waifu_config.waifu_save
waifu_reset = waifu_config.waifu_reset
last_sent_time_filter = waifu_config.waifu_last_sent_time_filter
HE = waifu_config.waifu_he
BE = HE + waifu_config.waifu_be
NTR = waifu_config.waifu_ntr
yinpa_HE = waifu_config.yinpa_he
yinpa_BE = yinpa_HE + waifu_config.yinpa_be
yinpa_CP = waifu_config.yinpa_cp
yinpa_CP = yinpa_HE if yinpa_CP == 0 else yinpa_CP

waifu_file = Path() / "data" / "waifu"

if not waifu_file.exists():
    os.makedirs(waifu_file)

record_CP_file = waifu_file / "record_CP"

if record_CP_file.exists():
    with open(record_CP_file, "r") as f:
        line = f.read()
        record_CP = eval(line)
else:
    record_CP = {}

record_waifu_file = waifu_file / "record_waifu"
if record_waifu_file.exists():
    with open(record_waifu_file, "r") as f:
        line = f.read()
        record_waifu = eval(line)
else:
    record_waifu = {}

record_lock_file = waifu_file / "record_lock"
if record_lock_file.exists():
    with open(record_lock_file, "r") as f:
        line = f.read()
        record_lock = eval(line)
else:
    record_lock = {}

record_yinpa1_file = waifu_file / "record_yinpa1"
if record_yinpa1_file.exists():
    with open(record_yinpa1_file, "r") as f:
        line = f.read()
        record_yinpa1 = eval(line)
else:
    record_yinpa1 = {}
record_yinpa2_file = waifu_file / "record_yinpa2"
if record_yinpa2_file.exists():
    with open(record_yinpa2_file, "r") as f:
        line = f.read()
        record_yinpa2 = eval(line)
else:
    record_yinpa2 = {}


if waifu_save:

    def save(file, data):
        with open(file, "w", encoding="utf8") as f:
            f.write(str(data))

else:

    def save(file, data):
        pass


from nonebot import require

scheduler = require("nonebot_plugin_apscheduler").scheduler

if waifu_reset:
    # 判断文件时效
    timestr = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    timeArray = time.strptime(timestr, "%Y-%m-%d")
    Zero_today = time.mktime(timeArray)

    if record_CP_file.exists() and os.path.getmtime(record_CP_file) < Zero_today:
        record_CP = {}
    if record_waifu_file.exists() and os.path.getmtime(record_waifu_file) > Zero_today:
        record_waifu = {}
    if record_lock_file.exists() and os.path.getmtime(record_lock_file) > Zero_today:
        record_lock = {}
    if (
        record_yinpa1_file.exists()
        and os.path.getmtime(record_yinpa1_file) > Zero_today
    ):
        record_yinpa1 = {}
    if (
        record_yinpa2_file.exists()
        and os.path.getmtime(record_yinpa2_file) > Zero_today
    ):
        record_yinpa2 = {}

    # 重置记录
    def reset_record():
        global record_CP, record_waifu, record_lock, record_yinpa1, record_yinpa2
        record_CP = {}
        record_waifu = {}
        record_lock = {}
        record_yinpa1 = {}
        record_yinpa2 = {}

else:
    # 重置记录
    def reset_record():
        global record_CP, record_yinpa1, record_yinpa2
        for group_id in record_CP:
            for user_id in record_CP[group_id]:
                if record_CP[group_id][user_id] == user_id:
                    record_CP[group_id][user_id] = 0
        record_yinpa1 = {}
        record_yinpa2 = {}


on_command("重置记录", priority=80, block=True).append_handler(reset_record)
scheduler.add_job(reset_record, "cron", hour=0, misfire_grace_time=120)

protect_list_file = waifu_file / "list_protect"
if protect_list_file.exists():
    with open(protect_list_file, "r") as f:
        line = f.read()
        protect_list = eval(line)
else:
    protect_list = {}

# 设置保护名单

protect = on_command("娶群友保护", priority=80, block=True)


@protect.handle()
async def _(
    bot: Bot, event: GroupMessageEvent, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
):
    group_id = event.group_id
    protect_set = protect_list.setdefault(group_id, set())
    at = get_message_at(event.message)
    if not at:
        protect_set.add(event.user_id)
        save(protect_list_file, protect_list)
        await protect.finish("保护成功！", at_sender=True)
    elif await permission(bot, event):
        protect_set.update(set(at))
        namelist = "\n".join(
            [
                (member["card"] or member["nickname"])
                for user_id in at
                if (
                    member := await bot.get_group_member_info(
                        group_id=group_id, user_id=user_id
                    )
                )
            ]
        )
        save(protect_list_file, protect_list)
        await protect.finish(f"保护成功！\n保护名单为：\n{namelist}", at_sender=True)
    else:
        await protect.finish("保护失败。你无法为其他人设置保护。", at_sender=True)


# 移出保护名单

unprotect = on_command("解除娶群友保护", priority=80, block=True)


@unprotect.handle()
async def _(
    bot: Bot, event: GroupMessageEvent, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
):
    group_id = event.group_id
    protect_set = protect_list.setdefault(group_id, set())
    at = get_message_at(event.message)
    if not at:
        user_id = event.user_id
        if user_id in protect_set:
            protect_set.discard(user_id)
            save(protect_list_file, protect_list)
            await unprotect.finish("解除保护成功！", at_sender=True)
        else:
            await unprotect.finish("你不在保护名单内。", at_sender=True)
    elif await permission(bot, event):
        valid_at = protect_set & set(at)
        if not valid_at:
            await unprotect.finish("保护名单内不存在指定成员。", at_sender=True)
        protect_set -= valid_at
        save(protect_list_file, protect_list)
        namelist = "\n".join(
            [
                (member["card"] or member["nickname"])
                for user_id in valid_at
                if (
                    member := await bot.get_group_member_info(
                        group_id=group_id, user_id=user_id
                    )
                )
            ]
        )
        await unprotect.finish(f"解除保护成功！\n解除保护名单为：\n{namelist}", at_sender=True)
    else:
        await unprotect.finish("解除保护失败。你无法为其他人解除保护。", at_sender=True)


# 查看保护名单
show_protect = on_command("查看保护名单", priority=90, block=True)


@show_protect.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    protect_set = protect_list.get(group_id)
    if not protect_set:
        await show_protect.finish("保护名单为空")
    namelist = "\n".join(
        [
            (member["card"] or member["nickname"])
            for user_id in protect_set
            if (
                member := await bot.get_group_member_info(
                    group_id=group_id, user_id=user_id
                )
            )
        ]
    )
    await show_protect.finish(MessageSegment.image(text_to_png(f"保护名单为：\n{namelist}")))


# 娶群友

no_waifu = [
    "你没有娶到群友，强者注定孤独，加油！",
    "找不到对象.jpg",
    "雪花飘飘北风萧萧～天地一片苍茫。",
    "要不等着分配一个对象？",
    "恭喜伱没有娶到老婆~",
    "さんが群友で結婚するであろうヒロインは、\n『自分の左手』です！",
    "醒醒，伱没有老婆。",
    "哈哈哈哈哈哈哈哈哈",
    "智者不入爱河，建设美丽中国。",
    "智者不入爱河，我们终成富婆",
    "智者不入爱河，寡王一路硕博",
]

happy_end = [
    "好耶~",
    "婚礼？启动！",
    "需要咱主持婚礼吗qwq",
    "不许秀恩爱！",
    "(响起婚礼进行曲♪)",
    "比翼从此添双翅，连理于今有合枝。\n琴瑟和鸣鸳鸯栖，同心结结永相系。",
    "金玉良缘，天作之合，郎才女貌，喜结同心。",
    "繁花簇锦迎新人，车水马龙贺新婚。",
    "乾坤和乐，燕尔新婚。",
    "愿天下有情人终成眷属。",
    "花团锦绣色彩艳，嘉宾满堂话语喧。",
    "火树银花不夜天，春归画栋双栖燕。",
    "红妆带绾同心结，碧树花开并蒂莲。",
    "一生一世两情相悦，三世尘缘四世同喜",
    "玉楼光辉花并蒂，金屋春暖月初圆。",
    "笙韵谱成同生梦，烛光笑对含羞人。",
    "祝你们百年好合,白头到老。",
    "祝你们生八个。",
]


async def waifu_rule(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    """
    规则：娶群友
    """
    msg = event.message.extract_plain_text()
    if not msg.startswith("娶群友"):
        return False
    group_id = event.group_id
    user_id = event.user_id
    protect_set = protect_list.get(group_id, set())
    if user_id in protect_set:
        return False
    at = get_message_at(event.message)
    at = at[0] if at else None
    if at in protect_set:
        return False
    tips = "伱的群友結婚对象是、"
    rec = record_CP.setdefault(group_id, {})
    if (waifu_id := rec.get(user_id)) and waifu_id != user_id:
        try:
            member = await bot.get_group_member_info(
                group_id=group_id, user_id=waifu_id
            )
        except:
            member = None
            waifu_id = user_id
        if member:
            if at and at != user_id:
                if waifu_id == at:
                    msg = (
                        "这是你的CP！"
                        + random.choice(happy_end)
                        + MessageSegment.image(file=await user_img(waifu_id))
                    )
                    if user_id in record_waifu.get(group_id, set()):
                        record_lock.setdefault(group_id, {})
                        record_lock[group_id][waifu_id] = user_id
                        record_lock[group_id][user_id] = waifu_id
                        save(record_lock_file, record_lock)
                        msg += "\ncp已锁！"
                else:
                    msg = (
                        "你已经有CP了，不许花心哦~"
                        + MessageSegment.image(file=await user_img(waifu_id))
                        + f"你的CP：{member['card'] or member['nickname']}"
                    )
            else:
                msg = (
                    tips
                    + MessageSegment.image(file=await user_img(waifu_id))
                    + f"『{member['card'] or member['nickname']}』！"
                )
            await bot.send(event, msg, at_sender=True)
            return False

    if at:
        if at == rec.get(at):
            X = HE
            del rec[waifu_id]
        else:
            X = random.randint(1, 100)

        if 0 < X <= HE:
            waifu_id = at
            tips = "恭喜你娶到了群友!\n" + tips
        elif HE < X <= BE:
            waifu_id = user_id
        else:
            pass

    if not waifu_id:
        group_id = event.group_id
        member_list = await bot.get_group_member_list(group_id=group_id)
        lastmonth = event.time - last_sent_time_filter
        rule_out = protect_set | set(rec.keys())
        waifu_ids = [
            user_id
            for member in member_list
            if (user_id := member["user_id"]) not in rule_out
            and member["last_sent_time"] > lastmonth
        ]
        if waifu_ids:
            waifu_id = random.choice(list(waifu_ids))
        else:
            msg = "群友已经被娶光了、\n" + random.choice(no_waifu)
            await bot.send(event, msg, at_sender=True)
            return False
    state["waifu"] = waifu_id, tips
    return True


waifu = on_message(rule=waifu_rule, priority=90, block=True)


@waifu.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    group_id = event.group_id
    user_id = event.user_id
    waifu_id, tips = state["waifu"]
    if waifu_id == user_id:
        record_CP[group_id][user_id] = user_id
        save(record_CP_file, record_CP)
        await waifu.finish(random.choice(no_waifu), at_sender=True)
    rec = record_CP.setdefault(group_id, {})
    waifu_set = record_waifu.setdefault(group_id, set())
    if waifu_id in rec:
        waifu_cp = rec[waifu_id]
        member = await bot.get_group_member_info(group_id=group_id, user_id=waifu_cp)
        msg = (
            "人家已经名花有主了~"
            + MessageSegment.image(file=await user_img(waifu_cp))
            + "ta的cp："
            + (member["card"] or member["nickname"])
        )
        if waifu_id in record_lock.get(group_id, {}).keys():
            await waifu.finish(msg + "\n本对cp已锁！", at_sender=True)
        X = random.randint(1, 100)
        if X > NTR:
            record_CP[group_id][user_id] = user_id
        else:
            rec.pop(waifu_cp)
            waifu_set.discard(waifu_cp)
            await waifu.send(msg + "\n但是...", at_sender=True)
            await asyncio.sleep(1)

    record_CP[group_id][user_id] = waifu_id
    record_CP[group_id][waifu_id] = user_id
    waifu_set.add(waifu_id)
    member = await bot.get_group_member_info(group_id=group_id, user_id=waifu_id)
    msg = (
        tips
        + MessageSegment.image(file=await user_img(waifu_id))
        + f"『{(member['card'] or member['nickname'])}』！"
    )
    save(record_waifu_file, record_waifu)
    save(record_CP_file, record_CP)
    await waifu.finish(msg, at_sender=True)


# 分手
if waifu_cd_bye > -1:
    global cd_bye
    cd_bye = {}

    bye = on_command(
        "离婚",
        aliases={"分手"},
        rule=lambda event: isinstance(event, GroupMessageEvent)
        and event.group_id in record_CP
        and record_CP[event.group_id].get(event.user_id, event.user_id)
        != event.user_id,
        priority=90,
        block=True,
    )

    @bye.handle()
    async def _(event: GroupMessageEvent):
        group_id = event.group_id
        user_id = event.user_id
        cd_bye.setdefault(group_id, {})
        T, N, A = cd_bye[group_id].setdefault(user_id, [0, 0, 0])
        Now = event.time
        cd = T - Now
        if Now > T:
            cd_bye[group_id][user_id] = [Now + waifu_cd_bye, 0, 0]
            rec = record_CP[group_id]
            waifu_set = record_waifu.setdefault(group_id, set())
            waifu_id = rec[user_id]
            del rec[user_id]
            del rec[waifu_id]
            waifu_set.discard(user_id)
            waifu_set.discard(waifu_id)
            if group_id in record_lock:
                if waifu_id in record_lock[group_id]:
                    del record_lock[group_id][waifu_id]
                if user_id in record_lock[group_id]:
                    del record_lock[group_id][user_id]
                save(record_lock_file, record_lock)
            save(record_waifu_file, record_waifu)
            save(record_CP_file, record_CP)
            if random.randint(1, 2) == 1:
                await bye.finish(random.choice(("嗯。", "...", "好。", "哦。", "行。")))
            else:
                await bye.finish(Message(f"[CQ:poke,qq={event.user_id}]"))
        else:
            if A > Now:
                A = Now
                N = 0
            else:
                N += 1
            if N == 1:
                msg = f"你的cd还有{round(cd/60,1)}分钟。"
            elif N == 2:
                msg = f"你已经问过了哦~ 你的cd还有{round(cd/60,1)}分钟。"
            elif N < 6:
                T += 10
                msg = f"还问！罚时！你的cd还有{round(cd/60,1)}+10分钟。"
            elif random.randint(0, 2) == 0:
                await bye.finish("哼！")
            else:
                await bye.finish()
            cd_bye[group_id][user_id] = [T, N, A]
            await bye.finish(msg, at_sender=True)


# 查看娶群友卡池

waifu_list = on_command("查看群友卡池", aliases={"群友卡池"}, priority=90, block=True)


@waifu_list.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    member_list = await bot.get_group_member_list(group_id=group_id)
    lastmonth = event.time - last_sent_time_filter
    rule_out = protect_list.get(group_id, set()) | set(
        record_CP.get(group_id, {}).keys()
    )
    member_list = [
        member
        for member in member_list
        if member["user_id"] not in rule_out and member["last_sent_time"] > lastmonth
    ]
    member_list.sort(key=lambda x: x["last_sent_time"], reverse=True)
    if member_list:
        msg = "卡池：\n——————————————\n"
        for member in member_list[:80]:
            msg += f"{member['card'] or member['nickname']}\n"
        await waifu_list.finish(MessageSegment.image(text_to_png(msg[:-1])))
    else:
        await waifu_list.finish("群友已经被娶光了。下次早点来吧。")


# 查看本群CP

cp_list = on_command("本群CP", aliases={"本群cp"}, priority=90, block=True)


@cp_list.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    waifu_set = record_waifu.get(group_id)
    if not waifu_set:
        await cp_list.finish("本群暂无cp哦~")
    rec = record_CP.get(group_id)
    msg = ""
    for waifu_id in waifu_set:
        user_id = rec[waifu_id]
        try:
            member = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
            niknameA = member["card"] or member["nickname"]
        except:
            niknameA = ""
        try:
            member = await bot.get_group_member_info(
                group_id=group_id, user_id=waifu_id
            )
            niknameB = member["card"] or member["nickname"]
        except:
            niknameB = ""

        msg += f"♥ {niknameA} | {niknameB}\n"
    await cp_list.finish(
        MessageSegment.image(text_to_png("本群CP：\n——————————————\n" + msg[:-1]))
    )


# 透群友
async def yinpa_rule(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    """
    规则：透群友
    """
    msg = event.message.extract_plain_text()
    if not msg.startswith("透群友"):
        return False
    group_id = event.group_id
    user_id = event.user_id
    protect_set = protect_list.get(group_id, set())
    if user_id in protect_set:
        return False
    at = get_message_at(event.message)
    yinpa_id = None
    tips = "伱的涩涩对象是、"
    if at:
        at = at[0]
        if at in protect_set:
            return False
        if at == user_id:
            msg = f"恭喜你涩到了你自己！" + MessageSegment.image(file=await user_img(user_id))
            await bot.send(event, msg, at_sender=True)
            return False
        X = random.randint(1, 100)
        if at == record_CP.get(group_id, {}).get(user_id, 0):
            if 0 < X <= yinpa_CP:
                yinpa_id = at
                tips = "恭喜你涩到了你的老婆！"
            else:
                await bot.send(event, "你的老婆拒绝和你涩涩！", at_sender=True)
                return False
        elif 0 < X <= yinpa_HE:
            yinpa_id = at
            tips = "恭喜你涩到了群友！"
        elif yinpa_HE < X <= yinpa_BE:
            yinpa_id = user_id
    if not yinpa_id:
        member_list = await bot.get_group_member_list(group_id=group_id)
        lastmonth = event.time - last_sent_time_filter
        yinpa_ids = [
            user_id
            for member in member_list
            if (user_id := member["user_id"]) not in protect_set
            and member["last_sent_time"] > lastmonth
        ]
        if yinpa_ids:
            yinpa_id = random.choice(yinpa_ids)
        else:
            return False
    state["yinpa"] = yinpa_id, tips
    return True


yinpa = on_message(rule=yinpa_rule, priority=90, block=True)


@yinpa.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    group_id = event.group_id
    user_id = event.user_id
    yinpa_id, tips = state["yinpa"]
    if yinpa_id == user_id:
        await yinpa.finish("不可以涩涩！", at_sender=True)
    else:
        record_yinpa1[user_id] = record_yinpa1.get(user_id, 0) + 1
        save(record_yinpa1_file, record_yinpa1)
        record_yinpa2[user_id] = record_yinpa2.get(yinpa_id, 0) + 1
        save(record_yinpa2_file, record_yinpa2)
        member = await bot.get_group_member_info(group_id=group_id, user_id=yinpa_id)
        msg = (
            tips
            + MessageSegment.image(file=await user_img(yinpa_id))
            + f"『{(member['card'] or member['nickname'])}』！"
        )
        await yinpa.finish(msg, at_sender=True)


# 查看涩涩记录

yinpa_list = on_command("涩涩记录", aliases={"色色记录"}, priority=90, block=True)


@yinpa_list.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    msg_list = []
    # 输出卡池
    member_list = await bot.get_group_member_list(group_id=event.group_id)
    lastmonth = event.time - last_sent_time_filter
    protect_set = protect_list.get(group_id, set())
    member_list = [
        member
        for member in member_list
        if member["user_id"] not in protect_set and member["last_sent_time"] > lastmonth
    ]
    member_list.sort(key=lambda x: x["last_sent_time"], reverse=True)
    msg = "卡池：\n——————————————\n"
    msg += "\n".join(
        [(member["card"] or member["nickname"]) for member in member_list[:80]]
    )
    msg_list.append(
        {
            "type": "node",
            "data": {
                "name": "卡池",
                "uin": event.self_id,
                "content": MessageSegment.image(text_to_png(msg)),
            },
        }
    )

    # 输出透群友记录

    record = [
        ((member["card"] or member["nickname"]), times)
        for member in member_list
        if (times := record_yinpa1.get(member["user_id"]))
    ]
    record.sort(key=lambda x: x[1], reverse=True)
    msg = "\n".join(
        [
            f"[align=left]{nickname}[/align][align=right]今日透群友 {times} 次[/align]"
            for nickname, times in record
        ]
    )
    if msg:
        msg_list.append(
            {
                "type": "node",
                "data": {
                    "name": "记录①",
                    "uin": event.self_id,
                    "content": MessageSegment.image(
                        bbcode_to_png("涩涩记录①：\n——————————————\n" + msg)
                    ),
                },
            }
        )

    # 输出被透记录

    record = [
        ((member["card"] or member["nickname"]), times)
        for member in member_list
        if (times := record_yinpa2.get(member["user_id"]))
    ]
    record.sort(key=lambda x: x[1], reverse=True)

    msg = "涩涩记录②：\n——————————————\n"
    msg = "\n".join(
        [
            f"[align=left]{nickname}[/align][align=right]今日被透 {times} 次[/align]"
            for nickname, times in record
        ]
    )
    if msg:
        msg_list.append(
            {
                "type": "node",
                "data": {
                    "name": "记录②",
                    "uin": event.self_id,
                    "content": MessageSegment.image(
                        bbcode_to_png("涩涩记录②：\n——————————————\n" + msg)
                    ),
                },
            }
        )

    await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_list)
    await yinpa_list.finish()
