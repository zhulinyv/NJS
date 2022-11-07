import json
import os
from pathlib import Path
from typing import Optional

SEARCH_DIR = Path(".") / "data" / "database" / "search"


class Config:
    def __init__(self, group_id: int):
        self.__gid = group_id
        self.__engines: dict = self.__get_config(glob=False)
        self.__engines_global: dict = self.__get_config(glob=True)

    def add_engine(self, prefix: str, url: str, glob: bool = False) -> bool:
        if glob:
            self.__engines_global[prefix] = url
        else:
            self.__engines[prefix] = url

        return self._save_data(glob=glob)

    def del_engine(self, prefix: str, glob: bool = False) -> bool:
        return self.__engines_global.pop(prefix, False) and self._save_data(glob=True) if glob \
            else self.__engines.pop(prefix, False) and self._save_data()

    def __get_config(self, glob: bool = False) -> dict:
        file_name = f'{self.__gid}.json' if not glob else 'global.json'
        path = SEARCH_DIR / file_name

        os.makedirs(SEARCH_DIR, exist_ok=True)
        if not path.is_file():
            with open(path, "w", encoding="utf-8") as w:
                w.write(json.dumps({}))
        data = json.loads(path.read_bytes())

        return data

    def _save_data(self, glob: bool = False) -> bool:
        file_name = 'global.json' if glob else f'{self.__gid}.json'
        data: dict = self.__engines_global if glob else self.__engines

        path = SEARCH_DIR / file_name
        with open(path, "w", encoding="utf-8") as w:
            w.write(json.dumps(data, indent=4))
        return True

    def get_url(self, prefix: str) -> Optional[str]:
        if not self.__engines.get(prefix, None):
            return self.__engines_global.get(prefix, None)
        else:
            return self.__engines[prefix]

    def list_data(self, glob: bool = False) -> str:
        count: int = 0
        temp_list = ""

        if not glob:
            for prefix in self.__engines:
                count += 1
                temp_list += f"{count}.前缀：{prefix}\n" \
                             f"链接：{self.__engines.get(prefix, '')}\n"
        else:
            for prefix in self.__engines_global:
                count += 1
                temp_list += f"{count}.前缀：{prefix}\n" \
                             f"链接：{self.__engines_global.get(prefix, '')}\n"

        return temp_list

    @property
    def prefixes(self) -> set:
        prefixes = set(self.__engines.keys()).union(set(self.__engines_global.keys()))
        return prefixes
