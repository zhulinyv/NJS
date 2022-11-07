import base64
import time
from io import BytesIO
from typing import List, TypedDict

import httpx
from httpx import NetworkError
from PIL import Image


class Confidence(TypedDict):
    label: str
    confidence: float


async def savor_image(img_url: str) -> List[Confidence]:
    async with httpx.AsyncClient() as client:
        res = await client.get(img_url)
    if res.is_error:
        raise NetworkError("无法获取此图像")

    image = Image.open(BytesIO(res.content)).convert("RGB")
    image.save(imageData := BytesIO(), format="jpeg")
    img_b64 = base64.b64encode(imageData.getvalue()).decode()

    url_push = "https://hysts-deepdanbooru.hf.space/api/predict"
    data = {
        "fn_index": 0,
        "data": [f"data:image/jpeg;base64,{img_b64}", 0.5],
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url_push, json=data, timeout=10)

    if res.is_error:
        raise NetworkError(f"网络出错: {res.status_code}")

    data = res.json()

    return data["data"][0]["confidences"]
