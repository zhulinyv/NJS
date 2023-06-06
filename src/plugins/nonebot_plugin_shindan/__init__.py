import re
import traceback
from typing import List, Union

from nonebot import on_command, on_message, require
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import Message as V12Msg
from nonebot.adapters.onebot.v12 import MessageEvent as V12MEvent
from nonebot.adapters.onebot.v12 import MessageSegment as V12MsgSeg
from nonebot.log import logger
from nonebot.params import CommandArg, EventMessage, EventPlainText
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule, to_me
from nonebot.typing import T_State

require("nonebot_plugin_datastore")
require("nonebot_plugin_htmlrender")

from nonebot_plugin_datastore.db import post_db_init

from .config import Config
from .manager import shindan_manager
from .shindanmaker import (
    download_image,
    get_shindan_title,
    make_shindan,
    render_shindan_list,
)

post_db_init(shindan_manager.load_shindan_records)

__plugin_meta__ = PluginMetadata(
    name="趣味占卜",
    description="使用ShindanMaker网站的趣味占卜",
    usage="发送“占卜列表”查看可用占卜\n发送“{占卜名} {名字}”使用占卜",
    config=Config,
    extra={
        "unique_name": "shindan",
        "example": "人设生成 小Q",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.3.4",
    },
)

add_usage = """Usage:
添加占卜 {id} {指令}
如：添加占卜 917962 人设生成"""

del_usage = """Usage:
删除占卜 {id}
如：删除占卜 917962"""

set_usage = """Usage:
设置占卜 {id} {mode}
设置占卜输出模式：'text' 或 'image'(默认)
如：设置占卜 360578 text"""

cmd_sd = on_command(
    "占卜", aliases={"shindan", "shindanmaker"}, rule=to_me(), block=True, priority=13
)
cmd_ls = on_command("占卜列表", aliases={"可用占卜"}, block=True, priority=13)
cmd_add = on_command("添加占卜", permission=SUPERUSER, block=True, priority=13)
cmd_del = on_command("删除占卜", permission=SUPERUSER, block=True, priority=13)
cmd_set = on_command("设置占卜", permission=SUPERUSER, block=True, priority=13)


@cmd_sd.handle()
async def _():
    await cmd_sd.finish(__plugin_meta__.usage)


@cmd_ls.handle()
async def _(bot: Union[V11Bot, V12Bot]):
    if not shindan_manager.shindan_records:
        await cmd_ls.finish("尚未添加任何占卜")

    img = await render_shindan_list(shindan_manager.shindan_records)

    if isinstance(bot, V11Bot):
        await cmd_ls.finish(V11MsgSeg.image(img))
    elif isinstance(bot, V12Bot):
        resp = await bot.upload_file(type="data", name="shindan", data=img)
        file_id = resp["file_id"]
        await cmd_ls.finish(V12MsgSeg.image(file_id))


@cmd_add.handle()
async def _(msg: Union[V11Msg, V12Msg] = CommandArg()):
    arg = msg.extract_plain_text().strip()
    if not arg:
        await cmd_add.finish(add_usage)

    args = arg.split()
    if len(args) != 2 or not args[0].isdigit():
        await cmd_add.finish(add_usage)

    id = args[0]
    command = args[1]
    title = await get_shindan_title(id)
    if not title:
        await cmd_add.finish("找不到该占卜，请检查id")

    if resp := await shindan_manager.add_shindan(id, command, title):
        await cmd_add.finish(resp)
    else:
        await cmd_add.finish(f"成功添加占卜“{title}”，可通过“{command} 名字”使用")


@cmd_del.handle()
async def _(msg: Union[V11Msg, V12Msg] = CommandArg()):
    arg = msg.extract_plain_text().strip()
    if not arg:
        await cmd_del.finish(del_usage)

    if not arg.isdigit():
        await cmd_del.finish(del_usage)

    id = arg

    if resp := await shindan_manager.remove_shindan(id):
        await cmd_add.finish(resp)
    else:
        await cmd_del.finish("成功删除该占卜")


@cmd_set.handle()
async def _(msg: Union[V11Msg, V12Msg] = CommandArg()):
    arg = msg.extract_plain_text().strip()
    if not arg:
        await cmd_set.finish(set_usage)

    args = arg.split()
    if len(args) != 2 or not args[0].isdigit() or args[1] not in ["text", "image"]:
        await cmd_set.finish(set_usage)

    id = args[0]
    mode = args[1]

    if resp := await shindan_manager.set_shindan_mode(id, mode):
        await cmd_add.finish(resp)
    else:
        await cmd_set.finish("设置成功")


def sd_handler() -> Rule:
    async def handle(
        bot: Union[V11Bot, V12Bot],
        event: Union[V11MEvent, V12MEvent],
        state: T_State,
        msg: Union[V11Msg, V12Msg] = EventMessage(),
        msg_text: str = EventPlainText(),
    ) -> bool:
        async def get_name(command: str) -> str:
            name = ""
            if isinstance(bot, V11Bot):
                assert isinstance(event, V11MEvent)
                for msg_seg in msg:
                    if msg_seg.type == "at":
                        assert isinstance(event, V11GMEvent)
                        info = await bot.get_group_member_info(
                            group_id=event.group_id, user_id=msg_seg.data["qq"]
                        )
                        name = info.get("card", "") or info.get("nickname", "")
                        break
                if not name:
                    name = msg_text[len(command) :].strip()
                if not name:
                    name = event.sender.card or event.sender.nickname
            elif isinstance(bot, V12Bot):
                assert isinstance(event, V12MEvent)

                async def get_user_name(user_id: str):
                    resp = await bot.get_user_info(user_id=user_id)
                    return resp["user_displayname"] or resp["user_name"]

                for msg_seg in msg:
                    if msg_seg.type == "mention":
                        name = await get_user_name(msg_seg.data["user_id"])
                        break
                if not name:
                    name = msg_text[len(command) :].strip()
                if not name:
                    name = await get_user_name(event.user_id)

            return name or ""

        for record in sorted(
            shindan_manager.shindan_records,
            reverse=True,
            key=lambda record: record.command,
        ):
            if msg_text.startswith(record.command):
                name = await get_name(record.command)
                state["id"] = record.shindan_id
                state["name"] = name
                state["mode"] = record.mode
                return True
        return False

    return Rule(handle)


sd_matcher = on_message(sd_handler(), priority=13)


@sd_matcher.handle()
async def _(bot: Union[V11Bot, V12Bot], state: T_State):
    id: str = state["id"]
    name: str = state["name"]
    mode: str = state["mode"]
    try:
        res = await make_shindan(id, name, mode)
    except:
        logger.warning(traceback.format_exc())
        await sd_matcher.finish("出错了，请稍后再试")

    msgs: List[Union[str, bytes]] = []
    if isinstance(res, str):
        img_pattern = r"((?:http|https)://\S+\.(?:jpg|jpeg|png|gif|bmp|webp))"
        for msg in re.split(img_pattern, res):
            if re.match(img_pattern, msg):
                try:
                    img = await download_image(msg)
                    msgs.append(img)
                except:
                    logger.warning(f"{msg} 下载出错！")
            else:
                msgs.append(msg)
    elif isinstance(res, bytes):
        msgs.append(res)

    if not msgs:
        await sd_matcher.finish()

    if isinstance(bot, V11Bot):
        message = V11Msg()
        for msg in msgs:
            if isinstance(msg, bytes):
                message.append(V11MsgSeg.image(msg))
            else:
                message.append(msg)
    else:
        message = V12Msg()
        for msg in msgs:
            if isinstance(msg, bytes):
                resp = await bot.upload_file(type="data", name="shindan", data=msg)
                file_id = resp["file_id"]
                message.append(V12MsgSeg.image(file_id))
            else:
                message.append(msg)
    await sd_matcher.finish(message)
