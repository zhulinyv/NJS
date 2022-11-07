from typing import Optional
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """
    合并转发消息记录的超时时间, 单位为天
    """

    reminder_expire_time: Optional[float] = None
