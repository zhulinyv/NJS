"""异常基类"""
from typing import Union


class ArkBaseException(Exception):
    """基础异常类"""
    def __init__(self, msg: str = "出现了错误，但是未说明具体原因。", details: Union[str, int] = ""):
        super().__init__(msg)
        self.msg = f"{msg} - {details}"

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.msg
