from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot
from nonebot import logger, on_command, on_shell_command
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.rule import ArgumentParser
from argparse import Namespace
from ..extension.safe_method import send_forward_msg
from ..extension.safe_method import risk_control

import aiohttp
import aiofiles
import json
import os

from ..config import config

vits_file_path = "data/novelai/bits_speakers.json"

vits = ArgumentParser()
vits.add_argument("text", nargs="*", help="文本")
vits.add_argument("-s", type=int, help="设置speaker", dest="id")
vits.add_argument("-get", action='store_true', help="获取speaker列表", dest="get_list")

vits_ = on_shell_command(
    "vits",
    parser=vits,
    priority=5
)

class VITS:

    def __init__(self, 
                 event: MessageEvent,  # 传递的事件对象
                 text: str = "",  # 要转换为语音的文本
                 id: str = "1",  # 语音文件的ID，默认为"1"
                 format: str = "wav",  # 语音文件的格式，默认为"wav"
                 lang: str = "auto",  # 文本语言，默认为"auto"（自动检测语言）
                 length: int = 1,  
                 noise: float = 0.667,  # 噪音水平，默认为0.667
                 noisew: float = 0.8,  # 噪音权重，默认为0.8
                 max: int = 50,  
                 **kwargs,
                 ):
        
        self.event = event
        self.text = text
        self.id = id or "1"
        self.format = format
        self.lang = lang
        self.length = length
        self.noise = noise
        self.noisew = noisew
        self.max = max
        self.params = None

    async def http_req(self,  
                       payload = {}, 
                       method = 1, 
                       end_point = "/voice/speakers",
                       params = {},
                       read = False
    ) -> aiohttp.ClientResponse or bytes:
        url = f"http://{config.vits_site}{end_point}"
        if method == 1:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, params=params) as resp:
                    if resp.status not in [200, 201]:
                        logger.error(f"VITS API出错, 错误代码{resp.status}, 错误信息{await resp.text()}")
                        raise RuntimeError
                    if read:
                        bytes_ = await resp.content.read()
                        return bytes_
                    resp_json = await resp.json()
                    return resp_json

    def get_params(self):

        self.params = {
            "text": self.text,
            "id": self.id,
            "format": self.format,
            "lang": self.lang,
            "noise": self.noise,
            "noisew": self.noisew,
            "max": self.max
        }


@vits_.handle()
async def _(event: MessageEvent, 
            bot: Bot, 
            args: Namespace = ShellCommandArgs()
            ):
    
    vits_instance = VITS(**vars(args), event=event)
    if args.get_list:
        resp_ = await vits_instance.http_req()
        async with aiofiles.open(vits_file_path, "w") as f:
            await f.write(json.dumps(resp_))
        # await send_forward_msg(bot, event, event.sender.nickname, str(event.user_id), resp_["VITS"])
        await risk_control(bot, event, resp_["VITS"], True, True)
        
    vits_instance.get_params()
    audio_resp = await vits_instance.http_req(end_point="/voice", params=vits_instance.params, read=True)
    await bot.send(event, message=MessageSegment.record(audio_resp))
        # await vits_.finish(f"出错了，{audio_resp.status}, {await audio_resp.text()}")
    