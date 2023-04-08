import io
import httpx
import asyncio
import urllib.request
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent

from .ocr_local import *
from .ocr_api import api_paddle_ocr





local_ocr = on_command("ocr", aliases={"OCR"}, priority=50, block=True)

@local_ocr.handle()
async def _():
    await local_ocr.send("请发送要识别的图片(支持中英文和数字)", at_sender=True)

@local_ocr.got("pic")
async def get_pic(event: MessageEvent):
    # 判断收到的信息是否为图片，不是则结束
    if not (str(event.message).find("[CQ:image") + 1):
        await local_ocr.finish("不是图片捏~", at_sender=True)
    for seg in event.message:
        if seg.type == "image":
            pic_url = seg.data["url"]
    async with httpx.AsyncClient() as client:
        response = await client.get(pic_url, timeout=10)
        with open('./src/plugins/ocr/ocr.jpg', 'wb') as f:
            f.write(response.content)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, ocr_local)
    await local_ocr.finish(f"识别结果: \n{result}", at_sender=True)





api_ocr = on_command("apiocr", aliases={"APIOCR"}, priority=50, block=True)

@api_ocr.handle()
async def _():
    await api_ocr.send("请发送要识别的图片(支持中英文和数字)", at_sender=True)

@api_ocr.got("pic")
async def get_pic(event: MessageEvent):
    # 判断收到的信息是否为图片，不是则结束
    if not (str(event.message).find("[CQ:image") + 1):
        await api_ocr.finish("不是图片捏~", at_sender=True)
    for seg in event.message:
        if seg.type == "image":
            pic_url = seg.data["url"]
    response = urllib.request.urlopen(pic_url)
    img = io.BytesIO(response.read())
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, api_paddle_ocr, img)
    await api_ocr.finish(f"识别结果: \n{result}", at_sender=True)