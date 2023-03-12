import os
from pathlib import Path

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .api.MirlKoi import MirlKoi,is_MirlKoi_tag
from .api.Anosu import Anosu
from .api.Lolicon import Lolicon

path = Path() / "data" / "setu"
file = path / "customer_api.json"
if file.exists():
    with open(file, "r", encoding="utf8") as f:
        customer_api = json.load(f)
else:
    customer_api = {}
    if not path.exists():
        os.makedirs(path)

def save():
    with open(file, "w", encoding="utf8") as f:
        json.dump(customer_api, f, ensure_ascii=False, indent=4)