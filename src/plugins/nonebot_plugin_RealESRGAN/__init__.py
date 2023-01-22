from .utils import *
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment, Bot, Event
from nonebot.params import T_State, CommandArg
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11.helpers import HandleCancellation
from json import loads
from nonebot import get_driver

try:
    api = loads(get_driver().config.json())["realesrgan_api"]
except:
    api = 'https://hf.space/embed/ppxxxg22/Real-ESRGAN/api/predict/'

real_esrgan = on_command(
    "重建", aliases={"超分", "real-esrgan", "超分辨率重建", "esrgan", "real_esrgan"}, priority=30, block=True
)


@real_esrgan.handle()
async def real_esrgan_handle_first(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    args: Message = CommandArg(),
):
    state['id'] = event.get_user_id()
    for seg in args:
        if seg.type == "text":
            state["mode"] = seg.data["text"].strip()
        if seg.type == "image":
            state['img'] = seg
            break


@real_esrgan.got("mode", prompt="请提供重建模式(二刺螈:anime，其他:base)，模式不绝对，可以任意选", parameterless=[HandleCancellation("已取消")])
async def real_esrgan_get_mode(event: MessageEvent, state: T_State):
    mode = str(state["mode"]).strip()
    if mode not in ["anime", "base"]:
        await real_esrgan.reject('"base" | "anime", 二选一')


@real_esrgan.got("img", prompt="请上传需要超分辨率重建的图片", parameterless=[HandleCancellation("已取消")])
async def real_esrgan_handle_img(event: MessageEvent, state: T_State):
    # 先拿到需要转换的图
    for seg in state["img"]:
        if seg.type == "image":
            img = await get_img(seg.data["url"])
            break
    else:
        await real_esrgan.finish(Message(f"[CQ:at,qq={state['id']}]不是图捏"))
    # 下面来处理图片
    try:
        json_data = img_encode_to_json(img, state['mode'])  # 先获取图片并进行编码
        if json_data is None:
            await real_esrgan.finish(Message(f"[CQ:at,qq={state['id']}]服务器无法接收到这张图捏,要不重试试试？"))
        result = await get_result(json_data, api=api)  # 然后进行超分辨率重建
        if result is None:
            await real_esrgan.finish(Message(f"[CQ:at,qq={state['id']}]这张图没能被正确解析，可能网络连接失败或者是由于远程服务器免费额度耗尽，如果是后者建议联系管理员使用自建仓库(免费)"))
        img = img_decode_from_json(result)  # 获取重建后图片并进行解码发送
        await real_esrgan.finish(MessageSegment.image(img))
    except Exception as e:
        ...
        # print('错误类型是', e.__class__.__name__)
        # print('错误明细是', e)
