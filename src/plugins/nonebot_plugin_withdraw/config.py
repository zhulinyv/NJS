from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    withdraw_max_size: int = 100
