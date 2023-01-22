from nonebot.plugin.on import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    GroupMessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER
    )
from nonebot.permission import SUPERUSER

from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Arg

from nonebot import logger

import asyncio
import time
import random

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from pathlib import Path

def get_message_at(data: str) -> list:
    '''
    获取at对象
    '''
    qq_list = []
    data = json.loads(data)
    try:
        for msg in data['message']:
            if msg['type'] == 'at':
                qq_list.append(int(msg['data']['qq']))
        return qq_list
    except Exception:
        return []

# 快捷禁言/解禁

path = Path() / "data" / "Focus_namelist.json"
if path.exists():
    with open(path, "r", encoding="utf8") as f:
        namelist = json.load(f)
else:
    namelist = {}

add_namelist = on_command("添加名单", rule = to_me(), permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority = 20)

@add_namelist.handle()
async def _(event: GroupMessageEvent,arg: Message = CommandArg()):
    group_id = str(event.group_id)
    at = get_message_at(event.json())
    msg = arg.extract_plain_text().strip().split()
    n = len(at)
    if n == len(msg):
        namelist.setdefault(group_id,{})
        for i in range(n):
            namelist[group_id].update({msg[i]:at[i]})
        with open(path, "w", encoding="utf8") as f:
            json.dump(namelist, f, ensure_ascii=False, indent=4)
        await add_namelist.finish("已添加")

ban = on_command("禁言", permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority = 20)

@ban.handle()
async def _(bot:Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    group_id = str(event.group_id)
    msg = arg.extract_plain_text().strip()
    namelist.setdefault(group_id,{})
    if msg in namelist[group_id].keys():
        user_id = namelist[group_id][msg]
        await bot.set_group_ban(group_id = event.group_id, user_id = user_id, duration = 3600)
    else:
        at = get_message_at(event.json())
        if at:
            for i in at:
                await bot.set_group_ban(group_id = event.group_id, user_id = i, duration = 3600)
        else:
            pass

amnesty = on_command("解封", aliases = {"解禁", "解除禁言"}, permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority = 20)

ban_list = {}

@amnesty.handle()
async def _(bot:Bot, event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
    global ban_list
    ban_list[event.group_id] = []
    member_list = await bot.get_group_member_list(group_id = event.group_id, no_cache = True)
    msg = ""
    now = time.time()
    for member in member_list:
        if member['shut_up_timestamp'] > now:
            ban_list[event.group_id].append(member['user_id'])
            nickname = member['card'] or member['nickname']
            t = int((member['shut_up_timestamp'] - now))
            td = int(t/86400)
            t -= td * 86400
            th = int(t/3600)
            t -= th * 3600
            tm = int(t/60)
            Time = ""
            Time += f" {td} 天" if td > 0 else ""
            Time += f" {th} 小时" if th > 0 or td > 0 else ""
            Time += f" {tm} 分钟"
            msg += f"{nickname} {member['user_id']}\n    -- {Time}\n"
    else:
        if ban_list[event.group_id]:
            user_id = get_message_at(event.json())

            group_id = str(event.group_id)
            namelist.setdefault(group_id,{})
            code = arg.extract_plain_text().strip()
            user = namelist[group_id].get(code)

            if user:
                user_id.append(user)

            if user_id:
                user_id_list = ""
                for i in user_id:
                    user_id_list += f"{i} "
                else:
                    matcher.set_arg("user_id", user_id_list)
            else:
                await amnesty.send("以下成员正在禁言：\n" + msg[:-1])
                await asyncio.sleep(1)
        else:
            await amnesty.finish()

@amnesty.got("user_id", prompt = "请输入要解除禁言的成员，如输入多个群成员用空格隔开。")
async def _(bot:Bot, event: GroupMessageEvent, user_id: Message = Arg()):
    user_id = str(user_id).strip().split()
    if user_id:
        for i in user_id:
            if int(i) in ban_list[event.group_id]:
                await bot.set_group_ban(group_id = event.group_id, user_id = int(i), duration = 0)

    await amnesty.finish()

global switch
switch = {}

global star, st
star = {}
st = {}

ban_game_switch_on = on_command("开启自由轮盘", aliases = {"开启无赌注轮盘"},permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER , priority = 5)
@ban_game_switch_on.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    global switch
    switch[event.group_id] = True
    logger.info("自由轮盘已开启！")
    await ban_game_switch_on.finish("自由轮盘已开启！")

ban_game_switch_off = on_command("关闭自由轮盘", aliases = {"关闭无赌注轮盘"},permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER , priority = 5)
@ban_game_switch_off.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    global switch, star, st
    switch[event.group_id] = False
    star[event.group_id] = 0
    st[event.group_id] = 0
    logger.info("自由轮盘已关闭！")
    await ban_game_switch_off.finish("自由轮盘已关闭！")

async def S(bot: Bot, event: GroupMessageEvent) -> bool:
    switch.setdefault(event.group_id,False)
    return switch[event.group_id]



ban_game = on_command("无赌注轮盘",permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER | S ,aliases = {"自由轮盘"}, priority = 5)

@ban_game.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    global star, st
    st[event.group_id] = 0
    if star.setdefault(event.group_id,0):
        star[event.group_id] = random.randint(1,6)
        await ban_game.finish("重新装弹！")
    else:
        star[event.group_id] = random.randint(1,6)
        msg = [
            "这个游戏非常简单，只需要几种道具：一把左轮，一颗子弹，以及愿意跟你一起玩的人。",
            "拿起这把左轮，对着自己的脑袋扣动扳机。如果安然无恙，继续游戏。",
            "对着自己，扣动扳机。如果你是六分之一的“幸运儿”，那么恭喜你，游戏结束。",
            "等等......好像有点不对劲？不过好在“幸运儿”永远没有机会开口说话并诉说游戏的邪恶了",
            "这个游戏非常公平，因为左轮最大的优点就是——不会卡壳",
            "小提示：每次开枪之前可以重新拨动滚轮哦"
            ]
        await ban_game.finish("游戏开始！\n"+ random.choice(msg))

async def Ready(bot: Bot, event: GroupMessageEvent) -> bool:
    star.setdefault(event.group_id,0)
    return star[event.group_id] > 0

roll = on_command("重新装弹",permission = Ready ,aliases = {"拨动滚轮"}, priority = 4, block=True)

@roll.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    global star, st
    st[event.group_id] = 0
    star[event.group_id] = random.randint(1,6)
    msg = [
        "随着金属轮清脆的转动声，子弹重新排列。",
        "——依旧没有人知道子弹的位置。",
        "也许...没有人知道子弹的位置。",
        "拿起这把左轮，对着自己的脑袋扣动扳机。如果安然无恙，继续游戏。",
        "小提示：开枪之前，你还可以继续拨动滚轮哦",
        f"偷偷告诉你，{'如果你开枪的话，下回合将游戏结束。' if star[event.group_id] == 1 else '下一发是空的。'}"
        ]
    random.choice(msg)
    await roll.finish("重新装弹！\n" + random.choice(msg))

shot = on_command("开枪", permission = Ready ,priority = 4, block=True)

@shot.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    global star, st
    st[event.group_id] += 1
    if st[event.group_id] == star[event.group_id]:
        star[event.group_id] = 0
        st[event.group_id] = 0
        try:
            await bot.set_group_ban(group_id = event.group_id, user_id = event.user_id, duration = random.randint(1,10)*60)
        except:
            pass
        await shot.finish("中弹！游戏结束。",at_sender = True)
    else:
        msg = [
            "——传来一声清脆的金属碰撞声。\n没有人知道子弹的位置。可是不论它转到了哪里，总是要响的。",
            "恭喜你，安然无恙......但是下一次还会这么幸运吗？",
            "显然你不是这六分之一的“幸运儿”。但是好消息是，游戏还在继续。",
            "咔的一声，撞针敲击到空仓上。——你还安全地活着。",
            "你的运气不错。祝你好运。",
            "小提示：每次开枪之前可以重新拨动滚轮哦",
            f"偷偷告诉你，如果没有拨动滚轮的话，接下来第{star[event.group_id] - st[event.group_id]}发是子弹的位置。",
            f"偷偷告诉你，如果没有拨动滚轮的话，{'下回合将游戏结束。' if star[event.group_id] - st[event.group_id] == 1 else '下一发是空的。'}",
            f"拨动滚轮时，你看到了，第{star[event.group_id]}发是子弹的位置。",
            f"撞针发出的清脆金属声。自从上次拨动滚轮，这已经是第{st[event.group_id]}发空枪了。"
            ]
        await shot.finish("继续！\n" + random.choice(msg))
