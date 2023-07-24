# 导入依赖
import ujson as json
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw


async def draw_help():
    # 当前路径
    path = Path(__file__).parent

    # 读取数据
    with open("./data/njs_help_new/help.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 总插件数
    number = 0
    for i in data["插件列表"]:
        number += 1
    
    # 总列数 (20 个插件为 1 列)
    list_number = number // 20
    if list_number < (number / 20):
        list_number += 1

    # 总排数 (3 列插件为 1 排)
    if ((list_number - 2) % 3) != 0:
        row_number = ((list_number - 2) // 3) + 1 + 1
    else:
        row_number = ((list_number - 2) // 3) + 1

    # 背景高度 (3 列为 600 像素高度)
    if list_number > 2:
        more = number % 20
        if more != 0 and (list_number % 3) == 0:
            height  = int(((row_number - 1) * 600  + (more * 26.5)) + 70)
        else:
            height = row_number * 600
    else:
        height = 600

    # 背景宽度 (1 列为 360 像素宽度)
    if list_number == 1:
        width = 720
    elif list_number > 2:
        width = 1080
    else:
        width = 360

    # 创建背景
    background = Image.new(mode="RGB", size=(width, height), color="white")

    # 读取字体到内存中
    with open(path / "Aa芒小果.ttf", "rb") as font:
        bytes_font = BytesIO(font.read())
        # 标题字体
        title_font = ImageFont.truetype(font=bytes_font, size=30)
    with open(path / "Aa芒小果.ttf", "rb") as font:
        bytes_font = BytesIO(font.read())
        # 颜色说明字体
        color_font = ImageFont.truetype(font=bytes_font, size=15)
    with open(path / "Aa芒小果.ttf", "rb") as font:
        bytes_font = BytesIO(font.read())
        # 作者字体
        author_font = ImageFont.truetype(font=bytes_font, size=20)
    with open(path / "Aa芒小果.ttf", "rb") as font:
        bytes_font = BytesIO(font.read())
        # 说三遍字体
        three_font = ImageFont.truetype(font=bytes_font, size=15)
    with open(path / "Aa芒小果.ttf", "rb") as font:
        bytes_font = BytesIO(font.read())
        # 插件名称字体
        plugin_font = ImageFont.truetype(font=bytes_font, size=22)
    # 答辩, 我也布吉岛为什么直接重新调整字体大小会报错, 只好重新打开了捏...

    # 添加标题
    draw = ImageDraw.Draw(background)
    draw.text(xy=(75, 30), text="《脑积水帮助》", fill=(0, 0, 0), font=title_font)

    # 打开 logo
    logo = Image.open(path / "njs_logo.png")

    # 调整图片大小
    logo = logo.resize((200, 200))

    # 添加 logo
    background.paste(logo, (80, 100, 280, 300))

    # 添加颜色说明
    draw.text(xy=(10, 320), text="*绿色表示正常可用", fill=(0, 176, 80), font=color_font)
    draw.text(xy=(10, 340), text="*蓝色表示部分停用", fill=(0, 176, 240), font=color_font)
    draw.text(xy=(10, 360), text="*红色表示正在维护", fill=(255, 0, 0), font=color_font)

    # 添加序号说明
    draw.text(xy=(45, 395), text="以下仅为功能名称, 并非指令!", fill=(0, 0, 0), font=author_font)

    # 添加说三遍
    for i in range(3):
        draw.text(xy=(55, 420 + i * 16.5), text="发送\"njs+序号或名称\"查看帮助捏~", fill=(0, 0, 0), font=three_font)

    # 添加小提示
    draw.text(xy=(100, 475), text="(重要的事情说三遍! ! !)", fill=(0, 0, 0), font=three_font)

    # 辅助线
    # draw.line((360, 0, 360, 1200), width=5, fill=(0, 0, 0))
    # draw.line((720, 0, 720, 1200), width=5, fill=(0, 0, 0))
    # draw.line((0, 600, 1080, 600), width=5, fill=(0, 0, 0))

    # 添加作者
    draw.text(xy=(95, 530), text="Powered by Xytpz", fill=(0, 0, 0), font=author_font)

    # 绘制帮助
    num = 0
    for i in range(row_number):
        for g in range(3):
            if num == 0:
                num += 1
            elif num > number:
                break
            elif (num == number) and ((g == 1) or (g == 2)):
                break
            else:
                x = 360 * g + 60
                y = 600 * i + 30
                for k in range(20):
                    text = data["插件列表"][num - 1]["插件名"]
                    color = data["插件列表"][num - 1]["显示颜色"]
                    if color == "绿色":
                        draw.text(xy=(x, y), text=f"{num}. {text}", fill=(0, 176, 80), font=plugin_font)
                    elif color == "蓝色":
                        draw.text(xy=(x, y), text=f"{num}. {text}", fill=(0, 176, 240), font=plugin_font)
                    elif color == "红色":
                        draw.text(xy=(x, y), text=f"{num}. {text}", fill=(255, 0, 0), font=plugin_font)
                    else:
                        draw.text(xy=(x, y), text=f"{num}. {text}", fill=(0, 0, 0), font=plugin_font)
                    y += 26.5
                    if num < number:
                        num += 1
                    else:
                        break

    # 保存图片
    background.save(path / "help_new.png")
