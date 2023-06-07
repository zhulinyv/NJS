import os
import json
from nonebot import on_keyword, on_command, logger
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.typing import T_State
from nonebot.params import CommandArg
import time
from nonebot.plugin import PluginMetadata


help_text = f"""
戒色命令如下(【】中的才是命令哦，记得加命令前缀；其中xx可以随意替换)：
【戒xx 目标】【戒xx 设置】，后面追加戒x目标天数。例如：/戒色 目标 30

【戒xx】，每日打卡，请勿中断喵。例如：/戒色

【群戒】【戒情况】【群友戒情况】，查看本群所有戒情况。例如：/群戒

【戒xx 放弃】【戒xx 取消】，删除戒xx目标。例如：/戒色 放弃

【戒帮助】【戒说明】【戒命令】，查看使用说明。例如：/戒帮助

财能使人贪，色能使人嗜，名能使人矜，潜能使人倚，四患既都去，岂在浮尘里。
""".strip()

__plugin_meta__ = PluginMetadata(
    name = '戒x打卡日记',
    description = '适用于nonebot2 v11的戒x打卡日记插件',
    usage = help_text
)

# 读取数据至此变量
data_json = {}
root_dir = "data"
data_dir = root_dir + "/abstain_diary"
data_path = data_dir + "/data.json"

custom_abstain = on_command("戒")
custom_abstain_state = on_command("群友戒情况", aliases={"戒情况", "群戒"})
custom_abstain_help = on_command("戒帮助", aliases={"戒说明", "戒命令"})


@custom_abstain_state.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    global data_json

    group_id = str(event.group_id)

    # 是否存在 群组数据
    if group_id in data_json:
        msg = "🥵🥵🥵群戒信息\n"
        msg += "打卡数 👈 群昵称 👉 目标数\n"
        msg += "——————————————\n"
        for key, value in data_json[group_id].items():
            msg += "戒" + str(key) + "\n"
            for key, value in data_json[group_id][key].items():
                msg += str(value["now_days"]) + " 👈 " + \
                    str(value["nickname"]) + " 👉 " + \
                    str(value["tgt_days"]) + "\n"
            msg += "——————————————\n"
        await custom_abstain_state.finish(MessageSegment.text(msg))
    else:
        msg = "\n本群无人设置【戒xx 目标】捏，请先设置目标再查询哦~"
        await custom_abstain_state.finish(MessageSegment.text(msg), at_sender=True)


@custom_abstain_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = "\n戒命令如下(【】中的才是命令哦，记得加命令前缀)：\n"
    msg += "【戒xx 目标】【戒xx 设置】，后面追加戒xx目标天数。例如：/戒氪金 目标 30\n\n"
    msg += "【戒xx】，每日打卡，请勿中断喵。例如：/戒氪金\n\n"
    msg += "【群戒】【戒情况】【群友戒情况】，查看本群所有戒情况。例如：/群戒\n\n"
    msg += "【戒xx 放弃】【戒xx 取消】，删除戒xx目标。例如：/戒氪金 放弃\n\n"
    msg += "财能使人贪，色能使人嗜，名能使人矜，潜能使人倚，四患既都去，岂在浮尘里。"
    await custom_abstain_help.finish(MessageSegment.text(msg), at_sender=True)


# 初始化和加载数据
def init_data():
    global data_json

    # 判断一级目录是否存在，如果不存在建立目录
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
    # 判断二级目录是否存在，如果不存在建立目录
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    with open(data_path, mode='a+', encoding='utf-8') as f:
        f.seek(0, 0)
        # logger.info(f.readlines())
        # logger.info(os.path.getsize(data_path))
        if os.path.getsize(data_path) == 0:
            data_json = {}
        else:
            data_json = json.load(f)
        f.close()
        logger.info("abstain_diary数据加载完毕。数据文件大小：" + str(os.path.getsize(data_path)) + "B")


# 初始化和加载数据
init_data()


@custom_abstain.handle()
async def _(bot: Bot, event: GroupMessageEvent, content: Message = CommandArg()):
    global data_json

    ret_json = {}

    user_id = str(event.get_user_id())
    group_id = str(event.group_id)
    nickname = event.sender.nickname

    # 获取命令传参转为字符串
    content = str(content)
    # 字符串解析 传参定义，以空格为分隔
    # 第一个传参为需要戒的事物，
    # 第二个则为功能点的选择（目标/设置，取消/放弃，（不填默认打卡））
    # 如果第二个选择的是目标，则需要传入第三个参数 戒的天数
    arg_arr = content.split()
    arg_arr_len = len(arg_arr)

    if arg_arr_len == 0:
        msg = "\n此处是戒功能的使用说明"
        await custom_abstain.finish(MessageSegment.text(msg), at_sender=True)
    elif arg_arr_len == 1:
        ret_json = await custom_abstain_func(user_id, group_id, arg_arr[0])
        await custom_abstain.finish(MessageSegment.text(ret_json["msg"]), at_sender=True)
    else:
        # 传参数>=2
        if arg_arr[1] == "取消" or arg_arr[1] == "放弃":
            ret_json = await custom_abandon(user_id, group_id, arg_arr[0])
            await custom_abstain.finish(MessageSegment.text(ret_json["msg"]), at_sender=True)
        elif arg_arr[1] == "目标" or arg_arr[1] == "设置":
            if arg_arr_len >= 3:
                try:
                    tgt_days_int = int(arg_arr[2])
                except:
                    msg = "请传入正整数喵~\n例如：/戒" + arg_arr[0] + " 目标 30"
                    await custom_abstain.finish(MessageSegment.text(msg), at_sender=True)

                # 进行天数判断
                if tgt_days_int < 1:
                    msg = "请传入正整数喵~\n例如：/戒" + arg_arr[0] + " 目标 30"
                    await custom_abstain.finish(MessageSegment.text(msg), at_sender=True)
                elif tgt_days_int == 1:
                    await custom_abstain.finish(MessageSegment.text("就一天？？？开什么玩笑，kora！"), at_sender=True)
                ret_json = await custom_set(user_id, group_id, nickname, arg_arr[0], tgt_days_int)
                await custom_abstain.finish(MessageSegment.text(ret_json["msg"]), at_sender=True)
            else:
                msg = "\n请传入目标天数。此处是戒功能的使用说明"
                await custom_abstain.finish(MessageSegment.text(msg), at_sender=True)
        else:
            msg = "\n功能点选择错误，第二个参数请传入（目标/设置，取消/放弃）"
            await custom_abstain.finish(MessageSegment.text(msg), at_sender=True)


# 放弃戒xx 分别传入 用户qq 群号 戒的内容
# 返回：json
# code: 0删除数据成功 1无数据 2写入失败
# {"code": 0, "msg": "返回的文字描述或报错"}
async def custom_abandon(user_id, group_id, content):
    global data_json
    return_json = {"code": 0, "msg": "返回的文字描述或报错"}

    # 是否存在 群组数据
    if group_id in data_json:
        # 是否存在 戒的内容
        if content in data_json[group_id]:
            # 是否存在 用户数据
            if user_id in data_json[group_id][content]:
                data_json[group_id][content].pop(user_id)
                try:
                    # 数据写回
                    with open(data_path, mode='w', encoding='utf-8') as f:
                        json.dump(data_json, f)
                        f.close()
                    msg = "\n戒" + content + "打卡已取消，您可以开冲啦！！！"
                    return_json["msg"] = msg
                    return return_json
                except IOError as e:
                    msg = "\n数据写入失败，请检查源码或数据问题。 " + str(e)
                    return_json["code"] = 2
                    return_json["msg"] = msg
                    return return_json

    msg = "\n您还没有设置【戒" + content + " 目标】捏，不用取消啦~"
    return_json["code"] = 1
    return_json["msg"] = msg
    return return_json


# 设置戒xx 分别传入 用户qq 群号 昵称 戒的内容 目标天数（需要是正整数且>1）
# 返回：json
# code: 0写入数据成功 2写入失败
# {"code": 0, "msg": "返回的文字描述或报错"}
async def custom_set(user_id, group_id, nickname, content, tgt_days):
    return_json = {"code": 0, "msg": "返回的文字描述或报错"}
    now_time = time.time()
    
    # 是否存在 群组数据
    if group_id in data_json:
        # 是否存在 戒的内容
        if content in data_json[group_id]:
            # 是否存在 用户数据
            if user_id in data_json[group_id][content]:
                data_json[group_id][content][user_id]["tgt_days"] = tgt_days
            else:
                temp_json = {
                    user_id: {
                        "tgt_days": tgt_days,
                        "now_days": 1,
                        "nickname": nickname,
                        "last_time" : now_time
                    }
                }
                data_json[group_id][content].update(temp_json)
        # 不存在 戒的内容
        else:
            temp_json = {
                content: {
                    user_id: {
                        "tgt_days": tgt_days,
                        "now_days": 1,
                        "nickname": nickname,
                        "last_time" : now_time
                    }
                }
            }
            data_json[group_id].update(temp_json)
    # 不存在 群组数据
    else:
        temp_json = {
            group_id: {
                content: {
                    user_id: {
                        "tgt_days": tgt_days,
                        "now_days": 1,
                        "nickname": nickname,
                        "last_time" : now_time
                    }
                }
            }
        }
        data_json.update(temp_json)

    msg = "\n"
    try:
        # 数据写回
        with open(data_path, mode='w', encoding='utf-8') as f:
            json.dump(data_json, f)
            f.close()
        msg += "戒" + content + "目标天数：" + str(tgt_days) + "，设置成功！\n今天是打卡第一天，加油！你我都有美好的未来！"
        return_json["msg"] = msg
    except IOError as e:
        msg += "设置失败 " + str(e)
        return_json["code"] = 2
        return_json["msg"] = msg
    return return_json


# 自定义戒xx打卡 分别传入 用户qq 群号 戒的内容
# 返回：json
# code: 0打卡成功 1无数据 2写入失败 3已打卡 4打卡中断 5打卡完成
# {"code": 0, "msg": "返回的文字描述或报错"}
async def custom_abstain_func(user_id, group_id, content):
    global data_json
    return_json = {"code": 0, "msg": "返回的文字描述或报错"}

    # 是否存在 群组数据
    if group_id in data_json:
        # 是否存在 戒的内容
        if content in data_json[group_id]:
            # 是否存在 用户数据
            if user_id in data_json[group_id][content]:
                now_time = time.time()
                last_time = data_json[group_id][content][user_id]["last_time"]
                temp_now = time.strftime("%Y-%m-%d", time.localtime(now_time))
                temp_last = time.strftime("%Y-%m-%d", time.localtime(data_json[group_id][content][user_id]["last_time"]))
                # 判断是否一天内重复打卡
                if temp_now == temp_last:
                    msg = "\n您今天已经打过卡啦，不用再打啦~\n记得明天再来哦~"
                    return_json["code"] = 3
                    return_json["msg"] = msg
                    return return_json

                data_json[group_id][content][user_id]["last_time"] = now_time

                # 判断是否打卡中断 24h间隔（则更改为注释行），默认规则为间隔一天
                # if (now_time - last_time) > 24 * 3600:
                if await days_between_dates(temp_last, temp_now) > 1:
                    # 重置为1
                    data_json[group_id][content][user_id]["now_days"] = 1
                    try:
                        # 数据写回
                        with open(data_path, mode='w', encoding='utf-8') as f:
                            json.dump(data_json, f)
                            f.close()
                        msg = "\n戒" + content + " 打卡中断了捏，打卡重置。\n当前打卡天数：1天！懂的都懂，仍需努力呀！"
                        return_json["code"] = 4
                        return_json["msg"] = msg
                        return return_json
                    except IOError as e:
                        msg = "\n数据写入失败，请检查源码或数据问题。" + str(e)
                        return_json["code"] = 2
                        return_json["msg"] = msg
                        return return_json
                
                data_json[group_id][content][user_id]["now_days"] += 1
                now_days = data_json[group_id][content][user_id]["now_days"]
                tgt_days = data_json[group_id][content][user_id]["tgt_days"]
                # 是否打卡达标
                if now_days >= tgt_days:
                    data_json[group_id][content].pop(user_id)
                    try:
                        # 数据写回
                        with open(data_path, mode='w', encoding='utf-8') as f:
                            json.dump(data_json, f)
                            f.close()
                        msg = "\n恭喜完成戒" + content + " 打卡" + str(now_days) + "天！这不得冲一把？？？"
                        return_json["code"] = 5
                        return_json["msg"] = msg
                    except IOError as e:
                        msg = "\n数据写入失败，请检查源码或数据问题。 " + str(e)
                        return_json["code"] = 2
                        return_json["msg"] = msg
                # 还未完成打卡目标
                else:
                    try:
                        # 数据写回
                        with open(data_path, mode='w', encoding='utf-8') as f:
                            json.dump(data_json, f)
                            f.close()
                        msg = "\n戒" + content + " 打卡成功！您已打卡" + str(now_days) + "天！"
                        return_json["code"] = 0
                        return_json["msg"] = msg
                    except IOError as e:
                        msg = "\n数据写入失败，请检查源码或数据问题。 " + str(e)
                        return_json["code"] = 2
                        return_json["msg"] = msg
            # 不存在 用户数据
            else:
                msg = "\n您还没有设置【戒" + content + " 目标】捏，请先设置目标再打卡哦~"
                return_json["code"] = 1
                return_json["msg"] = msg
        # 不存在 戒的内容
        else:
            msg = "\n您还没有设置【戒" + content + " 目标】捏，请先设置目标再打卡哦~"
            return_json["code"] = 1
            return_json["msg"] = msg
    # 不存在 群组数据
    else:
        msg = "\n您还没有设置【戒" + content + " 目标】捏，请先设置目标再打卡哦~"
        return_json["code"] = 1
        return_json["msg"] = msg

    return return_json


# 日期间隔天数
async def days_between_dates(day1, day2):
    time_array1 = time.strptime(day1, "%Y-%m-%d")
    timestamp_day1 = int(time.mktime(time_array1))
    time_array2 = time.strptime(day2, "%Y-%m-%d")
    timestamp_day2 = int(time.mktime(time_array2))
    result = (timestamp_day2 - timestamp_day1) // 60 // 60 // 24
    return result