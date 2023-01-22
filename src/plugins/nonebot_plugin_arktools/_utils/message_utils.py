from typing import Union, List


def merge_msg(msg_list: List[str], uin: Union[int, str]) -> List[dict]:
    """
    生成自定义合并消息
    :param msg_list: 消息列表
    :param uin: 发送者 QQ
    """
    uin = int(uin)
    mes_list = []
    for _message in msg_list:
        data = {
            "type": "node",
            "data": {
                "name": "test",
                "uin": f"{uin}",
                "content": _message,
            },
        }
        mes_list.append(data)
    return mes_list
