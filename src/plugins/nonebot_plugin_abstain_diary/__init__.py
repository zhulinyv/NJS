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
戒色命令如下(【】中的才是命令哦，记得加命令前缀)：
【戒色目标】【设置戒色目标】，后面追加戒色目标天数。例如：/戒色目标 30

【戒色】【戒色打卡】，每日打卡，请勿中断喵。例如：/戒色

【群戒色】【戒色情况】【群友戒色情况】，查看本群所有戒色情况。例如：/群戒色

【放弃戒色】【取消戒色】【不戒色了】，删除戒色目标。例如：/放弃戒色

【群戒色】【戒色情况】【群友戒色情况】，查看本群所有戒色情况

财能使人贪，色能使人嗜，名能使人矜，潜能使人倚，四患既都去，岂在浮尘里。
""".strip()

__plugin_meta__ = PluginMetadata(
    name = '戒色打卡日记',
    description = '适用于nonebot2 v11的戒色打卡日记插件',
    usage = help_text
)

# 读取数据至此变量
data_json = {}
data_dir = "data/abstain_diary"
data_path = "data/abstain_diary/data.json"

set_abstain = on_command("设置戒色目标", aliases={"戒色目标"})
abstain = on_command("戒色打卡", aliases={"戒色"})
abstain_state = on_command("群友戒色情况", aliases={"戒色情况", "群戒色"})
abstain_help = on_command("戒色帮助", aliases={"戒色说明", "戒色命令"})
abandon_abstain = on_command("放弃戒色", aliases={"取消戒色", "不戒色了"})

@set_abstain.handle()
async def _(bot: Bot, event: GroupMessageEvent, tgt_days: Message = CommandArg()):
    global data_json

    user_id = str(event.get_user_id())
    group_id = str(event.group_id)
    nickname = event.sender.nickname
    
    tgt_days = str(tgt_days)
    try:
        tgt_days_int = int(tgt_days)
    except:
        await set_abstain.finish(MessageSegment.text("请传入正整数喵~\n例如：/戒色目标 30"), at_sender=True)

    # 进行天数判断
    if tgt_days_int < 1:
        await set_abstain.finish(MessageSegment.text("请传入正整数喵~\n例如：/戒色目标 30"), at_sender=True)
    elif tgt_days_int == 1:
        await set_abstain.finish(MessageSegment.text("就一天？？？开什么玩笑，kora！"), at_sender=True)

    now_time = time.time()

    # 是否存在 群组数据
    if group_id in data_json:
        # 是否存在 用户数据
        if user_id in data_json[group_id]:
            data_json[group_id][user_id]["tgt_days"] = tgt_days_int
        else:
            temp_json = {
                user_id : {
                    "tgt_days": tgt_days_int,
                    "now_days": 1,
                    "nickname": nickname,
                    "last_time" : now_time
                }
            }
            data_json[group_id].update(temp_json)
    else:
        temp_json = {
            group_id: {
                user_id : {
                    "tgt_days": tgt_days_int,
                    "now_days": 1,
                    "nickname": nickname,
                    "last_time" : now_time
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
        msg += "戒色目标天数：" + tgt_days + "，设置成功！\n今天是打卡第一天，加油！你我都有美好的未来！"
    except IOError as e:
        msg += "设置失败 " + str(e)
    await set_abstain.finish(MessageSegment.text(msg), at_sender=True)


@abstain.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    global data_json

    user_id = str(event.get_user_id())
    group_id = str(event.group_id)

    # 是否存在 群组数据
    if group_id in data_json:
        # 是否存在 用户数据
        if user_id in data_json[group_id]:
            now_time = time.time()
            last_time = data_json[group_id][user_id]["last_time"]
            temp_now = time.strftime("%Y-%m-%d", time.localtime(now_time))
            temp_last = time.strftime("%Y-%m-%d", time.localtime(data_json[group_id][user_id]["last_time"]))
            # 判断是否一天内重复打卡
            if temp_now == temp_last:
                msg = "\n您今天已经打过卡啦，不用再打啦~\n记得明天再来哦~"
                await abstain.finish(MessageSegment.text(msg), at_sender=True)

            data_json[group_id][user_id]["last_time"] = now_time

            # 判断是否打卡中断
            if (now_time - last_time) > 24 * 3600:
                # 重置为1
                data_json[group_id][user_id]["now_days"] = 1
                try:
                    # 数据写回
                    with open(data_path, mode='w', encoding='utf-8') as f:
                        json.dump(data_json, f)
                        f.close()
                    msg = "\n戒色打卡中断了捏，打卡重置。\n当前打卡天数：1天！懂的都懂，仍需努力呀！"
                    await abstain.finish(MessageSegment.text(msg), at_sender=True)
                except IOError as e:
                    msg = "\n数据写入失败，请检查源码或数据问题。" + str(e)
                    await abstain.finish(MessageSegment.text(msg), at_sender=True)
            
            data_json[group_id][user_id]["now_days"] += 1
            now_days = data_json[group_id][user_id]["now_days"]
            tgt_days = data_json[group_id][user_id]["tgt_days"]
            # 是否打卡达标
            if now_days >= tgt_days:
                data_json[group_id].pop(user_id)
                try:
                    # 数据写回
                    with open(data_path, mode='w', encoding='utf-8') as f:
                        json.dump(data_json, f)
                        f.close()
                    msg = "\n恭喜完成戒色打卡" + str(now_days) + "天！这不得冲一把？？？"
                    await abstain.finish(MessageSegment.text(msg), at_sender=True)
                except IOError as e:
                    msg = "\n数据写入失败，请检查源码或数据问题。 " + str(e)
                    await abstain.finish(MessageSegment.text(msg), at_sender=True)
            else:
                try:
                    # 数据写回
                    with open(data_path, mode='w', encoding='utf-8') as f:
                        json.dump(data_json, f)
                        f.close()
                    msg = "\n戒色打卡成功！您已打卡" + str(now_days) + "天！"
                    await abstain.finish(MessageSegment.text(msg), at_sender=True)
                except IOError as e:
                    msg = "\n数据写入失败，请检查源码或数据问题。 " + str(e)
                    await abstain.finish(MessageSegment.text(msg), at_sender=True)
        else:
            msg = "\n您还没有设置【戒色目标】捏，请先设置目标再打卡哦~"
            await abstain.finish(MessageSegment.text(msg), at_sender=True)
    else:
        msg = "\n您还没有设置【戒色目标】捏，请先设置目标再打卡哦~"
        await abstain.finish(MessageSegment.text(msg), at_sender=True)


@abstain_state.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    global data_json

    group_id = str(event.group_id)

    # 是否存在 群组数据
    if group_id in data_json:
        msg = "🥵🥵🥵群戒色信息\n"
        msg += "打卡数  👈  群昵称  👉  目标数\n"
        msg += "——————————————\n"
        for key, value in data_json[group_id].items():
            msg += str(value["now_days"]) + "  👈  " + str(value["nickname"]) + "  👉  " + str(value["tgt_days"]) + "\n"
        await abstain_state.finish(MessageSegment.text(msg))
    else:
        msg = "\n本群无人设置【戒色目标】捏，请先设置目标再查询哦~"
        await abstain_state.finish(MessageSegment.text(msg), at_sender=True)


@abandon_abstain.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    global data_json

    user_id = str(event.get_user_id())
    group_id = str(event.group_id)

    # 是否存在 群组数据
    if group_id in data_json:
        # 是否存在 用户数据
        if user_id in data_json[group_id]:
            data_json[group_id].pop(user_id)
            try:
                # 数据写回
                with open(data_path, mode='w', encoding='utf-8') as f:
                    json.dump(data_json, f)
                    f.close()
                msg = "\n戒色打卡已取消，您可以开冲啦！！！"
                await abstain_state.finish(MessageSegment.text(msg), at_sender=True)
            except IOError as e:
                msg = "\n数据写入失败，请检查源码或数据问题。 " + str(e)
                await abstain.finish(MessageSegment.text(msg), at_sender=True)
        else:
            msg = "\n您还没有设置【戒色目标】捏，不用取消啦~"
            await abstain_state.finish(MessageSegment.text(msg), at_sender=True)
    else:
        msg = "\n您还没有设置【戒色目标】捏，不用取消啦~"
        await abstain_state.finish(MessageSegment.text(msg), at_sender=True)



@abstain_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = "\n戒色命令如下(【】中的才是命令哦，记得加命令前缀)：\n"
    msg += "【戒色目标】【设置戒色目标】，后面追加戒色目标天数。例如：/戒色目标 30\n\n"
    msg += "【戒色】【戒色打卡】，每日打卡，请勿中断喵。例如：/戒色\n\n"
    msg += "【群戒色】【戒色情况】【群友戒色情况】，查看本群所有戒色情况。例如：/群戒色\n\n"
    msg += "【放弃戒色】【取消戒色】【不戒色了】，删除戒色目标。例如：/放弃戒色\n\n"
    msg += "财能使人贪，色能使人嗜，名能使人矜，潜能使人倚，四患既都去，岂在浮尘里。"
    await abstain_help.finish(MessageSegment.text(msg), at_sender=True)



# 初始化和加载数据
def init_data():
    global data_json

    # 判断目录是否存在，如果不存在建立目录
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
        logger.info("戒色数据加载完毕。数据文件大小：" + str(os.path.getsize(data_path)) + "B")


# 初始化和加载数据
init_data()
