import math
import re
from io import BytesIO
from typing import List, Optional

from PIL import Image, ImageFilter, ImageOps
from PIL.ImageColor import colormap
from pil_utils import BuildImage, text2image
from pil_utils.gradient import ColorStop, LinearGradient
from pil_utils.types import ColorType

from .color_table import color_table
from .depends import Arg, Args, Img, Imgs, NoArg
from .utils import Maker, get_avg_duration, make_jpg_or_gif, save_gif, split_gif

colors = "|".join(colormap.keys())
color_pattern_str = rf"#[a-fA-F0-9]{{6}}|{colors}"

num_256 = r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])"
color_pattern_num = rf"(?:rgb)?\(?\s*{num_256}[\s,]+{num_256}[\s,]+{num_256}\s*\)?;?"


def flip_horizontal(img: BuildImage = Img(), arg=NoArg()):
    return make_jpg_or_gif(img, lambda img: img.transpose(Image.FLIP_LEFT_RIGHT))


def flip_vertical(img: BuildImage = Img(), arg=NoArg()):
    return make_jpg_or_gif(img, lambda img: img.transpose(Image.FLIP_TOP_BOTTOM))


def grey(img: BuildImage = Img(), arg=NoArg()):
    return make_jpg_or_gif(img, lambda img: img.convert("L"), keep_transparency=False)


def rotate(img: BuildImage = Img(), arg: str = Arg()):
    angle = None
    if not arg:
        angle = 90
    elif arg.isdigit() or (arg.startswith("-") and arg[1:].isdigit()):
        angle = int(arg)
    if not angle:
        return
    return make_jpg_or_gif(img, lambda img: img.rotate(angle, expand=True))


def resize(img: BuildImage = Img(), arg: str = Arg()):
    w, h = img.size
    match1 = re.fullmatch(r"(\d{1,4})?[*xX, ](\d{1,4})?", arg)
    match2 = re.fullmatch(r"(\d{1,3})%", arg)
    make: Optional[Maker] = None
    if match1:
        w = match1.group(1)
        h = match1.group(2)
        if not w and h:
            make = lambda img: img.resize_height(int(h))
        elif w and not h:
            make = lambda img: img.resize_width(int(w))
        elif w and h:
            make = lambda img: img.resize((int(w), int(h)))
    elif match2:
        ratio = int(match2.group(1)) / 100
        make = lambda img: img.resize((int(w * ratio), int(h * ratio)))
    if not make:
        return "请使用正确的尺寸格式，如：100x100、100x、50%"
    return make_jpg_or_gif(img, make)


def crop(img: BuildImage = Img(), arg: str = Arg()):
    w, h = img.size
    match1 = re.fullmatch(r"(\d{1,4})[*xX, ](\d{1,4})", arg)
    match2 = re.fullmatch(r"(\d{1,2})[:：比](\d{1,2})", arg)
    make: Optional[Maker] = None
    if match1:
        w = int(match1.group(1))
        h = int(match1.group(2))
        make = lambda img: img.resize_canvas((w, h), bg_color="white")
    elif match2:
        wp = int(match2.group(1))
        hp = int(match2.group(2))
        size = min(w / wp, h / hp)
        make = lambda img: img.resize_canvas((int(wp * size), int(hp * size)))
    if not make:
        return "请使用正确的裁剪格式，如：100x100、2:1"
    return make_jpg_or_gif(img, make)


def invert(img: BuildImage = Img(), arg=NoArg()):
    def make(img: BuildImage) -> BuildImage:
        result = BuildImage.new("RGB", img.size, "white")
        result.paste(img, alpha=True)
        return BuildImage(ImageOps.invert(result.image))

    return make_jpg_or_gif(img, make, keep_transparency=False)


def contour(img: BuildImage = Img(), arg=NoArg()):
    return make_jpg_or_gif(img, lambda img: img.filter(ImageFilter.CONTOUR))


def emboss(img: BuildImage = Img(), arg=NoArg()):
    return make_jpg_or_gif(img, lambda img: img.filter(ImageFilter.EMBOSS))


def blur(img: BuildImage = Img(), arg=NoArg()):
    return make_jpg_or_gif(img, lambda img: img.filter(ImageFilter.BLUR))


def sharpen(img: BuildImage = Img(), arg=NoArg()):
    return make_jpg_or_gif(img, lambda img: img.filter(ImageFilter.SHARPEN))


def pixelate(img: BuildImage = Img(), arg: str = Arg()):
    num = None
    if not arg:
        num = 8
    elif arg.isdigit():
        num = int(arg)
    if not num:
        return

    def make(img: BuildImage) -> BuildImage:
        image = img.image
        image = image.resize((img.width // num, img.height // num), resample=0)
        image = image.resize(img.size, resample=0)
        return BuildImage(image)

    return make_jpg_or_gif(img, make)


def color_mask(img: BuildImage = Img(), arg: str = Arg()):
    if re.fullmatch(color_pattern_str, arg):
        color = arg
    elif match := re.fullmatch(color_pattern_num, arg):
        color = tuple(map(int, match.groups()))
    elif arg in color_table:
        color = color_table[arg]
    else:
        return "请使用正确的颜色格式，如：#66ccff、red、红色、102,204,255"
    return make_jpg_or_gif(img, lambda img: img.color_mask(color))


def color_image(arg: str = Arg()):
    if re.fullmatch(color_pattern_str, arg):
        color = arg
    elif match := re.fullmatch(color_pattern_num, arg):
        color = tuple(map(int, match.groups()))
    elif arg in color_table:
        color = color_table[arg]
    else:
        return "请使用正确的颜色格式，如：#66ccff、red、红色、102,204,255"
    return BuildImage.new("RGB", (500, 500), color).save_jpg()


def gradient_image(args: List[str] = Args()):
    if not args:
        return
    angle = 0
    if args[0] in ["上下", "竖直"]:
        angle = 90
        args = args[1:]
    elif args[0] in ["左右", "水平"]:
        angle = 0
        args = args[1:]
    elif args[0].isdigit():
        angle = int(args[0])
        args = args[1:]
    if not args:
        return

    colors: List[ColorType] = []
    for arg in args:
        if re.fullmatch(color_pattern_str, arg):
            color = arg
        elif match := re.fullmatch(color_pattern_num, arg):
            color = tuple(map(int, match.groups()))
        elif arg in color_table:
            color = color_table[arg]
        else:
            return "请使用正确的颜色格式，如：#66ccff、red、红色、102,204,255"
        colors.append(color)

    img_w = 500
    img_h = 500
    angle *= math.pi / 180
    if math.sqrt(img_w**2 + img_h**2) * math.cos(angle) <= img_w:
        dy = img_h / 2
        dx = dy / math.tan(angle)
    else:
        dx = img_w / 2
        dy = dx * math.tan(angle)

    gradient = LinearGradient(
        (img_w / 2 - dx, img_h / 2 - dy, img_w / 2 + dx, img_h / 2 + dy),
        [ColorStop(i / (len(colors) - 1), color) for i, color in enumerate(colors)],
    )
    img = gradient.create_image((img_w, img_h))
    return BuildImage(img).save_jpg()


def gif_reverse(img: BuildImage = Img(), arg=NoArg()):
    image = img.image
    if getattr(image, "is_animated", False):
        frames = split_gif(image)
        duration = get_avg_duration(image) / 1000
        return save_gif(frames[::-1], duration)


def gif_obverse_reverse(img: BuildImage = Img(), arg=NoArg()):
    image = img.image
    if getattr(image, "is_animated", False):
        frames = split_gif(image)
        duration = get_avg_duration(image) / 1000
        frames = frames + frames[-2::-1]
        return save_gif(frames, duration)


def gif_change_fps(img: BuildImage = Img(), arg: str = Arg()):
    image = img.image
    if not getattr(image, "is_animated", False):
        return
    match1 = re.fullmatch(r"([\d\.]{1,4})(?:x|X|倍速?)", arg)
    match2 = re.fullmatch(r"(\d{1,3})%", arg)
    duration = get_avg_duration(image) / 1000
    if match1:
        duration /= float(match1.group(1))
    elif match2:
        duration /= int(match2.group(1)) / 100
    else:
        return "请使用正确的倍率格式，如：0.5x、50%"
    frames = split_gif(image)
    return save_gif(frames, duration)


def gif_split(img: BuildImage = Img(), arg=NoArg()):
    image = img.image
    if getattr(image, "is_animated", False):
        frames = split_gif(image)
        return [BuildImage(frame).save_png() for frame in frames]


def gif_join(imgs: List[BuildImage] = Imgs(), arg: str = Arg()):
    if not arg:
        duration = 100
    elif arg.isdigit():
        duration = int(arg)
    else:
        return

    if not imgs:
        return
    if len(imgs) < 2:
        return "gif合成至少需要2张图片"

    max_w = max([img.width for img in imgs])
    max_h = max([img.height for img in imgs])
    frames = [img.resize_canvas((max_w, max_h)).image for img in imgs]
    return save_gif(frames, duration / 1000)


def four_grid(img: BuildImage = Img(), arg=NoArg()):
    img = img.square()
    l = img.width // 2
    boxes = [
        (0, 0, l, l),
        (l, 0, l * 2, l),
        (0, l, l, l * 2),
        (l, l, l * 2, l * 2),
    ]
    output: List[BytesIO] = []
    for box in boxes:
        output.append(img.crop(box).save_png())
    return output


def nine_grid(img: BuildImage = Img(), arg=NoArg()):
    img = img.square()
    w = img.width
    l = img.width // 3
    boxes = [
        (0, 0, l, l),
        (l, 0, l * 2, l),
        (l * 2, 0, w, l),
        (0, l, l, l * 2),
        (l, l, l * 2, l * 2),
        (l * 2, l, w, l * 2),
        (0, l * 2, l, w),
        (l, l * 2, l * 2, w),
        (l * 2, l * 2, w, w),
    ]
    output: List[BytesIO] = []
    for box in boxes:
        output.append(img.crop(box).save_png())
    return output


def horizontal_join(imgs: List[BuildImage] = Imgs(), arg=NoArg()):
    if not imgs:
        return
    if len(imgs) < 2:
        return "图片拼接至少需要2张图片"

    spacing = 10
    img_h = min([img.height for img in imgs])
    imgs = [img.resize((img.width * img_h // img.height, img_h)) for img in imgs]
    img_w = sum([img.width for img in imgs]) + spacing * (len(imgs) - 1)
    frame = BuildImage.new("RGB", (img_w, img_h), "white")
    x = 0
    for img in imgs:
        frame.paste(img, (x, 0))
        x += img.width + spacing
    return frame.save_jpg()


def vertical_join(imgs: List[BuildImage] = Imgs(), arg=NoArg()):
    if not imgs:
        return
    if len(imgs) < 2:
        return "图片拼接至少需要2张图片"

    spacing = 10
    img_w = min([img.width for img in imgs])
    imgs = [img.resize((img_w, img.height * img_w // img.width)) for img in imgs]
    img_h = sum([img.height for img in imgs]) + spacing * (len(imgs) - 1)
    frame = BuildImage.new("RGB", (img_w, img_h), "white")
    y = 0
    for img in imgs:
        frame.paste(img, (0, y))
        y += img.height + spacing
    return frame.save_jpg()


def t2p(arg: str = Arg()):
    return BuildImage(text2image(arg, padding=(20, 20), max_width=1000)).save_png()
