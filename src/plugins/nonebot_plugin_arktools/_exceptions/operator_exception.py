from ._base_exception import *


class OperatorNotExistException(ArkBaseException):
    """干员不存在"""
    def __init__(self, msg: str = "该干员不存在", **kwargs):
        super().__init__(msg, **kwargs)
        self.msg = msg
