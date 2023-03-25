from PIL import ImageDraw, ImageFont, Image


def text_border(text: str, draw: ImageDraw, x: int, y: int, font: ImageFont, shadow_colour: tuple, fill_colour: tuple, anchor: str = "ms"):
    """文字加边框"""
    draw.text((x - 1, y), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x + 1, y), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x, y - 1), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x, y + 1), text=text, anchor=anchor, font=font, fill=shadow_colour)

    draw.text((x - 1, y - 1), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x + 1, y - 1), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x - 1, y + 1), text=text, anchor=anchor, font=font, fill=shadow_colour)
    draw.text((x + 1, y + 1), text=text, anchor=anchor, font=font, fill=shadow_colour)

    draw.text((x, y), text=text, anchor=anchor, font=font, fill=fill_colour)


def round_corner(img: Image, radius: int = 30):
    """圆角"""
    circle = Image.new("L", (radius*2, radius*2), 0)  # 黑色背景
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius*2, radius*2), fill=255)  # 白色圆形

    img = img.convert("RGBA")
    w, h = img.size

    # 切圆
    alpha = Image.new("L", img.size, 255)
    lu = circle.crop((0, 0, radius, radius))
    ru = circle.crop((radius, 0, radius*2, radius))
    ld = circle.crop((0, radius, radius, radius*2))
    rd = circle.crop((radius, radius, radius*2, radius*2))
    alpha.paste(lu, (0, 0))  # 左上角
    alpha.paste(ru, (w-radius, 0))  # 右上角
    alpha.paste(ld, (0, h-radius))  # 左下角
    alpha.paste(rd, (w-radius, h-radius))  # 右下角

    img.putalpha(alpha)
    return img


__all__ = [
    "text_border",
    "round_corner"
]
