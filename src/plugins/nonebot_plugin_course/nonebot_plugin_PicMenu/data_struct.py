from typing import List, Union

from pydantic import BaseModel


# 功能的数据信息
class FuncData(BaseModel):
    func: str
    trigger_method: str
    trigger_condition: str
    brief_des: str
    detail_des: str


# 插件菜单的数据信息
class PluginMenuData(BaseModel):
    name: str
    description: str
    usage: str
    funcs: Union[List[FuncData], None] = None
    template: str = "default"
