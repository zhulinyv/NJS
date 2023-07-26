import shlex
from io import BytesIO
from typing import List, Union

from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v11.utils import unescape
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import Message as V12Msg
from nonebot.adapters.onebot.v12 import MessageEvent as V12MEvent
from nonebot.params import CommandArg, Depends
from pil_utils import BuildImage
from typing_extensions import Literal

from .utils import download_url


def Imgs():
    async def dependency(
        bot: Union[V11Bot, V12Bot],
        event: Union[V11MEvent, V12MEvent],
        msg: Union[V11Msg, V12Msg] = CommandArg(),
    ):
        urls: List[str] = []
        if isinstance(bot, V11Bot):
            assert isinstance(event, V11MEvent)
            assert isinstance(msg, V11Msg)
            img_segs = msg["image"]
            if event.reply:
                img_segs = event.reply.message["image"].extend(img_segs)
            urls = [seg.data["url"] for seg in img_segs]
        else:
            assert isinstance(event, V12MEvent)
            assert isinstance(msg, V12Msg)
            img_segs = msg["image"]
            for seg in img_segs:
                file_id = seg.data["file_id"]
                data = await bot.get_file(type="url", file_id=file_id)
                urls.append(data["url"])

        return [BuildImage.open(BytesIO(await download_url(url))) for url in urls]

    return Depends(dependency)


def Img():
    async def dependency(imgs: List[BuildImage] = Imgs()):
        if len(imgs) == 1:
            return imgs[0]

    return Depends(dependency)


def Arg():
    async def dependency(msg: Union[V11Msg, V12Msg] = CommandArg()):
        if isinstance(msg, V11Msg):
            return unescape(msg.extract_plain_text().strip())
        else:
            return msg.extract_plain_text().strip()

    return Depends(dependency)


def Args():
    async def dependency(arg: str = Arg()):
        try:
            args = shlex.split(arg)
        except:
            args = arg.split()
        args = [a for a in args if a]
        return args

    return Depends(dependency)


def NoArg():
    async def dependency(arg: Literal[""] = Arg()):
        return

    return Depends(dependency)
