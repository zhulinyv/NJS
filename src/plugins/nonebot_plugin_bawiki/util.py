import datetime
import json
from copy import deepcopy
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
    overload,
)

from aiohttp import ClientSession
from nonebot.adapters.onebot.v11 import Message
from PIL import Image, ImageOps

from .config import config

_T = TypeVar("_T")

req_cache = {}


@overload
async def async_req(
    url,
    *,
    is_json: Literal[True] = True,
    raw: Literal[False] = False,
    ignore_cache=False,
    proxy=config.ba_proxy,
    method="GET",
    session: Optional[ClientSession] = None,
    **kwargs,
) -> Union[Dict[str, Any], list]:
    ...


@overload
async def async_req(
    url,
    *,
    is_json: Literal[False] = False,
    raw: Literal[True] = True,
    ignore_cache=False,
    proxy=config.ba_proxy,
    method="GET",
    session: Optional[ClientSession] = None,
    **kwargs,
) -> bytes:
    ...


@overload
async def async_req(
    url,
    *,
    is_json: Literal[False] = False,
    raw: Literal[False] = False,
    ignore_cache=False,
    proxy=config.ba_proxy,
    method="GET",
    session: Optional[ClientSession] = None,
    **kwargs,
) -> str:
    ...


async def async_req(
    url,
    is_json=True,
    raw=False,
    ignore_cache=False,
    proxy=config.ba_proxy,
    method="GET",
    session: Optional[ClientSession] = None,
    **kwargs,
):
    if (not ignore_cache) and (c := req_cache.get(url)):
        return c

    async with (session or ClientSession()) as c:
        async with c.request(method, url, **kwargs, proxy=proxy) as r:
            ret = (await r.read()) if raw else (await r.text())
            if is_json and (not raw):
                ret = json.loads(ret)
            req_cache[url] = ret
            return ret


def clear_req_cache():
    req_cache.clear()


def format_timestamp(t: int):
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def recover_alia(origin: str, alia_dict: Dict[str, List[str]]):
    origin = replace_brackets(origin).strip()
    origin_ = origin.lower()

    # 精确匹配
    for k, li in alia_dict.items():
        if origin_ in li or origin_ == k:
            return k

    # 没找到，模糊匹配
    origin_ = origin.replace(" ", "")
    for k, li in alia_dict.items():
        li = [x.replace(" ", "") for x in ([k, *li])]
        for v in li:
            if origin_ in v:
                return k

    return origin


def parse_time_delta(t: datetime.timedelta):
    mm, ss = divmod(t.seconds, 60)
    hh, mm = divmod(mm, 60)
    dd = t.days or 0
    return dd, hh, mm, ss


def img_invert_rgba(im: Image.Image):
    # https://stackoverflow.com/questions/2498875/how-to-invert-colors-of-image-with-pil-python-imaging
    r, g, b, a = im.split()
    rgb_image = Image.merge("RGB", (r, g, b))
    inverted_image = ImageOps.invert(rgb_image)
    r2, g2, b2 = inverted_image.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def replace_brackets(original: str):
    return original.replace("（", "(").replace("）", "(")


def splice_msg(msgs: list) -> Message:
    im = Message()
    for i, v in enumerate(msgs):
        if isinstance(v, str) and (i != 0):
            v = f"\n{v}"
        im += v
    return im


def split_list(li: Iterable[_T], length: int) -> List[List[_T]]:
    latest = []
    tmp = []
    for n, i in enumerate(li):
        tmp.append(i)
        if (n + 1) % length == 0:
            latest.append(deepcopy(tmp))
            tmp.clear()
    if tmp:
        latest.append(deepcopy(tmp))
    return latest
