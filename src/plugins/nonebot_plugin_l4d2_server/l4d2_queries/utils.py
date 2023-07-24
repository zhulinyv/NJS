# -*- coding: utf-8 -*-
import random
import struct
from typing import List

import a2s
from nonebot.log import logger
from pydantic import BaseModel

from ..l4d2_utils.config import l4_config
from ..l4d2_utils.txt_to_img import mode_txt_to_img
from ..l4d2_utils.utils import split_maohao
from .localIP import ALL_HOST


class GROUP_MSG(BaseModel):
    tag: str
    online_server: int
    empty_server: int
    full_server: int
    max_server: int

    online_player: int
    max_player: int

    def __str__(self) -> str:
        return f"""组:{self.tag}
    在线服务器:{self.online_server}/{self.max_server}
    空服务器:{self.empty_server}/{self.max_server}
    在线玩家数量:{self.online_player}/{self.max_player}"""


async def queries_server(msg: list) -> str:
    """查询ip返回信息"""
    ip = msg[0]
    port = msg[1]
    msgs = ""
    try:
        msgs = await queries(ip, port)
        msgs += await player_queries(ip, port)
    except (struct.error, TimeoutError):
        pass
    # except Exception:
    # msgs = '有无法识别的用户名'
    # return msgs
    return msgs


async def get_anne_server_ip(ip, ismsg: bool = False):
    """输出查询ip和ping"""
    host, port = split_maohao(ip)
    data = await queries_server([host, port])

    if l4_config.l4_image:
        data = mode_txt_to_img(
            data.split("\n")[0], data.replace(data.split("\n")[0], f"\nconnect {ip}")
        )
    else:
        data += f"\nconnect {ip}"
    return data


async def json_server_to_tag_dict(key: str, msg: str):
    """
    l4d2字典转tag的dict结果
     - 1、先匹配腐竹
     - 2、匹配数字（几服），没有参数则从结果里随机返回一个
    """
    data_dict = {}
    msg = msg.replace(" ", "")
    # 腐竹循环
    for tag, value in ALL_HOST.items():
        value: List[dict]
        if tag == key:
            data_dict.update({"server": tag})
            if not msg:
                # 腐竹
                data_dict.update(random.choice(value))
            elif msg.isdigit():
                logger.info("腐竹 + 序号")
                for server in value:
                    if msg == str(server["id"]):
                        data_dict.update(server)
                        break

    return data_dict


async def player_queries_anne_dict(ip: str, port: int):
    """anne算法返回玩家"""
    port = int(port)
    # message_dic = await l4d2.APlayer(ip,port,times=5)
    message_list: List[a2s.Player] = await a2s.aplayers((ip, port))  # type: ignore
    msg_list = []
    if message_list != []:
        for i in message_list:
            msg_list.append(
                {
                    "name": i.name,
                    "Score": i.score,
                    "Duration": await convert_duration(i.duration),
                }
            )
    return msg_list


async def player_queries(ip: str, port: int):
    port = int(port)
    message_list = await player_queries_anne_dict(ip, port)
    return await msg_ip_to_list(message_list)


async def msg_ip_to_list(message_list: list):
    message = ""
    n = 0
    if message_list == []:
        message += "服务器里，是空空的呢\n"
    else:
        max_duration_len = max([len(str(i["Duration"])) for i in message_list])
        max_score_len = max([len(str(i["Score"])) for i in message_list])
        for i in message_list:
            n += 1
            name = i["name"]
            Score = i["Score"]
            if Score == "0":
                Score = "摸"
            Duration = i["Duration"]
            soc = "[{:>{}}]".format(Score, max_score_len)
            dur = "{:^{}}".format(Duration, max_duration_len)
            message += f"{soc} | {dur} | {name} \n"
    return message


async def convert_duration(duration: float) -> str:
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    time_str = ""
    if hours > 0:
        time_str += f"{int(hours)}h "
    if minutes > 0 or hours > 0:
        time_str += f"{int(minutes)}m "
    time_str += f"{int(seconds)}s"
    return time_str.strip()


async def queries(ip: str, port: int):
    port = int(port)
    msg_dict = await queries_dict(ip, port)
    message = f"名称：{msg_dict['name']}\n"
    message += f"地图：{msg_dict['map_']}\n"
    message += f"延迟：{msg_dict['ping']}\n"
    message += f"玩家：{msg_dict['players']} / {msg_dict['max_players']}\n"
    return message


async def queries_dict(ip: str, port: int) -> dict:
    port = int(port)
    ip = str(ip)
    msg_dict = {}
    # message_dict = await l4d(ip,port)
    msg: a2s.SourceInfo = await a2s.ainfo((ip, port))  # type: ignore
    msg_dict["folder"] = msg.folder
    msg_dict["name"] = msg.server_name
    msg_dict["map_"] = msg.map_name
    msg_dict["players"] = msg.player_count
    msg_dict["max_players"] = msg.max_players
    msg_dict["rank_players"] = f"{msg.player_count}/{msg.max_players}"
    msg_dict["ip"] = str(ip) + ":" + str(port)
    msg_dict["ping"] = f"{msg.ping*1000:.0f}ms"
    msg_dict["system"] = f"{msg.platform}.svg"
    if msg_dict["players"] < msg_dict["max_players"]:
        msg_dict["enabled"] = True
    else:
        msg_dict["enabled"] = False
    return msg_dict
