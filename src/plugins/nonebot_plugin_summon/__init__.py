"""导入依赖"""
import nonebot
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message

from .utils import *

try:
    NICKNAME: str = (str(nonebot.get_driver().config.nickname)).replace('{\'', '').replace('\'}', '')
except:
    NICKNAME: str = "脑积水"

__plugin_meta__ = PluginMetadata(
    name="群友召唤术",
    description="让 BOT 帮你召唤群友!",
    usage=("""
设置召唤+艾特(或qq号)+昵称: 设置一个召唤群友
删除召唤+昵称: 删除一个召唤群友
召唤+昵称: 让机器人帮你叫群友
召唤列表: 查看已设置的昵称
戳+昵称+次数(数字): 让机器人戳群友
"""
    ),
    extra={
        "author": "zhulinyv <zhulinyv2005@outlook.com>",
        "version": "2.5.3",
    },
)



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
    # 获取群号
    gid = str(event.group_id)
    # 获取纯文本信息
    message = msg.extract_plain_text().strip()
    # 将字符串转换为列表
    variable_list = message.split(' ')
    variable_list = [word.strip() for word in variable_list if word.strip()]    # 去除空字符串元素
    # 通过艾特方式获取 qid
    qid = await get_at(event)
    # 判断是否成功获取，否则将取列表的第一个元素
    if qid == -1:       # 通过艾特方式获取失败, 那么就通过列表的第一个元素获取
        # 如果列表长度不为2，那么就是格式错误, 直接finish
        await set_summoning.finish("格式错误，请检查后重试\n设置召唤+艾特(或qq号)+昵称", at_sender=True) if len(variable_list) != 2 else ...
        # 在len=2的前提下, 判断列表第一个元素是否为数字，如果是数字，那么就是通过qq号+昵称方式，否则就是格式错误
        qid = int(variable_list[0]) if variable_list[0].isdigit() else await set_summoning.finish("格式错误，通过qq号+昵称方式第一个参数需要为数字", at_sender=True)
        name = variable_list[1]  # 名字
    else:
        # 如果qid不为-1，那么就是通过艾特方式获取，那么就直接取列表的第一个元素
        name = variable_list[0]  # 名字
    await set_summoning.finish("请不要尝试设置名字为空空格", at_sender=True) if name.isspace() else ...  # 如果昵称为空格，那么就finish
    # 更新dict
    if gid in userdata:
        userdata[gid][name] = qid
    else:
        userdata[gid] = {name: qid}
    write_json()  # 写入json
    await set_summoning.finish(f"设置成功~{name} -> {qid}", at_sender=True)


@del_summoning.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    name = msg.extract_plain_text().strip()     # 获取纯文本信息
    gid = str(event.group_id)                # 获取群号
    try:
        del userdata[gid][name] # 删除
    except:
        await del_summoning.finish("删除失败，没有这个人哦~", at_sender=True)   # 如果删除失败，那么就是没有这个人
    write_json()    # 写入json
    await del_summoning.finish("删除成功~")   # 删除成功


@model_switch.handle()
async def _(switch_msg: Message = CommandArg()):
    switch_msg = switch_msg.extract_plain_text().strip()    # 获取纯文本信息
    if switch_msg == "普通":
        switch = 1
    elif switch_msg == "增强":
        switch = 2
    elif switch_msg == "强力":
        switch = 3
    else:
        await model_switch.finish("没有这个模式哦~")
    userdata["send_model"] = switch # 更新dict
    write_json()    # 写入json
    msg = f"切换成功~~当前召唤术为: {switch}模式".replace(
        '1', "普通").replace('2', "增强").replace('3', "强力")
    await model_switch.finish(msg, at_sender=True)


@list_summoning.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)   # 获取群号
    if gid not in userdata or userdata[gid] == {}:    # 判断是否有这个群, 以及这个群的dict是否为空
        await list_summoning.finish(f"在本群{NICKNAME}的记忆里还没有人捏......", at_sender=True)
    else:
        dataDict = userdata[gid]    # 获取dict
    msg = ""
    for i in dataDict:  # 遍历dict
        msg = msg + f"{i} -> {dataDict[i]}\n"
    await list_summoning.finish(msg)


@summon.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    gid = str(event.group_id)   # 获取群号
    name = msg.extract_plain_text().strip()    # 获取纯文本信息
    switch = userdata["send_model"] # 获取模式
    try:
        qid = userdata[gid][name]   # 获取qq号
        if switch == 1:    # 判断模式
            await summon.finish(Message(f"[CQ:poke,qq={qid}]"))
        elif switch == 2:
            await summon.finish(Message(f"[CQ:at,qq={qid}]"))
        elif switch == 3:
            await summon.send(Message(f"[CQ:poke,qq={qid}]"))
            await summon.send(Message(f"[CQ:at,qq={qid}]"))
    except KeyError:    # 如果没有这个人，那么就是KeyError
        await summon.finish(f"{NICKNAME}的记忆里没有这号人捏......")


@poke.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    gid = str(event.group_id)   # 获取群号
    message = msg.extract_plain_text().strip()  # 获取纯文本信息
    variable_list = message.split(' ')  # 以空格分割
    variable_list = [word.strip() for word in variable_list if word.strip()]    # 去除空格
    await poke.finish("格式错误，请检查后重试\n戳+昵称+次数(数字)", at_sender=True) if len(variable_list) < 2 else ...  # 判断列表长度
    name = variable_list[0] # 名字
    nums = int(variable_list[1]) if variable_list[1].isdigit() else await poke.finish("格式错误，请检查后重试\n戳+昵称+次数(数字)", at_sender=True) # 次数
    await poke.finish(f"要人家戳这么多次, 你想让{NICKNAME}风控嘛......", at_sender=True) if nums > 10 else ... # 判断次数
    try:
        qid = userdata[gid][name]   # 获取qq号
    except KeyError:
        await poke.finish(f"{NICKNAME}的记忆里没有这号人捏......", at_sender=True)    # 如果没有这个人，那么就是KeyError

    for i in range(nums):   # 循环戳
        try:
            await poke.send(Message(f"[CQ:poke,qq={qid}]"))
        except Exception as e:
            await poke.send(f"戳一戳失败, 错误信息: {e}")
