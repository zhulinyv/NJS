"""网络请求相关异常"""
from . import ArkBaseException


class NoMethodException(ArkBaseException):
    """请求方式不是 GET 或 POST"""
    def __init__(self, msg: str = "请求方式只能为 GET 或 POST ", **kwargs):
        super().__init__(msg, **kwargs)
        self.msg = msg
