from typing import Optional

from pydantic import Extra, BaseModel


class Config(BaseModel, extra=Extra.ignore):
    qweather_apikey: Optional[str] = None
    qweather_apitype: Optional[str] = None
    debug: bool = False
