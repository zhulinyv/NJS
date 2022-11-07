import datetime

from PIL import Image, ImageOps

from .const import STU_ALIAS, SUFFIX_ALIAS


def format_timestamp(t):
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def recover_alia(origin: str, alia_dict: dict[str, list[str]]):
    origin = origin.lower().strip()

    # 精确匹配
    for k, li in alia_dict.items():
        if origin in li or origin == k:
            return k

    # 匹配括号别名
    for k, li in alia_dict.items():
        if (p := k.find("（")) != -1:
            prefixes = [k[:p]] + li
            suffixes = [k[p + 1 : -1]]

            if a := SUFFIX_ALIAS.get(suffixes[0]):
                suffixes.extend(a)

            for s in suffixes:
                for p in prefixes:
                    if f"{p}{s}" == origin or f"{s}{p}" == origin:
                        return k

    # 没找到，模糊匹配
    for k, li in alia_dict.items():
        li = [k] + li
        for v in li:
            if (v in origin) or (origin in v):
                return k

    return origin


def recover_stu_alia(a):
    return recover_alia(a, STU_ALIAS)


def parse_time_delta(t: datetime.timedelta):
    mm, ss = divmod(t.seconds, 60)
    hh, mm = divmod(mm, 60)
    dd = t.days or 0
    return dd, hh, mm, ss


def img_invert_rgba(im: Image.Image):
    # https://stackoverflow.com/questions/2498875/how-to-invert-colors-of-image-with-pil-python-imaging
    r, g, b, a = im.split()
    rgb_image = Image.merge("RGB", (r, g, b))
    inverted_image = ImageOps.invert(rgb_image)
    r2, g2, b2 = inverted_image.split()
    final_transparent_image = Image.merge("RGBA", (r2, g2, b2, a))
    return final_transparent_image
