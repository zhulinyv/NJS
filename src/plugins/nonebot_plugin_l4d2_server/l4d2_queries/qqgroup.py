import asyncio
import random
from typing import Any, Dict, List, Tuple, Union

from nonebot.log import logger

from ..l4d2_data.serverip import L4D2Server
from ..l4d2_image import server_ip_pic
from ..l4d2_utils.message import KAILAO, PRISON, QUEREN
from ..l4d2_utils.utils import split_maohao
from .localIP import ALL_HOST
from .utils import (
    msg_ip_to_list,
    player_queries,
    player_queries_anne_dict,
    queries,
    queries_dict,
)

try:
    import ujson as json
except:
    import json
si = L4D2Server()
errors = (
    ConnectionRefusedError,
    ConnectionResetError,
    asyncio.exceptions.TimeoutError,
    OSError,
)
# errors = (TypeError,KeyError,ValueError,ConnectionResetError,TimeoutError)


async def get_qqgroup_ip_msg(qqgroup):
    """首先，获取qq群订阅数据，再依次queries返回ip原标"""
    ip_list = await si.query_server_ip(qqgroup)
    return ip_list


async def bind_group_ip(group: int, host: str, port: int):
    ip_list = await si.query_server_ip(group)
    if (host, port) in ip_list:
        return "本群已添加过该ip辣"
    await si.bind_server_ip(group, host, port)
    return "绑定成功喵，新增ip" + host


async def del_group_ip(group: int, number: int):
    number = int(number)
    logger.info(number)
    try:
        groups, host, port = await si.query_number(number)
    except TypeError:
        return "没有这个序号哦"
    if groups != group:
        return "本群可没有订阅过这个ip"
    await si.del_server_ip(number)
    return "取消成功喵，已删除序号" + str(number)


async def qq_ip_queries(msg: List[tuple]):
    """输入一个ip的二元元组组成的列表，返回一个输出消息的列表
    未来作图这里重置"""
    messsage = ""
    for i in msg:
        number, qqgroup, host, port = i
        msg2 = await player_queries(host, port)
        msg1 = await queries(host, port)
        messsage += "序号、" + str(number) + "\n" + msg1 + msg2 + "--------------------\n"
    return messsage


async def qq_ip_querie(msg: List[Tuple[str, str, int]], igr: bool = True):
    msg_list: List[Dict[str, Any]] = []
    tasks = []  # 用来保存异步任务
    if msg != []:
        for i in msg:
            try:
                number: str
                host: str
                port: int
                qqgroup: str = ""  # 初始化为""
                if len(i) == 3:
                    number, host, port = i
                else:
                    number, qqgroup, host, port = i  # type: ignore
                # 将异步任务添加到任务列表中
                tasks.append(
                    asyncio.create_task(
                        process_message(
                            number,
                            host,
                            port,
                            msg_list,
                            igr,
                            qqgroup,
                        )
                    )
                )
            except ValueError:
                continue  # 处理异常情况
        # 等待所有异步任务完成
        await asyncio.gather(*tasks)
        # 对msg_list按照number顺序排序
        # msg_list.sort(key=lambda x: x["number"])
        send_list = sorted(msg_list, key=lambda x: int(x["number"]))
        result = {"msg_list": send_list}

    else:
        result: Dict[str, List[Dict[str, Any]]] = {}
    return result


async def qq_ip_queries_pic(msg: list, igr=False):
    result = await qq_ip_querie(msg, igr)
    if "msg_list" in result:
        pic = await server_ip_pic(result["msg_list"])
    else:
        pic = None
    return pic


async def process_message(
    number: str,
    host: str,
    port: int,
    msg_list: List[Dict[str, Any]],
    igr: bool,
    qqgroup: str = "",
):
    try:
        msg2 = await player_queries_anne_dict(host, port)
        msg1 = await queries_dict(host, port)
        msg3 = await server_rule_dict(host, port)
        msg1.update(
            {
                "Players": msg2,
                "number": number,
            }
        )
        msg1.update(msg3)
        if qqgroup:
            msg1.update({"tag": qqgroup})
        msg_list.append(msg1)
    except errors:
        if igr:
            pass
        else:
            # 空白字典
            null_dict = {
                key: "null"
                for key in [
                    "name",
                    "map_",
                    "players",
                    "max_players",
                    "rank_players",
                    "ping",
                ]
            }
            null_dict.update({"number": number, "ip": f"{host}:{port}", "Players": []})  # type: ignore
            msg_list.append(null_dict)


async def get_tan_jian(msg: List[tuple], mode: int):
    """获取anne列表抽一个"""
    msg_list = []
    random.shuffle(msg)
    for i in msg:
        number, host, port = i
        try:
            if mode == 1:
                # 探监
                msg2 = await player_queries_anne_dict(host, port)
                point = 0
                for i in msg2:
                    point += int(i["Score"])
                logger.info(point)
                msg1 = await queries_dict(host, port)
                sp: str = msg1["name"]
                if "特" not in sp:
                    continue
                sps = int(sp.split("特")[0].split("[")[-1])
                points = point / 4
                if points / sps < 10:
                    continue
                if "HT" in msg1["name"]:
                    continue
                msg1.update({"Players": msg2})
                msg1.update({"ranks": point})
                ips = f"{host}:{str(port)}"
                msg1.update({"ips": ips})
                # msg1是一行数据完整的字典
                msg_list.append(msg1)
            if mode == 2:
                # 坐牢
                # try:
                msg1 = await queries_dict(host, port)
                if "普通药役" in msg1["name"]:
                    if "缺人" in msg1["name"]:
                        msg2 = await player_queries_anne_dict(host, port)
                        msg1.update({"Players": msg2})
                        ips = f"{host}:{str(port)}"
                        msg1.update({"ips": ips})
                        # msg1是一行数据完整的字典
                    else:
                        continue
                else:
                    continue
                msg_list.append(msg1)
            if mode == 3:
                # 开牢
                msg1 = await queries_dict(host, port)
                if "[" not in msg1["name"]:
                    msg2 = await player_queries_anne_dict(host, port)
                    msg1.update({"Players": msg2})
                    ips = f"{host}:{str(port)}"
                    msg1.update({"ips": ips})
                    # msg1是一行数据完整的字典
                    msg_list.append(msg1)
        except errors:
            continue
        if msg_list != []:
            break
    # 随机选一个牢房
    logger.info(msg_list)
    if len(msg_list) == 0:
        return "暂时没有这种牢房捏"
    logger.info(len(msg_list))
    mse = msg_list[0]
    message: str = ""
    if mode == 1:
        ranks = mse["ranks"]
        if ranks <= 300:
            message = random.choice(PRISON[1])
        if 300 < ranks <= 450:
            message = random.choice(PRISON[2])
        if ranks > 450:
            message = random.choice(PRISON[3])
    if mode == 2:
        player_point = mse["players"]
        if player_point == "1":
            message = random.choice(QUEREN[1])
        elif player_point == "2":
            message = random.choice(QUEREN[2])
        elif player_point == "3":
            message = random.choice(QUEREN[3])
        else:
            message = random.choice(QUEREN[4])
    if mode == 3:
        message = random.choice(KAILAO)
    message += "\n" + "名称：" + mse["name"] + "\n"
    message += "地图：" + mse["map_"] + "\n"
    message += f"玩家：{mse['players']} / {mse['max_players']}\n"
    try:
        message += await msg_ip_to_list(mse["Players"])
    except KeyError:
        message += "服务器里，是空空的呢\n"
    return message


async def get_server_ip(number):
    group, host, port = await si.query_number(number)
    try:
        return str(host) + ":" + str(port)
    except TypeError:
        return None


async def write_json(data_str: str):
    """
    添加数据或者删除数据
     - 【求生更新 添加 腐竹 ip 模式 序号】
     - 【求生更新 添加 腐竹 ip 模式】
     - 【求生更新 删除 腐竹 序号】
    """
    data_list = data_str.split()
    logger.info(data_list)
    if data_list[0] == "添加":
        add_server = {}
        server_dict = ALL_HOST.get(data_list[1], {})
        if not server_dict:
            logger.info("新建分支")
            ALL_HOST[data_list[1]] = []
        for key, value in ALL_HOST.items():
            if data_list[1] == key:
                ids = [server["id"] for server in value]
                # 序号
                if len(data_list) == 4:
                    data_num = int(max(ids, default=0)) + 1
                    add_server.update({"id": data_num})
                elif len(data_list) == 5:
                    if not data_list[4].isdigit():
                        return "序号应该为大于0的正整数，请输入【求生更新 添加 腐竹 ip 模式 序号】"
                    data_num = int(data_list[4])
                    if data_num in ids:
                        return "该序号已存在，请尝试删除原序号【求生更新 删除 腐竹 序号】"
                    add_server.update({"id": data_num})
                else:
                    return "输入参数错误，请输入【求生更新 添加 腐竹 ip 模式 序号】或【求生更新 添加 腐竹 ip 模式】"
                # 模式，ip
                try:
                    host, port = split_maohao(data_list[2])
                    add_server.update({"host": host, "port": port})
                except KeyError:
                    return "ip格式不正确【114.11.4.514:9191】"
                add_server.update({"version": data_list[3]})
                value.append(add_server)
                ALL_HOST[key] = value
                with open("data/L4D2/l4d2.json", "w", encoding="utf8") as f_new:
                    json.dump(ALL_HOST, f_new, ensure_ascii=False, indent=4)
                return f"添加成功，指令为{key}{data_num}"

    elif data_list[0] == "删除":
        for key, value in ALL_HOST.items():
            if data_list[1] == key:
                try:
                    data_num = int(data_list[2])
                except ValueError:
                    return "序号应该为大于0的正整数，请输入【求生更新 删除 腐竹 序号】"
                for i, server in enumerate(value):
                    if data_num == server["id"]:
                        value.pop(i)
                        if not value:
                            ALL_HOST.pop(key)
                        with open("data/L4D2/l4d2.json", "w", encoding="utf8") as f_new:
                            json.dump(ALL_HOST, f_new, ensure_ascii=False, indent=4)
                        return "删除成功喵"
                return "序号不正确，请输入【求生更新 删除 腐竹 序号】"
        return "腐竹名不存在，请输入【求生更新 删除 腐竹 序号】"


async def add_ip(group_id, host, port):
    """先查找是否存在，如果不存在则创建"""
    return await bind_group_ip(group_id, host, port)


async def del_ip(group_id, number):
    """删除群ip"""
    return await del_group_ip(group_id, number)


async def show_ip(group_id):
    """先查找群ip，再根据群ip返回"""
    data_list = await get_qqgroup_ip_msg(group_id)
    logger.info(data_list)
    if len(data_list) == 0:
        return "本群没有订阅"
    msg = await qq_ip_queries_pic(data_list)
    return msg


async def get_number_url(number):
    ip = await get_server_ip(number)
    if not ip:
        return "该序号不存在"
    url = f"connect {ip}"
    return url


async def server_rule_dict(ip: str, port: int):
    port = int(port)
    ip = str(ip)
    msg_dict = {}
    # message_dict = await l4d(ip,port)
    try:
        msg: dict = await a2s.arules((ip, port))  # type: ignore
        msg_dict["tick"] = msg["l4d2_tickrate_enabler"] + "tick"
    except:
        msg_dict["tick"] = ""
    return msg_dict
