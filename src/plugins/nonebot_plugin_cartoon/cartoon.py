import base64
from io import BytesIO

import httpx
from httpx import NetworkError
from PIL import Image


async def cartonization(img_url: str) -> str:
    async with httpx.AsyncClient() as client:
        res = await client.get(img_url)
    if res.is_error:
        raise NetworkError("无法获取此图像")

    image = Image.open(BytesIO(res.content)).convert("RGB")
    if image.width * image.height >= 49_0000:
        image.thumbnail((700, 700))
    image.save(imageData := BytesIO(), format="jpeg")
    img_b64 = base64.b64encode(imageData.getvalue()).decode()

    url_push = "https://hylee-white-box-cartoonization.hf.space/api/predict/"
    data = {
        "fn_index": 0,
        "data": [f"data:image/jpeg;base64,{img_b64}"],
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url_push, json=data, timeout=60)

    if res.is_error:
        raise NetworkError(f"网络出错: {res.status_code}")

    data = res.json()

    img_data = data["data"][0].split(",")[1]

    return f"base64://{img_data}"
