from pathlib import Path
from typing import Any, Dict, Union

import httpx
from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseModel, Extra

try:
    import ujson as json
except ModuleNotFoundError:
    import json


class PluginConfig(BaseModel, extra=Extra.ignore):
    crazy_path: Path = Path(__file__).parent
    crazy_auto_update: bool = False


driver = get_driver()
crazy_config: PluginConfig = PluginConfig.parse_obj(driver.config.dict())


class DownloadError(Exception):
    pass


class ResourceError(Exception):
    pass


async def download_url() -> Union[Dict[str, Any], None]:
    url: str = "https://raw.fgit.ml/MinatoAquaCrews/nonebot_plugin_crazy_thursday/master/nonebot_plugin_crazy_thursday/post.json"

    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    continue

                return response.json()

            except Exception:
                logger.warning(
                    f"Error occured when downloading {url}, {i+1}/3")

    logger.warning("Abort downloading")
    return None


@driver.on_startup
async def kfc_post_check() -> None:
    '''
        Get the latest version of post.json from repo if CRAZY_AUTO_UPDATE.
        If failed and post dosen't exists, raise exception.
        Otherwise just abort it.
    '''
    json_path: Path = crazy_config.crazy_path / "post.json"

    cur_version: float = 0
    if json_path.exists():
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            cur_version = data.get("version", 0)

    if crazy_config.crazy_auto_update:
        response = await download_url()
    else:
        response = None

    if response is None:
        if not json_path.exists():
            logger.warning("Crazy Thursday resource missing! Please check!")
            raise ResourceError
    else:
        try:
            version: float = response.get("version", 0)
        except KeyError:
            logger.warning(
                "KFC post text resource downloaded incompletely! Please check!")
            raise DownloadError

        # Update when there is a newer version
        if version > cur_version:
            with json_path.open("w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=4)

            logger.info(
                f"Updated post.json, version: {cur_version} -> {version}")
