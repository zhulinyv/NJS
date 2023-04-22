from pathlib import Path
from typing import Any, Dict, List, Set, Union

import httpx
import nonebot
from aiocache import cached
from nonebot import logger
from pydantic import BaseModel, Extra

try:
    import ujson as json
except ModuleNotFoundError:
    import json


class PluginConfig(BaseModel, extra=Extra.ignore):
    '''
        Path of tarot images resource
    '''
    tarot_path: Path = Path(__file__).parent / "resource"
    chain_reply: bool = True
    tarot_auto_update: bool = False
    nickname: Set[str] = {"Bot"}

    '''
        DO NOT CHANGE THIS VALUE IN ANY .ENV FILES
    '''
    tarot_official_themes: List[str] = ["BilibiliTarot", "TouhouTarot"]


driver = nonebot.get_driver()
tarot_config: PluginConfig = PluginConfig.parse_obj(
    driver.config.dict(exclude_unset=True))


class DownloadError(Exception):
    pass


class ResourceError(Exception):

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg

    __repr__ = __str__


class EventNotSupport(Exception):
    pass


async def download_url(name: str, is_json: bool = False) -> Union[Dict[str, Any], bytes, None]:
    url: str = "https://raw.fgit.ml/MinatoAquaCrews/nonebot_plugin_tarot/master/nonebot_plugin_tarot/" + name

    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                response: httpx.Response = await client.get(url)
                if response.status_code != 200:
                    continue

                return response.json() if is_json else response.content

            except Exception:
                logger.warning(
                    f"Error occurred when downloading {url}, {i+1}/3")

    logger.warning("Abort downloading")
    return None


@driver.on_startup
async def tarot_version_check() -> None:
    '''
        Get the latest version of tarot.json from repo
    '''
    if not tarot_config.tarot_path.exists():
        tarot_config.tarot_path.mkdir(parents=True, exist_ok=True)

    tarot_json_path: Path = Path(__file__).parent / "tarot.json"

    cur_version: float = 0
    if tarot_json_path.exists():
        with tarot_json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            cur_version = data.get("version", 0)

    # Auto update check on startup if TAROT_AUTO_UPDATE
    if tarot_config.tarot_auto_update:
        response: Dict[str, Any] = await download_url("tarot.json", is_json=True)
    else:
        response = None

    if response is None:
        if not tarot_json_path.exists():
            logger.warning("Tarot text resource missing! Please check!")
            raise ResourceError("Missing necessary resource: tarot.json!")
    else:
        try:
            version: float = response.get("version", 0)
        except KeyError:
            logger.warning(
                "Tarot text resource downloaded incompletely! Please check!")
            raise DownloadError

        # Update when there is a newer version
        if version > cur_version:
            with tarot_json_path.open("w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=4)
                logger.info(
                    f"Updated tarot.json, version: {cur_version} -> {version}")


@cached(ttl=180)
async def get_tarot(_theme: str, _type: str, _name: str) -> Union[bytes, None]:
    '''
        Downloads tarot image and stores cache temporarily
        if downloading failed, return None
    '''
    logger.info(
        f"Downloading tarot image {_theme}/{_type}/{_name} from repo")

    resource: str = "resource/" + f"{_theme}/{_type}/{_name}"
    data = await download_url(resource)

    if data is None:
        logger.warning(
            f"Downloading tarot image {_theme}/{_type}/{_name} failed!")

    return data
