from io import BytesIO

from httpx import AsyncClient
from PIL import Image

from nonebot import logger, on_keyword, get_driver
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    PrivateMessageEvent,
    GroupMessageEvent,
    MessageEvent,
)
from nonebot.adapters.onebot.v11.helpers import extract_image_urls
from nonebot.params import Arg
from nonebot.rule import Rule
from nonebot.exception import ActionFailed
from nonebot.internal.matcher import Matcher
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata

from . import decode
from .config import Config
from .exception import QRDecodeError

__plugin_meta__ = PluginMetadata(
    name="二维码",
    description="解析二维码",
    usage="""命令: {#} {扫码}
示例: #扫码
大括号内{}为必要关键字
附带一张图片、或回复一张图片、或再发送一张图片
可以自定义命令符、命令关键字""",
    type="application",
    homepage="https://github.com/tomorinao-www/nonebot-plugin-qrcode2",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

config: Config = Config.parse_obj(get_driver().config)


async def _cmd_check(bot: Bot, event: MessageEvent):
    txt_msg = event.message.extract_plain_text().strip()
    if config.qrcode_cmd in txt_msg:
        return True


qr = on_keyword(
    config.qrcode_keyword,
    rule=Rule(_cmd_check),
    priority=config.qrcode_priority,
    block=True,
)


@qr.handle()
async def _(event: MessageEvent, matcher: Matcher):
    # 获取图片链接
    message = event.reply.message if event.reply else event.message
    if imgs := message["image"]:
        matcher.set_arg("imgs", imgs)


@qr.got("imgs", prompt="请发送需要识别的图片")
async def get_image(state: T_State, imgs: Message = Arg()):
    img_urls = extract_image_urls(imgs)
    if not img_urls:
        await qr.reject("没有找到图片, 请重新发送")
    state["img_urls"] = img_urls


@qr.handle()
async def main(bot: Bot, event: MessageEvent, state: T_State):
    # 拿到图片
    img_urls = state["img_urls"]
    async with AsyncClient(trust_env=False) as client:
        res = await client.get(img_urls[0])
        if res.is_error:
            await qr.finish("获取图片失败")
        base_img = Image.open(BytesIO(res.content)).convert("RGB")

    # 识别二维码
    try:
        decoded_list, decode_name = decode.all_decode(base_img)
    except QRDecodeError:
        await qr.finish(f"图中没有二维码")
    except Exception as e:
        logger.error(repr(e))
        await qr.finish(f"扫码失败{repr(e)}")
    
    # 构造消息
    qr_num = len(decoded_list)
    res_start_msg = Message(f"共识别到{qr_num}个二维码\nby {decode_name}")
    message_list: list[Message] = [res_start_msg]
    for txt, box in decoded_list:
        img_bytes = BytesIO()
        item_img = base_img.crop(box)
        item_img.save(img_bytes, format="JPEG")
        msg_txt = Message(txt)
        message = msg_txt + MessageSegment.image(img_bytes.getvalue())
        message_list.append(message)

    # 发送消息
    if len(message_list) == 2:
        await qr.finish(message_list[1], reply_message=True)
    # 若识别出2个及以上二维码，发送合并转发消息
    nickname = config.nickname[0] if config.nickname else "qrcode2"
    try:
        msgs = [
            {
                "type": "node",
                "data": {
                    "name": nickname,
                    "uin": bot.self_id,
                    "content": msg,
                },
            }
            for msg in message_list
        ]
        # 发送转发消息
        await bot.send_forward_msg(
            user_id=event.user_id if isinstance(event, PrivateMessageEvent) else 0,
            group_id=event.group_id if isinstance(event, GroupMessageEvent) else 0,
            messages=msgs,
        )
    except ActionFailed as e:
        logger.warning(e)
        await qr.finish(
            message=Message("消息被风控了~合并消息发送失败"),
            at_sender=True,
        )
