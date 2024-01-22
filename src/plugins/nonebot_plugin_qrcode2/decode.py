import os
from PIL import Image
from cv2 import wechat_qrcode_WeChatQRCode
from numpy import array as nparray
from pyzbar import pyzbar

from .exception import QRDecodeError


# (解码内容, box(left, upper, right, lower))
QRDecoded = tuple[str, tuple]

wechat_args = ['detect.prototxt','detect.caffemodel','sr.prototxt','sr.caffemodel']
wechat_model_path = os.path.join(os.path.dirname(__file__), "resource/wechat_model")
wechat_args = [os.path.join(wechat_model_path, f) for f in wechat_args]


def wechat_decode(img: Image.Image) -> list[QRDecoded] | None:
    img_nparray = nparray(img)
    detector = wechat_qrcode_WeChatQRCode(*wechat_args)
    datas, points = detector.detectAndDecode(img_nparray)
    if not datas:
        return None
    boxs = []
    for item in points:
        xs = [p[0] for p in item]
        ys = [p[1] for p in item]
        box = (min(xs), min(ys), max(xs), max(ys))
        boxs.append(box)
    return list(zip(datas, boxs))


def pyzbar_decode(img: Image.Image) -> list[QRDecoded] | None:
    decoded_list: list[pyzbar.Decoded] = None
    try:
        decoded_list = pyzbar.decode(img, symbols=[pyzbar.ZBarSymbol.QRCODE])
    except Exception as e:
        return None
    if not decoded_list:
        return None
    result = []
    for item in decoded_list:
        rect: pyzbar.Rect = item.rect
        box = (rect.left, rect.top, rect.left + rect.width, rect.top + rect.height)
        result.append((str(item.data.decode("utf-8")), box))
    return result

def all_decode(img: Image) -> tuple[list[QRDecoded], str]:
    """
    return: (decoded_list, decode_name)
    raise: QRDecodeError
    """
    decode_funcs = (wechat_decode, pyzbar_decode)
    for decode in decode_funcs:
        decoded_list = decode(img)
        if decoded_list:
            return (decoded_list, decode.__name__)
    raise QRDecodeError