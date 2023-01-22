import os
from pathlib import Path
from math import sin, cos, pi

from httpx import AsyncClient

from PIL import Image, ImageDraw, ImageFont

font_path = Path(os.path.join(os.path.dirname(__file__), "src", "SIMYOU.TTF"))


# Tip: ra_sin(30) = ra_cos(60) = 0.5
def ra_sin(angle):
    return round(sin(angle * pi/180), 2)


def ra_cos(angle):
    return round(cos(angle * pi/180), 2)


def rotate_line(center, p0, angle):
    ctx, cty = center
    x0, y0 = p0
    x1 = ctx + (x0 - ctx) * ra_cos(angle) + (y0 - cty) * ra_sin(angle)
    y1 = cty - (x0 - ctx) * ra_sin(angle) + (y0 - cty) * ra_cos(angle)
    return x1, y1


class FaceRecognition:
    def __init__(self, img_b64_str: str, ak: str, sk: str):
        self.API_KEY = ak
        self.SECRET_KEY = sk
        self.img_b64_str = img_b64_str
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                                      "Chrome/54.0.2840.99 Safari/537.36"
                        }

    async def get_access_token(self) -> str:
        host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials' \
               f'&client_id={self.API_KEY}' \
               f'&client_secret={self.SECRET_KEY}'
        async with AsyncClient() as client:
            resp = await client.get(host, headers=self.headers)
        access_token = resp.json()['access_token']
        return access_token

    async def face_beauty(self) -> dict:
        api_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        data = {
            "image": self.img_b64_str,
            "image_type": "BASE64",
            "face_field": "gender,beauty",
            "max_face_num": 120
        }
        access_token = await self.get_access_token()
        request_url = f"{api_url}?access_token={access_token}"
        async with AsyncClient() as client:
            resp = await client.post(request_url, data=data, headers=self.headers)
        result = resp.json()
        return result

    @staticmethod
    async def draw_face_rects(img_ori, buf, faces_pos) -> None:
        img = Image.open(img_ori)
        img_draw = ImageDraw.Draw(img)

        index = 1
        for face in faces_pos:
            left = face['left']
            top = face['top']
            width = face['width']
            height = face['height']
            angle = -face['rotation']
            font = ImageFont.truetype(str(font_path), int(width / 3))

            upper_left = left, top
            upper_right = rotate_line(upper_left, (left + width, top), angle)
            lower_left = rotate_line(upper_left, (left, top + height), angle)
            lower_right = rotate_line(upper_left, (left + width, top + height), angle)

            img_draw.polygon([upper_left, lower_left, lower_right, upper_right], outline=(0, 0, 255))
            img_draw.text(upper_left, str(index), fill=(0, 0, 255), font=font)

            index += 1

        img.save(buf, format="png")
