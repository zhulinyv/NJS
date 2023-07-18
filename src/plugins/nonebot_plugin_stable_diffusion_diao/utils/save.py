from ..config import config
from pathlib import Path
import hashlib
import aiofiles
import time

path = Path("data/novelai/output").resolve()


async def save_img(fifo, img_bytes: bytes, extra: str = "unknown", hash=time.time()):
    # 存储图片
    if config.novelai_save:
        path_ = path / extra
        path_.mkdir(parents=True, exist_ok=True)
        hash = hashlib.md5(img_bytes).hexdigest()
        file = (path_ / hash).resolve()
        async with aiofiles.open(str(file) + ".jpg", "wb") as f:
            await f.write(img_bytes)
        if config.novelai_save == 2:
            async with aiofiles.open(str(file) + ".txt", "w", encoding="utf-8") as f:
                await f.write(repr(fifo))
