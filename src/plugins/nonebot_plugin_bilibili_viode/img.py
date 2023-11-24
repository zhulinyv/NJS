import time
from io import BytesIO
from pathlib import Path

import httpx
import qrcode
from nonebot.log import logger
from PIL import Image, ImageDraw, ImageFont

from .models.bilibili import VideoInfo
from .models.config import ImageItem, TextItem
from .utils import format_number, load_config

IMG_DIR = Path(__file__).parent / 'resource/image'
FONT_DIR = Path(__file__).parent / 'resource/font'


def _str2color(color: str) -> tuple:
    """
    将颜色字符串转换为RGB元组
    """
    if color.startswith('#'):
        color = color[1:]
        return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
    elif color.startswith('rgb('):
        color = color[4:-1]
        return tuple(int(c) for c in color.split(','))
    else:
        raise ValueError('不支持的颜色格式')


def _font_wight(font: ImageFont, text: str) -> int:
    """
    计算文本的宽度
    """
    return font.getlength(text)


def _font_remove(
    text: str,
    font: ImageFont,
    max_width: int,
) -> str:
    """
    根据最大宽度，移除文本中的部分字符,并在末尾添加省略号（由于添加省略号后宽度可能超过最大宽度，所以需要多次调用该方法）
    """
    while _font_wight(font, text) > max_width:
        text = text[:-1]
    return text + '...' if text != '' else ''


def _text_split(
    text: str,
    font: ImageFont,
    max_width: int,
    max_lines: int,
) -> str:
    """
    根据最大宽度和最大行数，将文本分割为多行
    """
    lines = []
    line = ''
    for c in text:
        if _font_wight(font, line + c) <= max_width:
            line += c
        else:
            lines.append(line)
            line = c
    lines.append(line)
    # 如果行数超过最大行数，则截断多余的行，并移除多余的字符
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = _font_remove(lines[-1], font, max_width)
    result = ''
    for line in lines:
        result += line + '\n'
    return result[:-1]


def _circle_image(img: Image, radius: int) -> Image:
    """
    圆角处理
    :param img: 源图象。
    :param radius: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """
    """
    圆角处理
    :param img: 源图象。
    :param radius: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """
    if radius <= 0:
        return img
    # 画圆（用于分离4个角）
    circle = Image.new('L', (radius * 2, radius * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)  # 画白色圆形
    # 原图
    img = img.convert("RGBA")
    w, h = img.size

    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)),
                (w - radius, 0))  # 右上角
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)),
                (w - radius, h - radius))  # 右下角
    alpha.paste(circle.crop((0, radius, radius, radius * 2)),
                (0, h - radius))  # 左下角
    # alpha.show()

    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    return img


def _url2QRcode(url: str) -> Image:
    """
    将url转换为二维码图片
    :param url: url
    :return: 二维码图片
    """
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=0)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black",
                        back_color=(255, 255, 255, 0)).convert('RGBA')
    img_data = img.getdata()
    new_data = []
    for item in img_data:
        if item[3] == 0:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img


def _url2Image(url: str, size: tuple = (0, 0)) -> Image:
    """
    将url转换为Image对象
    :param url: url
    :param size: 图片大小,默认为(0,0)，表示不改变图片大小
    """
    response = httpx.get(url, verify=False, timeout=None)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        if size != (0, 0):
            img = img.resize(size)
        return img


def _render_image(draw, data, config: ImageItem):
    """
    在底层画布上绘制一个图像。

    参数：
    - draw：底层画布
    - data：图像数据，一个Image对象
    - config：图像配置项，一个字典，包括以下字段：
        - x：图像左上角在画布上的x坐标
        - y：图像左上角在画布上的y坐标
        - width：图像的宽度
        - height：图像的高度
        - opacity：不透明度（0-255）

    返回值：无

    """
    # 如果指定了图像文件名
    if config.path:
        # 如果文件名是一个url，则先下载图像
        if config.path.startswith('http'):
            data = _url2Image(config.path)
        # 如果文件名是一个本地文件，则直接读取图像
        else:
            data = Image.open(IMG_DIR / config.path)
    # 如果没有指定宽度和高度，则使用原图的宽度和高度
    _width = config.width if config.width else data.width
    _height = config.height if config.height else data.height
    # 如果有指定圆角半径，则将图像裁剪为圆形
    if config.radius:
        data = _circle_image(data, config.radius)
    else:
        data = data.convert('RGBA')
    # 将图像缩放到指定大小
    data = data.resize((_width, _height), Image.LANCZOS)
    # 将图像粘贴到画布上
    draw.paste(data, (config.x, config.y), data)
    return draw


def _render_text(draw, text, config: TextItem):
    """
    在底层画布上绘制一段文本。

    参数：
    - draw：底层画布
    - text：文本内容，一个字符串
    - config：文本配置项，一个字典，包括以下字段：
        - x：文本左上角在画布上的x坐标
        - y：文本左上角在画布上的y坐标
        - font：字体文件路径
        - font_size：字体大小
        - color：文本颜色，一个#开头的十六进制颜色值
        - font_max_width：文本最大宽度，超过该宽度则自动换行
        - font_max_lines：文本最大行数，超过该行数则自动截断

    返回值：无
    """
    font = ImageFont.truetype(str(FONT_DIR / config.font), config.font_size)
    # 如果指定了最大宽度，
    if config.font_max_width:
        # 如果指定了最大行数
        if config.font_max_lines:
            # 如果文本的宽度大于最大宽度乘以最大行数，则先分割文本为多行
            if _font_wight(font, text) > config.font_max_width:
                text = _text_split(text, font, config.font_max_width,
                                   config.font_max_lines)
        # 如果没有指定最大行数，则直接移除文本中的部分字符
        else:
            text = _font_remove(text, font, config.font_max_width)
    # 将颜色转换为RGBA格式
    color = _str2color(config.font_color)
    draw.text(xy=(config.x, config.y), text=str(text), font=font, fill=color)
    return draw


def render_img(video_info: VideoInfo, config: str) -> Image:
    """
    根据视频信息和配置项生成视频封面。

    参数：
    - video_info：视频信息，一个VideoInfo对象
    - config：配置项索引，默认值为0，表示使用templates目录下的0.yaml配置文件

    返回值：一个Image对象
    """
    start_time = time.time()

    # 读取配置文件
    config = load_config(config)
    logger.debug(f"读取配置文件耗时：{time.time()-start_time}秒")
    # 创建画布
    canvas_config = config['base']
    w = canvas_config.get('width')
    h = canvas_config.get('height')
    c = canvas_config.get('color', (255, 255, 255, 0))
    # 如果没有指定宽度和高度，则尝试使用background_image的宽度和高度
    if not w or not h:
        try:
            background_image = config.get('background_image')
            if background_image:
                w = background_image.get('width')
                h = background_image.get('height')
            else:
                raise ValueError("未指定宽度和高度")
        except Exception as e:
            raise e
    canvas = Image.new('RGBA', (w, h), c)
    config.pop('base')
    draw = ImageDraw.Draw(canvas)
    logger.debug(f"创建画布耗时：{time.time()-start_time}秒")
    # 预处理 VideoInfo, 将其中的数据转换
    video_data = {
        'title':
        video_info.title,  # 视频标题
        'cover':
        _url2Image(video_info.pic),  # 封面
        'duration':
        time.strftime("%M:%S", time.gmtime(video_info.duration)),  # 时长
        'pubdate':
        time.strftime("发布于 %Y-%m-%d %H:%M:%S",
                      time.localtime(video_info.pubdate)),  # 发布时间
        'view':
        format_number(video_info.stat.view) + " 播放",  # 播放量
        'danmaku':
        format_number(video_info.stat.danmaku) + " 弹幕",  # 弹幕数
        'favorite':
        format_number(video_info.stat.favorite) + " 收藏",  # 收藏数
        'coin':
        format_number(video_info.stat.coin) + " 硬币",  # 硬币数
        'share':
        format_number(video_info.stat.share) + " 分享",  # 分享数
        'like':
        format_number(video_info.stat.like) + " 点赞",  # 点赞数
        'up_name':
        video_info.owner.name,  # up主名字
        'up_face':
        _url2Image(video_info.owner.face, (300, 300)),  # up主头像
        'up_mid':
        video_info.owner.mid,  # up主mid
        'up_follower':
        format_number(video_info.owner.follower) + "粉丝",  # up主粉丝数
        'qrcode':
        _url2QRcode(video_info.share_url),  # 二维码
    }
    logger.debug(f"预处理VideoInfo耗时：{time.time()-start_time}秒")
    # 循环从配置文件读取每个配置项，并根据配置项的类型调用相应的渲染函数
    for k, v in config.items():
        if v.get('type') == 'image':
            c = ImageItem(**v)
            _render_image(canvas, video_data.get(k), c)
        elif v.get('type') == 'text':
            c = TextItem(**v)
            _render_text(draw, video_data.get(k), c)
        else:
            raise ValueError("未知的配置项类型")
    logger.debug(f"渲染耗时：{time.time()-start_time}秒")
    return canvas
