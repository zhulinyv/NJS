from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot
from nonebot import logger, on_command, on_shell_command
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.rule import ArgumentParser
from argparse import Namespace

import aiohttp

from ..config import config

vits = ArgumentParser()
vits.add_argument("-s", type=int, help="设置speaker", dest="speaker")
vits.add_argument("-v", "--value", type=str, help="设置值", dest="value")
vits.add_argument("-s", "--search", type=str, help="搜索设置名", dest="search")
vits.add_argument("-get", action='store_true', help="获取speaker列表", dest="get_list")

vits_ = on_shell_command(
    "vits",
    parser=vits,
    priority=5
)


def voice_vits(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max=50):
    fields = {
        "text": text,
        "id": str(id),
        "format": format,
        "lang": lang,
        "length": str(length),
        "noise": str(noise),
        "noisew": str(noisew),
        "max": str(max)
    }


class VITS:

    def __init__(self, 
                 event: MessageEvent,  # 传递的事件对象
                 text: str = "",  # 要转换为语音的文本
                 id: str = "1",  # 语音文件的ID，默认为"1"
                 format: str = "wav",  # 语音文件的格式，默认为"wav"
                 lang: str = "auto",  # 文本语言，默认为"auto"（自动检测语言）
                 length: int = 1,  # 语音长度（秒），默认为1秒
                 noise: float = 0.667,  # 噪音水平，默认为0.667
                 noisew: float = 0.8,  # 噪音权重，默认为0.8
                 max: int = 50  # 最大请求数，默认为50
                 ):
        self.event = event
        self.text = text
        self.id = id
        self.format = format
        self.lang = lang
        self.length = length
        self.noise = noise
        self.noisew = noisew
        self.max = max

    async def http_req(self,  payload, method=1):
        if method == 1:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=f"http://{config.vits_site}/voice/speakers") as resp:
                    pass


@vits_.handle()
async def _(event: MessageEvent, bot: Bot, args: Namespace = ShellCommandArgs()):
    vits_instance = VITS(event=event)
    if args.get_list:
        await vits_instance.http_req()

