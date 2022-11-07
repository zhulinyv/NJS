import base64
from argparse import Namespace
from io import BytesIO
from typing import List, Union
from urllib.parse import urljoin

import httpx
from httpx import TimeoutException
from nonebot import on_shell_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.adapters.onebot.v11.helpers import (
    Cooldown,
    CooldownIsolateLevel,
    autorevoke_send,
    extract_image_urls,
)
from nonebot.exception import ParserExit
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Arg, ShellCommandArgs
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from PIL import Image, UnidentifiedImageError

from .config import *
from .database import DrawCount
from .limit import daily_limiter, limiter
from .manage import group_checker, group_manager, shield_filter, shield_manager

try:
    import ujson as json
except ImportError:
    import json

TAGS_PROMPT = "请输入描述性的单词或短句"


cooldown = Cooldown(
    cooldown=cooldown_time, prompt="AI绘图冷却中……", isolate_level=CooldownIsolateLevel.USER
)


async def get_tags(state: T_State, tags: str = Arg()):
    state["tags"] = tags


async def filter_tags(event: MessageEvent, matcher: Matcher, state: T_State):
    filter_tags, state["tags"] = shield_filter(state["tags"])
    msg = f"正在努力绘图中……(今日剩余{limiter.last(event.user_id)}次)"
    if filter_tags:
        msg += f"\n已过滤屏蔽词: {filter_tags}"
    await matcher.send(msg, at_sender=True)


async def count_tags(event: MessageEvent, state: T_State):
    if enable_database:
        await DrawCount.count_tags(
            event.user_id,
            event.group_id if isinstance(event, GroupMessageEvent) else 0,
            state["tags"],
        )


async def send_msg(
    bot: Bot,
    event: MessageEvent,
    message: Union[List[Message], Message],
):
    if isinstance(message, Message):
        message = [message]
    for msg in message:
        if revoke_time:
            await autorevoke_send(
                bot, event, msg, revoke_interval=revoke_time, at_sender=True
            )
        else:
            await bot.send(event, msg, at_sender=True)
    limiter.increase(event.user_id)


novel_parser = ArgumentParser()
novel_parser.add_argument("tags", default="", nargs="*", help="描述标签")
novel_parser.add_argument("-p", "--shape", default="", help="画布形状")
novel_parser.add_argument("-c", "--scale", type=float, help="规模")
novel_parser.add_argument("-s", "--seed", type=int, help="种子")
novel_parser.add_argument("-t", "--steps", type=int, help="步骤")
novel_parser.add_argument("-n", "--ntags", default="", nargs="*", help="负面标签")


ai_novel = on_shell_command(
    "绘画",
    aliases={"画画", "画图", "作图", "绘图", "约稿"},
    parser=novel_parser,
    rule=group_checker,
    handlers=[shield_manager, group_manager],
)


@ai_novel.handle()
async def _(args: ParserExit = ShellCommandArgs()):
    await ai_novel.finish(args.message)


@ai_novel.handle([cooldown, daily_limiter()])
async def novel_draw(
    matcher: Matcher,
    state: T_State,
    args: Namespace = ShellCommandArgs(),
):
    shape = args.shape.lower()
    shape_list = ["landscape", "portrait", "square"]

    for s in shape_list:
        if s.startswith(shape):
            shape = s
            break

    if shape not in shape_list:
        await ai_novel.finish("shape 的输入值不正确, 应为 landscape, portrait 或 square")

    args.shape = shape.capitalize()
    args.tags = " ".join(args.tags)
    args.ntags = " ".join(args.ntags)
    state["args"] = args
    if args.tags:
        matcher.set_arg("tags", Message(args.tags))


ai_novel.got("tags", TAGS_PROMPT)(get_tags)

ai_novel.handle()(filter_tags)

ai_novel.handle()(count_tags)


@ai_novel.handle()
async def novel_draw_handle(bot: Bot, event: MessageEvent, state: T_State):
    args = state["args"]
    args.tags = state["tags"]

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                urljoin(api_url, "got_image"),
                params={"token": token, **{k: v for k, v in vars(args).items() if v}},
                timeout=timeout,
            )
    except TimeoutException:
        await ai_novel.finish("绘图请求超时, 请稍后重试")

    if res.is_error:
        logger.error(f"{res.url} {res.status_code}")
        await ai_novel.finish("出现意外的网络错误")
    try:
        info = Image.open(BytesIO(res.content)).info
    except UnidentifiedImageError:
        await ai_novel.finish("API 返回图像异常, 请稍后重试")
    if not info:
        await ai_novel.finish("token失效, 请更换token后重试")
    image = "\n" + MessageSegment.image(res.content)
    comment = json.loads(info["Comment"])
    text = Message(
        text_templet.format(
            **{
                "tags": info["Description"],
                "steps": comment["steps"],
                "seed": comment["seed"],
                "strength": comment["strength"],
                "scale": comment["scale"],
                "ntags": comment["uc"],
            }
        )
    )
    if message_mode == "image":
        msg = image
    elif message_mode == "part":
        msg = [image, text]
    else:
        msg = image + text
    await send_msg(bot, event, msg)


image_parser = ArgumentParser()
image_parser.add_argument("tags", default="", nargs="*", help="描述标签")
image_parser.add_argument(
    "-e", "--strength", type=float, help="允许 AI 改变图像的构成, 降低该值会产生更接近原始图像的效果"
)

ai_image = on_shell_command(
    "以图绘图", aliases={"以图生图", "以图作图", "以图制图"}, parser=image_parser, rule=group_checker
)


@ai_image.handle([cooldown, daily_limiter()])
async def image_draw(
    event: MessageEvent,
    matcher: Matcher,
    state: T_State,
    args: Namespace = ShellCommandArgs(),
):
    message = reply.message if (reply := event.reply) else event.message

    state["args"] = args

    if imgs := message["image"]:
        matcher.set_arg("imgs", Message(imgs))

    if args.tags:
        args.tags = " ".join(args.tags)
        matcher.set_arg("tags", Message(args.tags))


@ai_image.got("imgs", prompt="请发送基准图片")
async def get_image(state: T_State, imgs: Message = Arg()):
    urls = extract_image_urls(imgs)
    if not urls:
        await ai_image.reject("没有找到图片, 请重新发送")
    async with httpx.AsyncClient() as client:
        res = await client.get(urls[0])
        if res.is_error:
            await ai_image.finish("获取图片失败, 请更换图片重试")
        base_img = Image.open(BytesIO(res.content)).convert("RGB")

        if base_img.width > base_img.height:
            state["shape"] = "Landscape"
        elif base_img.width < base_img.height:
            state["shape"] = "Portrait"
        else:
            state["shape"] = "Square"

        state["image_data"] = BytesIO()
        base_img.save(state["image_data"], format="JPEG")


ai_image.got("tags", TAGS_PROMPT)(get_tags)

ai_image.handle()(filter_tags)

ai_image.handle()(count_tags)


@ai_image.handle()
async def image_draw_handle(bot: Bot, event: MessageEvent, state: T_State):
    args = state["args"]

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                urljoin(api_url, "got_image2image"),
                data=base64.b64encode(state["image_data"].getvalue()),  # type: ignore
                params={
                    "token": token,
                    "tags": state["tags"],
                    "shape": state["shape"],
                    "strength": args.strength or 0.6,
                },
                timeout=timeout,
            )
    except TimeoutException:
        await ai_novel.finish("绘图请求超时, 请稍后重试")

    if res.is_error:
        logger.error(f"{res.url} {res.status_code}")
        await ai_novel.finish("出现意外的网络错误")
    msg = "\n" + MessageSegment.image(res.content)
    await send_msg(bot, event, msg)
