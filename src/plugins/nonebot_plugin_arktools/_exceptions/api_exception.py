"""API 相关异常"""
from . import ArkBaseException


class APINonExistenceException(ArkBaseException):
    """API不存在"""
    def __init__(self, msg: str = "该API不存在", **kwargs):
        super().__init__(msg, **kwargs)
        self.msg = msg


class APICodeException(ArkBaseException):
    """接口响应码异常"""
    def __init__(self, status: int = 200, msg: str = "接口响应码错误", **kwargs):
        super().__init__(msg, **kwargs)
        self.status = status

    def __repr__(self):
        return f"{self.status}: {self.msg}"
