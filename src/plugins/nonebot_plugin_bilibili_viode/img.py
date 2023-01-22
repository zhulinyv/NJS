import time
from io import BytesIO
from pathlib import Path

import qrcode
from httpx import AsyncClient
from PIL import Image, ImageDraw, ImageFont

from .model import VideoInfo
from .utils import format_number, get_video_info


def circle_corner(img, radii):  # 把原图片变成圆角，
    """
    圆角处理
    :param img: 源图象。
    :param radii: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """

    # 画圆（用于分离4个角）
    circle = Image.new("L", (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形

    # 原图
    img = img.convert("RGBA")
    w, h = img.size

    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new("L", img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(
        circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii)
    )  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
    # alpha.show()

    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    return img

    # 创建二维码
    qrcode = Image.new("RGB", (300, 300), (255, 255, 255))
    # 创建二维码的Draw对象
    draw = ImageDraw.Draw(qrcode)


async def build_get_share_info(video_info: VideoInfo) -> bytes:
    """
    构建获取分享链接的图片
    :param video_id: 视频id
    :return: 图片
    """
    if not video_info:
        return None
    # 图片尺寸 1750 x 1500
    img_width = 1750
    img_height = 1500
    # 创建一个空白图片，背景色为白色
    img = Image.new("RGB", (img_width, img_height), (255, 255, 255))
    # 绘制UP主信息
    # UP头像贴到左上角
    async with AsyncClient() as client:
        resp = await client.get(video_info.upInfo.face)
        img_up_icon = Image.open(BytesIO(resp.content))
        img_up_icon = img_up_icon.resize((150, 150))
        img.paste(img_up_icon, (25, 25))
    # UP名字绘制到头像右侧，间距为25
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("msyh.ttc", 60)
    draw.text(
        (img_up_icon.width + 50, 30), video_info.upInfo.name, (251, 114, 153), font
    )
    # 发布时间绘制到UP名字下方，间距为25
    font = ImageFont.truetype("msyh.ttc", 80)
    # 计算发布时间
    now_time = int(time.time())
    time_diff = now_time - video_info.pubdate
    if time_diff < 60:
        time_str = "刚刚"
    elif time_diff < 3600:
        time_str = f"{int(time_diff / 60)}分钟前"
    elif time_diff < 3600 * 24:
        hours = int(time_diff / 3600 % 24)
        time_str = f"{hours}小时前"
    else:
        days = int(time_diff / 3600 / 24)
        time_str = f"{days}天前"
    # 绘制发布时间,字体颜色为灰色
    font = ImageFont.truetype("msyh.ttc", 50)
    draw.text(
        (img_up_icon.width + 50, 105),
        time_str,
        (128, 128, 128),
        font,
    )
    # 将网络图片转换为PIL图片
    async with AsyncClient() as client:
        resp = await client.get(video_info.pic)
        if resp.status_code == 200:
            picture = Image.open(BytesIO(resp.content))
            # 将图片缩放到宽度与空白图片左右留白25像素一致，高度自适应
            picture = picture.resize(
                (img_width - 50, int(picture.height * (img_width - 50) / picture.width))
            )
            # 将图片绘制到空白图片上
            img.paste(picture, (25, 300))

    # 绘制视频信息
    # 视频标题绘制到图片上，左边距为25
    title = video_info.title
    font = ImageFont.truetype("msyh.ttc", 90)
    if img_width - 50 < font.getsize(title)[0]:
        sum = 0
        for i in range(len(title)):
            sum += font.getsize(title[i])[0]
            if sum > img_width - 50:
                title = title[: i - 1] + "···"
                break
    # 在空白图片绘制文字,上边距为190，左边距为25，字体大小为60，字体颜色为黑
    draw.text((25, 180), title, (0, 0, 0), font=font)
    # 绘制视频简介
    desc = video_info.desc.replace("\n", "")
    font = ImageFont.truetype("msyh.ttc", 50)
    _height = 0
    # 如果视频简介超出2行
    if font.getsize(desc)[0] > (img_width - 50) * 2:
        # 计算简介字符的超出位数
        sum = 0
        n = 0
        for i in range(len(desc)):
            sum += font.getsize(desc[i])[0]
            if sum > (img_width - 50) * 2:
                # 将简介字符超出的部分删除
                desc = desc[: i - 5] + "···"
                break
            if sum > (img_width - 50):
                if n == 0:
                    n = i
        _height = img_height - font.getsize(desc)[1] * 2 - 5
        for i in range(0, len(desc), n):
            draw.text((25, _height), desc[i : i + n], (0, 0, 0), font=font)
            _height += font.getsize(desc[i : i + n])[1]
    # 如果简介不足2行，则图片高度裁剪70像素
    elif font.getsize(desc)[0] < (img_width - 50):
        img = img.crop((0, 0, img_width, img_height - 70))
        img_height -= 70
        _height = img_height - font.getsize(desc)[1] - 5
        draw = ImageDraw.Draw(img)
        # 在空白图片底部绘制文字,下边距为font高度乘2加25，左边距为25，字体颜色为黑
        draw.text((25, _height), desc, (0, 0, 0), font=font)

    # 将图片转换为PIL图片
    img = img.convert("RGB")
    # 将PIL图片转换为bytes
    img_bytes = BytesIO()
    img.save(img_bytes, "png")
    return img_bytes.getvalue()


async def build_video_poster(video_info: VideoInfo):
    """
    生成视频海报
    :param video_id: 视频id
    :return: 视频海报
    """
    if video_info is None:
        return None
    res_path = Path(__file__).parent.joinpath("resource")
    base_img = Image.open(res_path / "image/template.png")
    # 封面图片
    async with AsyncClient(verify=False) as client:
        resp = await client.get(video_info.pic)
        if resp.status_code == 200:
            picture = Image.open(BytesIO(resp.content))
            # 将图片缩放到宽度为725，高度自适应
            picture = picture.resize((722, 410), Image.ANTIALIAS)
            picture = circle_corner(picture, 10)
            # 将图片绘制到base图片上
            base_img.paste(picture, (120, 205), picture)
    # UP头像
    async with AsyncClient(verify=False) as client:
        resp = await client.get(video_info.upInfo.face)
        if resp.status_code == 200:
            picture = Image.open(BytesIO(resp.content))
            # 将图片缩放到宽度为100，高度自适应
            picture = picture.resize((100, 100), Image.ANTIALIAS)
            picture = circle_corner(picture, 50)
            # 将图片绘制到base图片上
            base_img.paste(picture, (70, 1055), picture)
    # 二维码
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=50,
        border=4,
    )
    qr.add_data(video_info.shareUrl)
    qr.make()
    picture = qr.make_image(fill_color="black", back_color="white")
    picture = picture.resize((150, 150))
    picture = circle_corner(picture, 20)
    base_img.paste(picture, (745, 1038), picture)

    draw = ImageDraw.Draw(base_img)

    # 视频标题
    title = video_info.title
    # 每行文字最大宽度为685，如果超出2行则截取
    font = ImageFont.truetype(
        (res_path / "font/SourceHanSansSC-Bold.otf").__str__(), 45
    )
    # 如果视频标题超出1行
    if font.getsize(title)[0] > 685:
        # 计算标题字符的超出位数
        sum = 0
        for i in range(len(title)):
            sum += font.getsize(title[i])[0]
            if sum > 685:
                title = title[:i] + "\n" + title[i:]
                break
    # 如果视频标题超出2行
    if font.getsize(title)[0] > 685 * 2:
        # 计算标题字符的超出位数
        sum = font.getsize("···")[0]
        for i in range(len(title)):
            sum += font.getsize(title[i])[0]
            if sum > 685 * 2:
                # 将标题字符超出的部分删除
                title = title[:i] + "···"
                break

    # 将标题绘制到base图片上
    draw.text((125, 703), title, (0, 0, 0), font=font)
    # 视频信息
    tmp = f"{format_number(video_info.stat.view)}播放· {format_number(video_info.stat.like)}点赞 · {format_number(video_info.stat.danmaku)}弹幕"
    font = ImageFont.truetype(
        (res_path / "font/SourceHanSansSC-Normal.otf").__str__(), 35
    )
    draw.text((125, 835), tmp, "#878789", font=font)
    # 视频发布时间
    tmp = "发布于：" + time.strftime("%Y-%m-%d %H:%M", time.localtime(video_info.pubdate))
    font = ImageFont.truetype(
        (res_path / "font/SourceHanSansSC-Light.otf").__str__(), 35
    )
    draw.text((133, 910), tmp, "#a9a9a9", font=font)
    # UP主信息
    tmp = video_info.upInfo.name
    font = ImageFont.truetype(
        (res_path / "font/SourceHanSansSC-Bold.otf").__str__(), 35
    )
    draw.text((195, 1070), tmp, "#575757", font=font)
    # UP主粉丝数
    tmp = f"{format_number(video_info.upInfo.fans)}粉丝"
    font = ImageFont.truetype(
        (res_path / "font/SourceHanSansSC-Normal.otf").__str__(), 30
    )
    draw.text((195, 1120), tmp, "#828385", font=font)

    base_img = base_img.convert("RGB")
    img_bytes = BytesIO()
    base_img.save(img_bytes, "png")
    return img_bytes.getvalue()
