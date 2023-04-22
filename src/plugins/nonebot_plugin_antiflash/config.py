from nonebot.log import logger
from typing import List, Dict
import os
from pathlib import Path
from pydantic import BaseModel, Extra
import nonebot
try:
    import ujson as json
except ModuleNotFoundError:
    import json

class AntiFlashConfig(BaseModel, extra=Extra.ignore):
    
    anti_flash_on: bool = True
    anti_flash_group: List[str] = []
    anti_flash_path: str = os.path.dirname(__file__)

class AntiFlashHandler:
    
    def __init__(self, config):
        self.on: bool = config.anti_flash_on
        self.group_on: List[str] = list(set(config.anti_flash_group))
        self.path: Path = Path(config.anti_flash_path) / "config.json"
        
        if not self.on:
            logger.warning(f"已全局禁用群聊反闪照，指令：开启/禁用反闪照")
        else:
            if not self.path.exists():
                with open(self.path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(dict()))
                    f.close()
                    
            self.check_default_groups()
    
    def check_default_groups(self) -> None:
        '''
            初始化更新默认开启群组
        '''
        file = self.load_json(self.path)
        for gid in self.group_on:
            file.update({gid: True})
        
        self.save_json(self.path, file)
    
    def check_permission(self, gid: str) -> bool:
        '''
            检测群组是否已开启功能
        '''
        file = self.load_json(self.path)
        return False if gid not in file else file[gid]
    
    def add_group(self, gid: str) -> None:
        '''
            Update覆盖
        '''
        file = self.load_json(self.path)
        file.update({gid: True})
        self.save_json(self.path, file)
    
    def remove_group(self, gid: str) -> None:
        '''
            尝试Pop
        '''
        file = self.load_json(self.path)
        try:
            file.pop(gid)
        except KeyError:
            pass
        
        self.save_json(self.path, file)
        
    def save_json(self, file: Path, data: Dict[str, bool]) -> None:
        if file.exists():
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    def load_json(self, file: Path) -> Dict[str, bool]:
        if file.exists():
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)

config: AntiFlashConfig = AntiFlashConfig.parse_obj(nonebot.get_driver().config.dict())
handler = AntiFlashHandler(config)