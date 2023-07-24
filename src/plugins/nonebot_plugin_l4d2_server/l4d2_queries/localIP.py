try:
    import ujson as json
except:
    import json
from pathlib import Path
from typing import Dict, List
import os

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
filename = "data/L4D2/l4d2.json"
global_file = Path(Path(__file__).parent.parent, filename)


def load_ip_json():
    # 本地模块
    LOCAL_HOST: Dict[str, List[Dict[str, str]]] = {}
    try:
        # 获取所有json文件的路径
        json_files = Path("data/L4D2/l4d2").glob("*.json")

        # 将所有json文件中的字典对象合并为一个字典
        for file_path in json_files:
            with open(file_path, "r", encoding="utf-8") as f:
                LOCAL_HOST.update(json.load(f))
    except:
        pass
    return LOCAL_HOST


def load_group_json():
    try:
        GROUP_HOST: Dict[str, List[str]] = json.load(
            open(filename, "r", encoding="utf8")
        )
    except IOError or FileNotFoundError:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        data: Dict[str, List[str]] = {"anne": ["云"]}
        with open(filename, "w") as f:
            json.dump(data, f)
        GROUP_HOST: Dict[str, List[str]] = {}
    return GROUP_HOST


ALL_HOST: Dict[str, List[Dict[str, str]]] = load_ip_json()
Group_All_HOST: Dict[str, List[str]] = load_group_json()
