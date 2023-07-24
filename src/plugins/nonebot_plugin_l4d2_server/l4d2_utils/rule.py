from nonebot.adapters.onebot.v11 import Message, NoticeEvent
from nonebot.params import CommandArg, Depends
from nonebot.rule import Rule

from .config import file_format, l4_config


async def full_command(arg: Message = CommandArg()) -> bool:
    return not bool(str(arg))


def FullCommand() -> Rule:
    return Rule(full_command)


def FullCommandDepend():
    return Depends(full_command)


def wenjian(event: NoticeEvent):
    args = event.dict()
    try:
        name: str = args["file"]["name"]
        usr_id = str(args["user_id"])
    except KeyError:
        return False
    if args["notice_type"] == "offline_file":
        if l4_config.l4_master:
            return name.endswith(file_format) and usr_id in l4_config.l4_master
        else:
            return name.endswith(file_format)
    elif args["notice_type"] == "group_upload":
        if l4_config.l4_master:
            return usr_id in l4_config.l4_master and name.endswith(file_format)
        else:
            return False
    return False
