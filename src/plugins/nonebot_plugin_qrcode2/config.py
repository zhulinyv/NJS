from nonebot.config import BaseConfig


class Config(BaseConfig):
    # 命令符
    qrcode_cmd: str = "#"
    # 命令关键字
    qrcode_keyword: set[str] = {"扫码"}
    # 响应优先级
    qrcode_priority: int = 10
    # bot昵称列表
    nickname: list[str] = ["qrcode2"]

