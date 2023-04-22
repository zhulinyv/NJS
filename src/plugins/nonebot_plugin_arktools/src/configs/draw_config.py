"""抽卡设置"""
from pydantic import BaseModel, Extra

class DrawConfig(BaseModel, extra=Extra.ignore):
    """干员概率"""
    draw_rate_6: float = 0.02
    draw_rate_5: float = 0.08
    draw_rate_4: float = 0.48
    draw_rate_3: float = 0.42


__all__ = [
    "DrawConfig"
]