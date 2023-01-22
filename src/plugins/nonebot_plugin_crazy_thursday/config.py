from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseModel, Extra
from pathlib import Path
from typing import Union, Dict, List
import httpx
try:
    import ujson as json
except ModuleNotFoundError:
    import json

class PluginConfig(BaseModel, extra=Extra.ignore):
    crazy_path: Path = Path(__file__).parent

driver = get_driver()
crazy_config: PluginConfig = PluginConfig.parse_obj(driver.config.dict())

class DownloadError(Exception):
    pass

class ResourceError(Exception):
    pass

async def download_url(url: str) -> Union[httpx.Response, None]:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    continue
                return response
            except Exception as e:
                logger.warning(f"Error occured when downloading {url}, {i+1}/3: {e}")
    
    logger.warning(f"Abort downloading")
    return None

@driver.on_startup
async def post_check() -> None:
    '''
        Get the latest version of post.json from repo
        If failed and post dosen't exists, raise exception
        Otherwise just abort downloading
    '''
    json_path: Path = crazy_config.crazy_path / "post.json"
            
    url = "https://raw.fastgit.org/MinatoAquaCrews/nonebot_plugin_crazy_thursday/beta/nonebot_plugin_crazy_thursday/post.json"
    response = await download_url(url)
    if response is None:
        if not json_path.exists():
           logger.warning("Crazy Thursday resource missing! Please check!")
           raise ResourceError
    else:
        docs: Dict[str, Union[float, List[str]]] = response.json()
        version = docs.get("version")

        with json_path.open("w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=4)
            logger.info(f"Get the latest Crazy Thursday posts from repo, version: {version}")