from typing import Dict, List, Tuple

from ..l4d2_utils.utils import split_maohao
from .localIP import ALL_HOST, Group_All_HOST
from .qqgroup import qq_ip_querie


async def get_group_ip_to_msg(command: str, text: str = ""):
    """输出群组ip"""
    if not text:
        group_tag_list: List[str] = Group_All_HOST[command]
        group_ip_dict: Dict[str, List[Dict[str, str]]] = {}
        for tag, one_group in ALL_HOST.items():
            if tag in group_tag_list:
                group_ip_dict.update({tag: one_group})
                ip_tuple_list: List[Tuple[str, str, int]] = []
                for one_server in one_group:
                    number = one_server["id"]
                    host, port = split_maohao(one_server["ip"])
                    ip_tuple_list.append((number, host, int(port)))
                msg_group_server = await qq_ip_querie(ip_tuple_list)
                send_dict = await check_group_msg(msg_group_server)
            else:
                continue
            # 还没写完
        #     host, port = split_maohao(one_ip["ip"])
        #     msg_tuple = (one_ip["id"], host, port)
        #     ip_list.append(msg_tuple)
        # img = await qq_ip_queries_pic(ip_list, igr)


async def check_group_msg(msg: Dict[str, List[Dict[str, str]]]):
    ...
