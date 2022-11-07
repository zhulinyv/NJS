from pydantic import BaseModel, Extra
from typing import Union, Dict, List
from pathlib import Path
from nonebot import get_driver
from nonebot.log import logger
import httpx
import aiofiles

class RandomTkkConfig(BaseModel, extra=Extra.ignore):
    
    tkk_path: Path = Path(__file__).parent / "resource"
    easy_size: int = 10
    normal_size: int = 20
    hard_size: int = 40
    extreme_size: int = 60
    max_size: int = 80
    
driver = get_driver()
tkk_config: RandomTkkConfig = RandomTkkConfig.parse_obj(driver.config.dict())

characters: Dict[str, List[str]] = {
    "honoka": ["高坂穗乃果", "穗乃果", "果皇"],
    "eli": ["绚濑绘里", "绘理", "会长"],
    "umi": ["田园海未", "海未", "海爷"],
    "maki": ["西木野真姬", "真姬"],
    "rin": ["星空凛", "凛喵"],
    "hanayo": ["小泉花阳", "花阳"],
    "nico": ["矢泽妮可", "妮可"],
    "nozomi": ["东条希", "希"],
    "kotori": ["南小鸟", "南琴梨"],
    "you": ["渡边曜", "曜酱"],
    "dia": ["黑泽黛雅", "呆雅"],
    "riko": ["樱内梨子", "梨梨"],
    "yoshiko": ["津岛善子", "夜羽"],
    "ruby": ["黑泽露比", "露比"],
    "hanamaru": ["国木田花丸", "花丸", "小丸"],
    "mari": ["小原鞠莉"],
    "kanan": ["松浦果南", "果南"],
    "chika": ["高海千歌", "千歌"],
    "ren": ["叶月恋", "小恋"],
    "sumire": ["平安名堇", "平安民警", "民警"],
    "chisato": ["岚千砂都", "千酱", "小千"],
    "kanon": ["涩谷香音", "香音"],
    "tankuku": ["唐可可", "上海偶像"]
}

def find_charac(_name: str) -> Union[str, bool]:
    '''
        Find the character
    '''
    for charac in characters:
        # That _name is the characters dict key is also OK
        if _name == charac or _name in characters[charac]:
            return charac
    
    return False

def other_characs_list(_charac: str) -> List[str]:
    '''
        Get the random character list except character _charac
    '''
    pick: List[str] = []
    for charac in characters:
        if _charac != charac:
            pick.append(charac)
    
    return pick

class DownloadError(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg

async def download_url(url: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    continue
                return response
            except Exception:
                logger.warning(f"Error occured when downloading {url}, {i+1}/3")
    
    raise DownloadError("Resource of Random Tankuku plugin missing! Please check!")

@driver.on_startup
async def _():
    tkk_path: Path = tkk_config.tkk_path
    
    if not tkk_path.exists():
        tkk_path.mkdir(parents=True, exist_ok=True)
        
    url: str = "https://raw.fastgit.org/MinatoAquaCrews/nonebot_plugin_randomtkk/main/nonebot_plugin_randomtkk/resource/"
    
    for chara in characters:
        _name: str = chara + ".png"
        if not (tkk_path / _name).exists():
            response = await download_url(url + _name)
            await save_resource(_name, response)

    if not (tkk_path / "mark.png").exists():
        response = await download_url(url + "mark.png")
        await save_resource("mark.png", response)
        
    if not (tkk_path / "msyh.ttc").exists():
        response = await download_url(url + "msyh.ttc")
        await save_resource("msyh.ttc", response)

async def save_resource(name: str, response: httpx.Response) -> None:
    async with aiofiles.open((tkk_config.tkk_path / name), "wb") as f:
        await f.write(response.content)