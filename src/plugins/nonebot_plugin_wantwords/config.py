from pydantic import BaseModel, Extra

class Config(BaseModel, extra=Extra.ignore):
    wantwords_max_results: int = 10 # 最大输出结果数，1～100整数
