import json
from pathlib import Path

import httpx
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import NoticeEvent

upload = on_notice(priority=1)


@upload.handle()
async def _(event: NoticeEvent):
    try:
        arg = event.dict()
        files: dict = arg["file"]
        name: str = files["name"]
        if arg["notice_type"] == "offline_file" and name.endswith(".json"):
            try:
                jsons = json.loads(httpx.get(files["url"]).content.decode("utf-8"))
            except json.decoder:
                await upload.finish("求生json格式不正确")
            if not validate_json(jsons):
                await upload.finish("求生json格式不正确")
            key = await up_date(jsons, name)
            if key:
                msg = "输入成功\n"
                for key, value in jsons.items():
                    msg += f"当前你的{key}指令：{len(value)}个\n"
                await upload.send(msg)
    except KeyError:
        pass


async def validate_json(json_data):
    try:
        data = json.loads(json_data)
        if not isinstance(data, dict):
            return False

        for key, value in data.items():
            if not isinstance(value, list):
                return False
            for item in value:
                if not isinstance(item, dict):
                    return False
                if not all(key in item for key in ["id", "version", "ip"]):
                    return False

        return True

    except json.JSONDecodeError:
        return False


async def up_date(data, name):
    directory = Path("data/L4D2/l4d2")
    directory.mkdir(parents=True, exist_ok=True)

    file_path = directory / name
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, ensure_ascii=False)

    return True
