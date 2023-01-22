from nonebot.adapters.onebot.v11 import MessageSegment
import random
from pathlib import Path 
from typing import List, Dict, Union, Tuple
from PIL import Image
from io import BytesIO
from .config import tarot_config, get_tarot
try:
    import ujson as json
except ModuleNotFoundError:
    import json

class Tarot:
    def __init__(self):
        self._init_json_ok: bool = False
        self._formations: Dict[str, Dict[str, Union[int, bool, List[List[str]]]]] = {}
        self._cards: Dict[str, Dict[str, Union[str, Dict[str, str]]]] = {}
        self.cards_num: int = 0
        self.is_chain_reply: bool = tarot_config.chain_reply
        self.devined: List[str] = []
        self.is_cut: bool = False
        self.represent: List[str] = []
    
    def init_json(self):
        tarot_json: Path = tarot_config.tarot_path / "tarot.json"
        with open(tarot_json, 'r', encoding='utf-8') as f:
            content = json.load(f)
            self._formations = content.get("formation")
            self._cards = content.get("cards")
        
        self._init_json_ok = True
        
    async def divine(self) -> Tuple[MessageSegment, int]:
        '''
            Get one formation of all formations
        '''
        if not self._init_json_ok:
            self.init_json()
            
        formation_name = random.choice(list(self._formations))
        formation = self._formations.get(formation_name)
        self.cards_num = formation.get("cards_num")
        self.devined = random.sample(list(self._cards), self.cards_num)
        self.is_cut = formation.get("is_cut")
        self.represent = random.choice(formation.get("represent"))
        
        return MessageSegment.text(f"启用{formation_name}，正在洗牌中"), self.cards_num

    async def reveal(self, index: int) -> MessageSegment:
        '''
            index: 0 to cards_num-1
        '''
        if self.is_cut and index == self.cards_num - 1:
            msg_header = MessageSegment.text(f"切牌「{self.represent[index]}」\n")
        else:
            msg_header = MessageSegment.text(f"第{index+1}张牌「{self.represent[index]}」\n")
        
        msg_body: MessageSegment = await self.multi_divine(index)
        
        return msg_header + msg_body
        
    async def multi_divine(self, index: int) -> MessageSegment:
        '''
            Multi divines, arrcording to index get the meaning and image(up or down)
        '''
        card: Dict[str, Dict[str, Union[str, Dict[str, str]]]] = self._cards.get(self.devined[index])
        name_cn: str = card.get("name_cn")
        img_path: Path = tarot_config.tarot_path / card.get("type") / card.get("pic")
        if not img_path.exists():
            data = await get_tarot(card.get("type"), card.get("pic"))
            if data is None:
                return MessageSegment.text(f"图片下载出错，请重试……")
            
            img = Image.open(BytesIO(data))
        else:
            img = Image.open(img_path)
        
        if random.random() < 0.5:
            # 正位
            meaning = card.get("meaning").get("up")
            msg = MessageSegment.text(f"「{name_cn}正位」「{meaning}」\n")  
        else:
            meaning = card.get("meaning").get("down")
            msg = MessageSegment.text(f"「{name_cn}逆位」「{meaning}」\n")
            img = img.rotate(180)
        
        buf = BytesIO()
        img.save(buf, format='png')
        
        return msg + MessageSegment.image(buf)
    
    async def single_divine(self) -> MessageSegment:
        '''
            Single divine, get a tarot
        '''
        if not self._init_json_ok:
            self.init_json()
              
        self.devined = [random.choice(list(self._cards))]
        
        msg = MessageSegment.text("回应是")
        body: MessageSegment = await self.multi_divine(0)
        
        return msg + body
    
    def switch_chain_reply(self, new_state: bool) -> None:
        '''
            开启/关闭群聊转发模式
        '''
        self.is_chain_reply = new_state

tarot_manager = Tarot()