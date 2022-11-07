from typing import Tuple, List, Dict, Union, Optional
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, MessageSegment
import random
import asyncio
from .config import tkk_config, find_charac, other_characs_list

class RandomTkkHandler:
    
    def __init__(self):
        self.tkk_config = tkk_config
        self.timers: Dict[str, asyncio.TimerHandle] = dict()
        self.tkk_status: Dict[str, Union[str, bool, List[int], bytes]] = dict()
        
    def _config_tkk_size(self, level: str) -> int:
        '''
            size of tkk picture
        '''
        if level == "简单":
            return self.tkk_config.easy_size
        elif level == "普通":
            return self.tkk_config.normal_size
        elif level == "困难":
            return self.tkk_config.hard_size
        elif level == "地狱":
            return self.tkk_config.extreme_size
        else:
            try:
                tkk_size = int(level) if int(level) <= self.tkk_config.max_size else self.tkk_config.normal_size
                if tkk_size < self.tkk_config.easy_size:
                    tkk_size = self.tkk_config.easy_size
                return tkk_size
            except ValueError:
                return self.tkk_config.easy_size
    
    def _get_tkk_position(self, tkk_size: int) -> Tuple[int, int]:
        '''
            生成唐可可坐标
        '''
        col = random.randint(1, tkk_size)   # 列
        row = random.randint(1, tkk_size)   # 行
        return row, col
    
    def _get_waiting_time(self, tkk_size: int) -> int:
        '''
            计算等待时间
        '''
        if tkk_size >= 30:
            time = int(0.1 * (tkk_size - 30)**2 + 50)
        else:
            time = int(1.7 * (tkk_size - 10) + 15)
        
        return time
    
    def check_tkk_playing(self, uuid: str) -> bool:
        '''
            作为Rule: 群聊/私聊是否进行游戏
        '''
        return False if not self.tkk_status.get(uuid, False) else self.tkk_status[uuid]["playing"]

    def check_starter(self, gid: Optional[str], uid: str) -> bool:
        '''
            作为Rule: 是否为发起者提前结束游戏
        '''
        try:
            if gid is None:
                return self.tkk_status[uid]["playing"] and self.tkk_status[uid]["starter"] == uid
            else:
                return self.tkk_status[gid]["playing"] and self.tkk_status[gid]["starter"] == uid
        except KeyError:
            return False
    
    def _draw_tkk(self, row: int, col: int, tkk_size: int, _find_charac: str) -> Tuple[bytes, bytes]:
        '''
            画图
        '''
        temp: int = 0
        font: ImageFont.FreeTypeFont = ImageFont.truetype(str(tkk_config.tkk_path / "msyh.ttc"), 16)
        base: Image.Image = Image.new("RGB",(64 * tkk_size, 64 * tkk_size))
        _charac: str = find_charac(_find_charac)  # type: ignore
        pick_list: List[str] = other_characs_list(_charac)
        
        for r in range(0, tkk_size):
            for c in range(0, tkk_size):
                if r == row - 1 and c == col - 1:
                    charac = Image.open(tkk_config.tkk_path / (_charac + ".png"))
                    charac = charac.resize((64, 64), Image.ANTIALIAS) # 加载icon
                    draw = ImageDraw.Draw(charac)
                    draw.text((20, 40), f"({c+1},{r+1})", font=font, fill=(255, 0, 0, 0))
                    base.paste(charac, (r * 64, c * 64))
                    temp += 1
                else:
                    icon = Image.open(tkk_config.tkk_path / (random.choice(pick_list) + '.png'))
                    icon = icon.resize((64,64), Image.ANTIALIAS)
                    draw = ImageDraw.Draw(icon)
                    draw.text((20, 40), f"({c+1},{r+1})", font=font, fill=(255, 0, 0, 0))
                    base.paste(icon, (r * 64, c * 64))
        
        buf = BytesIO()
        base.save(buf, format='png')
        
        base2: Image.Image = base.copy()
        mark = Image.open(tkk_config.tkk_path / "mark.png")

        base2.paste(mark,((row - 1) * 64, (col - 1) * 64), mark)
        buf2 = BytesIO()
        base2.save(buf2, format='png')
        
        return buf.getvalue(), buf2.getvalue()
    
    def check_surrender_charac(self, uuid: str, _charac: str) -> bool:
        return _charac == self.tkk_status[uuid]["character"]
    
    def check_answer(self, uuid: str, pos: List[int]) -> bool: 
        return pos == self.tkk_status[uuid]["answer"]
    
    async def surrender(self, matcher: Matcher, uuid: str) -> None:
        '''
            发起者主动提前结束游戏：取消定时器，结算游戏
        '''
        try:
            timer = self.timers.get(uuid, None)
            if timer:
                timer.cancel()
        except Exception:
            return
        
        await self._timeout_close_game(matcher, uuid)
    
    async def _timeout_close_game(self, matcher: Matcher, uuid: str) -> None:
        '''
            超时无正确答案，结算游戏: 移除定时器、公布答案
        '''
        try:
            self.timers.pop(uuid, None)
        except KeyError:
            await matcher.finish("提前结束游戏出错……")
        
        answer: List[int] = self.tkk_status[uuid]["answer"]
        msg: Message = MessageSegment.text("没人找出来，好可惜啊☹\n") + MessageSegment.text(f"答案是{answer[0]}行{answer[1]}列") + MessageSegment.image(self.tkk_status[uuid]["mark_img"])
             
        if not self.tkk_status.pop(uuid, False):
            await matcher.finish("提前结束游戏出错……")
        
        await matcher.finish(msg)

    def _start_timer(self, matcher: Matcher, uuid: str, timeout: int) -> None:
        '''
            开启超时定时器，回调函数：_timeout_close_game
        '''
        timer = self.timers.get(uuid, None)
        if timer:
            timer.cancel()
        
        loop = asyncio.get_running_loop()
        timer = loop.call_later(
            timeout, lambda: asyncio.ensure_future(self._timeout_close_game(matcher, uuid))
        )
        self.timers.update({uuid: timer})
        
    def bingo_close_game(self, uuid: str) -> bool:
        '''
            等待时间内答对后结束游戏：取消定时器，移除定时器，移除记录
        '''
        try:
            timer = self.timers.get(uuid, None)
            if timer:
                timer.cancel()
            self.timers.pop(uuid, None)
            self.tkk_status.pop(uuid, False)
        except KeyError:
            return False
        
        return True
    
    def one_go(self, matcher: Matcher, uuid: str, uid: str, level: str, find_charac: str) -> Tuple[bytes, int]:
        '''
            记录每个群组如下属性：
                "playing": False,       bool        当前是否在进行游戏
                "starter": Username,    str         发起此次游戏者，仅此人可提前结束游戏
                "character": Charac,    str         寻找的角色
                "anwser": [0, 0],       List[int]   答案
                "mark_img": bytes       bytes       框出角色的图片
        '''
        tkk_size = self._config_tkk_size(level)
        row, col = self._get_tkk_position(tkk_size)
        waiting = self._get_waiting_time(tkk_size)
        img_file, mark_file = self._draw_tkk(row, col, tkk_size, find_charac)
        
        self.tkk_status.update({
            uuid: {
                "playing": True,
                "starter": uid,
                "character": find_charac,
                "answer": [col, row],
                "mark_img": mark_file
            }
        })
        
        # Start countdown
        self._start_timer(matcher, uuid, waiting)
        
        return img_file, waiting

random_tkk_handler = RandomTkkHandler()