"""导入依赖"""
import nonebot
from loguru import logger
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

try:
    import ujson as json
except ModuleNotFoundError:
    import json

"""获取变量"""
data_path = "./data/summon/"
switch = 1

try:
    NICKNAME: str = nonebot.get_driver().config.nickname
except:
    NICKNAME: str = "脑积水"



"""获取指令"""
set_summoning = on_command("设置召唤", aliases={"设置召唤术"}, priority=60, block=True)
del_summoning = on_command("删除召唤", aliases={"删除召唤术"}, rule=to_me(), priority=60, block=True)
model_switch = on_command("切换召唤术", aliases={"切换召唤模式"}, rule=to_me(), permission=SUPERUSER, priority=60, block=True)
list_summoning = on_command("召唤列表", aliases={"查看召唤", "查看召唤术"}, priority=60, block=True)
summon = on_command("召唤", priority=60, block=True)
poke = on_command("戳", priority=60, block=True)



"""执行指令"""
@set_summoning.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    # 获取纯文本信息
    message = msg.extract_plain_text().strip()
    # 将字符串转换为列表
    variable_list = message.split(' ')
    # 通过艾特方式获取 qid
    qid = await get_at(event)
    # 判断是否成功获取，否则将取列表的第一个元素
    if qid == None:
        qid = int(variable_list[0])
    # 获取设置的昵称
    try:
        # 取第二个元素作为昵称
        name = variable_list[1]
    except Exception:
        # 艾特方式不存在第二个元素，则取第一个元素
        name = variable_list[0]
    # 获取群号
    gid = str(event.group_id)
    # 编辑文件路径
    global data_path_gid
    data_path_gid = data_path + gid + "/"
    # 文件操作
    data = read_json()
    data = write_json(name, qid, data)
    logger.info(f"已设置 {name}: {qid}")
    await set_summoning.finish("设置成功~")

@del_summoning.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    name = msg.extract_plain_text().strip()
    gid = str(event.group_id)
    global data_path_gid
    data_path_gid = data_path + gid + "/"
    remove_json(name)
    await del_summoning.finish("删除成功~")

@model_switch.handle()
async def _(switch_msg: Message = CommandArg()):
    switch_msg = switch_msg.extract_plain_text().strip()
    global switch
    if switch_msg == "普通":
        switch = 1
    elif switch_msg == "增强":
        switch = 2
    elif switch_msg == "强力":
        switch = 3
    else:
        await model_switch.finish("没有这个模式哦~")
    msg = f"切换成功~~当前召唤术为: {switch}模式".replace('1', "普通").replace('2', "增强").replace('3', "强力")
    await model_switch.finish(msg, at_sender=True)

@list_summoning.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    global data_path_gid
    data_path_gid = data_path + gid + "/"
    data = read_json()
    if data == {}:
        await list_summoning.finish(f"{NICKNAME}的记忆里还没有人捏......".replace('{\'', '').replace('\'}', ''), at_sende=True)
    msg = f"{data}".replace(' ', '').replace(':', '：').replace('{', '').replace('}', '').replace(',', '\n').replace('\'', '')
    await list_summoning.finish(msg)

@summon.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    gid = str(event.group_id)
    global data_path_gid
    data_path_gid = data_path + gid + "/"
    name = msg.extract_plain_text().strip()
    data = read_json()
    try:
        qid = data[name]
        if switch == 1:
            await summon.finish(Message(f"[CQ:poke,qq={qid}]"))
        elif switch == 2:
            await summon.finish(Message(f"[CQ:at,qq={qid}]"))
        elif switch == 3:
            await summon.send(Message(f"[CQ:poke,qq={qid}]"))
            await summon.send(Message(f"[CQ:at,qq={qid}]"))
    except KeyError:
        await summon.finish(f"{NICKNAME}的记忆里没有这号人捏......".replace('{\'', '').replace('\'}', ''))

@poke.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    gid = str(event.group_id)
    global data_path_gid
    data_path_gid = data_path + gid + "/"
    message = msg.extract_plain_text().strip()
    variable_list = message.split(' ')
    name = variable_list[0]
    times = int(variable_list[1])
    data = read_json()
    try:
        if times <= 10:
            qid = data[name]
            for t in range(times):
                await poke.send(Message(f"[CQ:poke,qq={qid}]"))
        else:
            await poke.finish(f"你想让{NICKNAME}风控嘛......".replace('{\'', '').replace('\'}', ''), at_sende=True)
    except KeyError:
        await poke.finish(f"{NICKNAME}的记忆里没有这号人捏......".replace('{\'', '').replace('\'}', ''), at_sender=True)



"""一些工具"""
# 获取被艾特用户 ID
async def get_at(event: GroupMessageEvent) -> int:
    msg=event.get_message()
    for msg_seg in msg:
        if msg_seg.type == "at":
            return int(msg_seg.data["qq"])

# read_json
def read_json() -> dict:
    try:
        with open(data_path_gid + "userinfo.json", "r") as f_in:
            data = json.load(f_in)
            f_in.close()
            return data
    except FileNotFoundError:
        try:
            import os
            os.makedirs(data_path_gid)
        except FileExistsError:
            pass
        with open(data_path_gid + "userinfo.json", mode="w") as f_out:
            json.dump({}, f_out)
        return {}

# write_json
def write_json(name: str, qid: str, data: dict):
    data[name] = qid
    with open(data_path_gid + "userinfo.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()

# remove_json
def remove_json(name: str):
    with open(data_path_gid + "userinfo.json", "r") as f_in:
        data = json.load(f_in)
        f_in.close()
    data.pop(name)
    with open(data_path_gid + "userinfo.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()
