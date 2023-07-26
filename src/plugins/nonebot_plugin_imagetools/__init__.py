import imghdr
import math
import tempfile
from datetime import datetime
from io import BytesIO
from itertools import chain
from pathlib import Path
from typing import List, Union
from zipfile import ZIP_BZIP2, ZipFile

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import MessageSegment as V12MsgSeg
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_Handler
from nonebot.utils import run_sync
from PIL.Image import Image as IMG
from pil_utils import BuildImage, Text2Image

from .config import imagetools_config
from .data_source import commands
from .utils import Command

__plugin_meta__ = PluginMetadata(
    name="图片操作",
    description="简单图片操作",
    usage="发送“图片操作”查看支持的指令",
    extra={
        "unique_name": "imagetools",
        "example": "旋转 [图片]",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.2.1",
    },
)


help_cmd = on_command("图片操作", aliases={"图片工具"}, block=True, priority=12)


@run_sync
def help_image() -> BytesIO:
    def cmd_text(commands: List[Command], start: int = 1) -> str:
        texts = []
        for i, meme in enumerate(commands):
            text = f"{i + start}. " + "/".join(meme.keywords)
            texts.append(text)
        return "\n".join(texts)

    head_text = "简单图片操作，支持的操作："
    head = Text2Image.from_text(head_text, 30, weight="bold").to_image(padding=(20, 10))

    imgs: List[IMG] = []
    col_num = 2
    num_per_col = math.ceil(len(commands) / col_num)
    for idx in range(0, len(commands), num_per_col):
        text = cmd_text(commands[idx : idx + num_per_col], start=idx + 1)
        imgs.append(Text2Image.from_text(text, 30).to_image(padding=(20, 10)))
    w = max(sum((img.width for img in imgs)), head.width)
    h = head.height + max((img.height for img in imgs))
    frame = BuildImage.new("RGBA", (w, h), "white")
    frame.paste(head, alpha=True)
    current_w = 0
    for img in imgs:
        frame.paste(img, (current_w, head.height), alpha=True)
        current_w += img.width
    return frame.save_jpg()


@help_cmd.handle()
async def _(bot: Union[V11Bot, V12Bot], matcher: Matcher):
    img = await help_image()

    if isinstance(bot, V11Bot):
        await matcher.finish(V11MsgSeg.image(img))
    else:
        resp = await bot.upload_file(
            type="data", name="imagetools", data=img.getvalue()
        )
        file_id = resp["file_id"]
        await matcher.finish(V12MsgSeg.image(file_id))


def handler_v11(command: Command) -> T_Handler:
    async def handle(
        bot: V11Bot,
        event: V11MEvent,
        matcher: Matcher,
        res: Union[str, BytesIO, List[BytesIO]] = Depends(command.func),
    ):
        if isinstance(res, str):
            await matcher.finish(res)
        elif isinstance(res, BytesIO):
            await matcher.finish(V11MsgSeg.image(res))
        else:
            if len(res) > imagetools_config.imagetools_zip_threshold:
                zip_file = zip_images(res)
                filename = f"{command.keywords[0]}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.zip"
                try:
                    await upload_file(bot, event, zip_file, filename)
                except:
                    logger.warning("上传文件失败")

            msgs: List[V11Msg] = [V11Msg(V11MsgSeg.image(msg)) for msg in res]
            max_forward_msg_num = imagetools_config.max_forward_msg_num
            # 超出最大转发消息条数时，改为一条消息包含多张图片
            if len(msgs) > max_forward_msg_num:
                step = math.ceil(len(msgs) / max_forward_msg_num)
                msgs = [
                    V11Msg(chain.from_iterable(msgs[i : i + step]))
                    for i in range(0, len(msgs) - 1, step)
                ]
            await send_forward_msg(bot, event, "imagetools", bot.self_id, msgs)

    return handle


def handler_v12(command: Command) -> T_Handler:
    async def handle(
        bot: V12Bot,
        matcher: Matcher,
        res: Union[str, BytesIO, List[BytesIO]] = Depends(command.func),
    ):
        if isinstance(res, str):
            await matcher.finish(res)
        elif isinstance(res, BytesIO):
            resp = await bot.upload_file(
                type="data", name="imagetools", data=res.getvalue()
            )
            file_id = resp["file_id"]
            await matcher.finish(V12MsgSeg.image(file_id))
        else:
            zip_file = zip_images(res)
            filename = f"{command.keywords[0]}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.zip"
            resp = await bot.upload_file(
                type="data", name=filename, data=zip_file.getvalue()
            )
            file_id = resp["file_id"]
            await matcher.finish(V12MsgSeg.file(file_id))

    return handle


def create_matchers():
    for command in commands:
        matcher = on_command(
            command.keywords[0], aliases=set(command.keywords), block=True, priority=12
        )
        matcher.append_handler(handler_v11(command))
        matcher.append_handler(handler_v12(command))


create_matchers()


async def send_forward_msg(
    bot: V11Bot,
    event: V11MEvent,
    name: str,
    uin: str,
    msgs: List[V11Msg],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    if isinstance(event, V11GMEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )


def zip_images(files: List[BytesIO]):
    output = BytesIO()
    with ZipFile(output, "w", ZIP_BZIP2) as zip_file:
        for i, file in enumerate(files):
            file_bytes = file.getvalue()
            ext = imghdr.what(None, h=file_bytes)
            zip_file.writestr(f"{i}.{ext}", file_bytes)
    return output


async def upload_file(
    bot: V11Bot,
    event: V11MEvent,
    file: BytesIO,
    filename: str,
):
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(Path(temp_dir) / filename, "wb") as f:
            f.write(file.getbuffer())
        if isinstance(event, V11GMEvent):
            await bot.call_api(
                "upload_group_file", group_id=event.group_id, file=f.name, name=filename
            )
        else:
            await bot.call_api(
                "upload_private_file", user_id=event.user_id, file=f.name, name=filename
            )
