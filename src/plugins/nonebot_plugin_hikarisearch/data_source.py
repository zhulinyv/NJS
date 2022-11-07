import httpx
from dataclasses import dataclass
from typing import List, Tuple, Protocol
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .config import hikari_config

API = hikari_config.hikarisearch_api.strip("/")


async def search_saucenao(image: bytes) -> List[Message]:
    data = {"hide": "true"}
    result = await post("/api/SauceNAO", data, image)
    return [
        MessageSegment.image(res["image"])
        + "{}\n图片相似度: {:.2f}%\n图片来源:\n{}".format(
            res["title"],
            res["similarity"],
            "\n".join(
                ["\n".join(dict(content).values()) for content in res["content"]]
            ),
        )
        for res in result
    ]


async def search_iqdb(image: bytes) -> List[Message]:
    data = {
        "services": '["danbooru","konachan","yandere","gelbooru","sankaku_channel","e_shuushuu","zerochan","anime_pictures"]',
        "discolor": "false",
    }
    result = await post("/api/IqDB", data, image)
    return [
        MessageSegment.image(res["image"])
        + "图片相似度: {:.0f}%\n图片来源:\n{}".format(res["similarity"], res["url"])
        for res in result
    ]


async def search_ascii2d(image: bytes) -> List[Message]:
    data = {"type": "color"}
    result = await post("/api/ascii2d", data, image)
    return [
        MessageSegment.image(res["image"])
        + "图片来源: {}\n{}\n图片作者: {}\n{}".format(
            res["source"]["text"],
            res["source"]["link"],
            res["author"]["text"],
            res["author"]["link"],
        )
        for res in result
    ]


async def search_ehentai(image: bytes) -> List[Message]:
    data = {"site": "eh", "cover": "false", "deleted": "false", "similar": "true"}
    result = await post("/api/E-Hentai", data, image)
    return [
        MessageSegment.image(res["image"])
        + "[{}] {}\n图片来源:\n{}".format(res["type"], res["title"], res["link"])
        for res in result
    ]


async def search_tracemoe(image: bytes) -> List[Message]:
    data = {"cutBorders": "true"}
    result = await post("/api/TraceMoe", data, image)
    return [
        MessageSegment.image(res["preview"])
        + "图片相似度:{:.2f}\n{}图片来源:\n{}\n英文名:{}\n罗马字名:{}".format(
            res["similarity"],
            res["file"],
            res["name"]["native"],
            res["name"]["english"],
            res["name"]["romaji"],
        )
        for res in result
    ]


async def post(url, data: dict, image: bytes) -> dict:
    files = {"image": image}
    async with httpx.AsyncClient() as client:
        resp = await client.post(API + url, data=data, files=files, timeout=20)
        return resp.json()


async def download_image(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=20)
        return resp.content


class Func(Protocol):
    async def __call__(self, image: bytes) -> List[Message]:
        ...


@dataclass
class Source:
    name: str
    keywords: Tuple[str, ...]
    func: Func

    def __post_init__(self):
        self.commands: Tuple[str] = tuple(
            sum(([keyword + "搜图", "搜图" + keyword] for keyword in self.keywords), [])
        )


sources = [
    Source("SauceNAO", ("saucenao", "SauceNAO", "sauce", "nao"), search_saucenao),
    Source("ascii2d", ("ascii2d", "ascii", "asc"), search_ascii2d),
    Source("IqDB", ("iqdb", "IqDB", "IQDB"), search_iqdb),
    Source("E-Hentai", ("ehentai", "E-Hentai", "e-hentai", "eh"), search_ehentai),
    Source("TraceMoe", ("tracemoe", "TraceMoe", "trace"), search_tracemoe),
]
