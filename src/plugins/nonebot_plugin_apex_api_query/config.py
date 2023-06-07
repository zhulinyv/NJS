from pydantic import BaseModel, Extra
from typing import Optional

class Config(BaseModel, extra=Extra.ignore):
    apex_api_key: Optional[str] = None
    apex_api_url: str = 'https://api.mozambiquehe.re/'
    apex_api_t2i: bool = True
