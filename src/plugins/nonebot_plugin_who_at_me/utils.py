from typing import Dict, Any

from nonebot.adapters.onebot.v11 import MessageSegment


def node_custom(
    user_id: int, name: str, time: int, content: MessageSegment
) -> "MessageSegment":
    return MessageSegment(
        type="node",
        data={"uin": str(user_id), "name": name, "content": content, "time": time},
    )


def get_member_name(member: Dict[str, Any]) -> "str":
    return member["card"] if not len(member["card"]) == 0 else member["nickname"]
