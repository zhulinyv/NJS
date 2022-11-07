import os
import json
from .._exceptions import *


def get_api(field: str):
    """
    获取 API。
    :param field: API 所属分类，即 _apis 下的文件名（不含后缀名）
    :return dict, 该 API 的内容。
    """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "_apis", f"{field.lower()}.json"))
    print(path)
    if os.path.exists(path):
        with open(path, encoding="utf8") as f:
            return json.loads(f.read())
    else:
        raise APINonExistenceException