import os
import time
import json
from ..config import config
import aiofiles


async def count(user: str, num):

    filename = "data/novelai/day_limit_data.json"

    async def save_data(data):
        async with aiofiles.open(filename, "w") as file:
            await file.write(json.dumps(data))

    day: int = time.localtime(time.time()).tm_yday
    json_data = {"date": day, "count": {}}

    if os.path.exists(filename):
        async with aiofiles.open(filename, "r") as file:
            content = await file.read()
            json_data: dict = json.loads(content)
        try:
            json_data["date"]
        except KeyError:
            json_data = {"date": day, "count": {}}
        if json_data["date"] != day:
            json_data = {"date": day, "count": {}}

    data = json_data["count"]
    count: int = data.get(user, 0) + num
    if count > config.novelai_daylimit:
        return -1
    else:
        data[user] = count
        json_data["count"] = data
        await save_data(json_data)
        return config.novelai_daylimit-count
