from typing import Set

from nonebot.adapters.onebot.v11 import Message


def extract_member_at(message: Message) -> Set[str]:
    """提取消息中被艾特人的QQ号
    参数:
        message: 消息对象
    返回:
        被艾特集合
    """
    return {
        segment.data["qq"]
        for segment in message
        if (segment.type == "at") and ("qq" in segment.data)
    }
