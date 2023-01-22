from typing import Optional

from pydantic import Extra, BaseModel

class Config(BaseModel, extra=Extra.ignore):
    start_time: Optional[int] = 0
    end_time: Optional[int] = 24