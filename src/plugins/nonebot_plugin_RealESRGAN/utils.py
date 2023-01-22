from json import loads
from base64 import b64encode, b64decode
import aiohttp

######### 实现对图片的base64编码和从返回数据中解析出原始图片 #########


def img_encode_to_json(img: bytes, mode="base") -> dict:
    '''
    对二进制格式的图片进行base64编码，并组织成json格式返回，用于request请求

    Args:
        img (bytes): 二进制格式图片

    Returns:
        dict: 返回的json数据
    '''
    base64_data = b64encode(img)
    base64_data = str(base64_data, 'utf-8')
    return {
        'fn_index': 0,
        'data': [
            'data:image/jpeg;base64,{}'.format(base64_data),
            f'{mode}',
        ]
    }


def img_decode_from_json(response_str: str) -> bytes:
    '''
    将返回的json解析出img的base64再解码返回

    Args:
        response_str (str): 字符串格式的json

    Returns:
        bytes: img的二进制格式
    '''
    result = loads(response_str)
    img_base64 = result['data'][0].split("base64,")[1]
    return b64decode(img_base64)


######### 网络请求部分 #########

async def get_img(img_url: str) -> bytes:
    '''
    将收到的图片下载下来，并转换成二进制格式

    Args:
        img_url (str): 图片url地址

    Returns:
        bytes: 二进制格式的图片
    '''
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as resp:
            result = await resp.content.read()
    if not result:
        return None
    return result


async def get_result(json_data: dict, *, api) -> str:
    '''
    来构造请求并获取返回的重建后的图像

    Args:
        json_data (dict): 对图片编码后的数据

    Returns:
        str: 返回的json格式数据
    '''
    headers = {
        'authority': 'hf.space',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        # Already added when you pass json=
        # 'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://hf.space',
        'pragma': 'no-cache',
        'referer': 'https://hf.space/embed/ppxxxg22/Real-ESRGAN/+?__theme=light',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api, headers=headers, json=json_data, timeout=120) as resp:
                result = await resp.text()
        if not result:
            return None
        return result
    except:
        return None
