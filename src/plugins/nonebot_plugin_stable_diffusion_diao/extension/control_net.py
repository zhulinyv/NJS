from PIL import Image
from io import BytesIO
import io
import base64
import aiohttp
from ..config import config

max_res = 800


async def control_net_func(pic: bytes, sd_url, tag):
    new_img = Image.open(io.BytesIO(pic)).convert("RGB")
    old_res = new_img.width * new_img.height
    width = new_img.width
    height = new_img.height

    if old_res > pow(max_res, 2):
        if width <= height:
            ratio = height/width
            width: float = max_res/pow(ratio, 0.5)
            height: float = width*ratio
        else:
            ratio = width/height
            height: float = max_res/pow(ratio, 0.5)
            width: float = height*ratio

        new_img.resize((round(width), round(height)))
    img_bytes =  BytesIO()
    new_img.save(img_bytes, format="JPEG")
    img_bytes = img_bytes.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

# "data:image/jpeg;base64," + 

    payload = {
  "prompt": tag,
  "negative_prompt": "秋柔嫣姬",
  "controlnet_input_image": [img_base64],
  "controlnet_module": "canny",
  "controlnet_model": "control_canny [9d312881]",
  "controlnet_weight": 0.8,
  "controlnet_resize_mode": "Scale to Fit (Inner Fit)",
  "controlnet_lowvram": "false",
  "controlnet_processor_res": 768,
  "controlnet_threshold_a": 100,
  "controlnet_threshold_b": 250,
  "sampler_index": "DDIM",
  "steps": 15,
  "cfg_scale": 7,
  "width": round(width),
  "height":round(height),
  "restore_faces": "false",
  "override_settings_restore_afterwards": "true"
}


    async with aiohttp.ClientSession() as session:
        async with session.post(url=sd_url + "/controlnet/txt2img", json=payload) as resp:
            print(resp.status)
            resp_all = await resp.json()
            resp_img = resp_all["images"][0]
            
            return base64.b64decode(resp_img), resp_img



            
