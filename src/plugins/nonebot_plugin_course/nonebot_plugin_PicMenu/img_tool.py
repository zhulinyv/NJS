import base64
import re
from io import BytesIO
from pathlib import Path
from typing import List, Literal, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFilter, ImageFont, PngImagePlugin
from PIL.Image import Image as Img


class Box(object):
    def __init__(
        self,
        pos: Tuple[int, int] = (0, 0),
        size: Tuple[int, int] = None,
    ):
        """
        说明:
            Box对象，图片处理的参考框，根据坐标和大小生成基础点
        参数:
            :param pos:
            :param size:
        """
        if size is None:
            raise ValueError('param "size" is necessary')
        self.pos = pos
        self.size = size
        self.left = pos[0]
        self.right = pos[0] + size[0]
        self.top = pos[1]
        self.bottom = pos[1] + size[1]
        self.topLeft = pos
        self.topRight = (self.right, self.top)
        self.bottomLeft = (self.left, self.bottom)
        self.bottomRight = (self.right, self.bottom)


class ImageFactory(object):
    def __init__(
        self,
        img: Union[Optional[str], Img, BytesIO] = None,
        image_mode: str = "RGBA",
    ):
        """
        说明:
            进行图像合成的基础对象
        参数：
            :param img: 图像处理的底版
            :param image_mode: 图像的类型
        """
        if not img:
            raise ValueError("An Image needed")
        if type(img) is Img or type(img) is PngImagePlugin.PngImageFile:
            self.img = img
        else:
            self.img = Image.open(img)
        self.mode = image_mode
        self.img.convert(image_mode)
        self.draw = ImageDraw.Draw(self.img)
        self.boxes = {}  # 参照方框
        self.boxes.update({"self": Box((0, 0), self.img.size)})

    def get_size(self):
        """
        说明: 获得处理图片的大小
        :return: 处理图片大小的元组
        """
        return self.img.size

    def change_making_img(self, img: Union[Optional[str], Img] = None):
        """
        说明: 更换正在处理的图片
        :param img: Image对象，或图片路径
        """
        if type(img) is Img:
            self.img = img
        else:
            self.img = Image.open(img)
        self.img.convert(self.mode)
        self.draw = ImageDraw.Draw(self.img)
        self.boxes["self"] = Box((0, 0), self.img.size)

    def add_box(self, box_id: str, pos: Tuple[int, int], size: Tuple[int, int]):
        """
        说明: 项目添加参考框
            :param box_id: 参考框key
            :param pos: 参考框位置（左上角）
            :param size: 参考框
        """
        self.boxes.update({box_id: Box(pos, size)})

    def align_box(
        self,
        box: Union[Box, str] = None,
        img: Union[Img, Box, Tuple[int, int]] = None,
        pos: Tuple[int, int] = None,
        align: Optional[Literal["center", "horizontal", "vertical"]] = None,
    ) -> tuple:
        """
        说明:
            得到img对齐参考框在making_img中的像素坐标
        参数:
            :param box: 参考框集中字典的key或Box对象
            :param img: 要对齐的img
            :param pos: 目标对齐点，空为参考框的左上角，中心对齐时无效
            :param align: 对齐方式
        返回值:
            :return: 坐标元组（左上角目标点）
        """

        def get_center(b_pos, b_size):
            h_c = int(b_pos[0] + b_size[0] / 2)
            v_c = int(b_pos[1] + b_size[1] / 2)
            return h_c, v_c

        if not box or not img:
            raise ValueError("A box and an img are necessary")
        if isinstance(box, str):
            if box not in self.boxes.keys():
                raise ValueError(f'The "{box}" not in foundation_box')
            else:
                box_pos = self.boxes[box].pos
                box_size = self.boxes[box].size
        elif isinstance(box, Box):
            box_pos, box_size = box.pos, box.size
        if not pos:
            pos = box_pos
        if align:
            if align not in ["center", "horizontal", "vertical"]:
                raise ValueError(
                    "center_type must be 'center', 'horizontal' or 'vertical'"
                )
            else:
                if isinstance(img, Img):
                    size = img.size
                elif isinstance(img, tuple):
                    size = img
                if align == "center":
                    h_center, v_center = get_center(box_pos, box_size)
                    align_x = int(h_center - size[0] / 2)
                    align_y = int(v_center - size[1] / 2)
                elif align == "horizontal":
                    h_center, _ = get_center(box_pos, box_size)
                    align_x = int(h_center - size[0] / 2)
                    align_y = pos[1]
                elif align == "vertical":
                    _, v_center = get_center(box_pos, box_size)
                    align_x = pos[0]
                    align_y = int(v_center - size[1] / 2)
        else:
            align_x, align_y = pos
        return align_x, align_y

    def img_paste(
        self,
        img: Img,
        pos: Tuple[int, int] = (0, 0),
        isalpha: bool = False,
        align: Optional[Literal["center", "horizontal", "vertical"]] = None,
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        说明:
            在处理底版上粘贴img2
        参数:
            :param img: 粘贴图
            :param pos: 粘贴点（左上角）
            :param isalpha：图片背景是否为透明
            :param align: 对齐方式 "center": 中心对齐 "horizontal": 水平对齐 "vertical": 竖直对齐
            :return 粘贴图的粘贴点以及size
        """
        if align:
            if align not in ["center", "horizontal", "vertical"]:
                raise ValueError(
                    "center_type must be 'center', 'horizontal' or 'vertical'"
                )
            else:
                if align == "center":
                    width = int((self.img.size[0] - img.size[0]) / 2)
                    height = int((self.img.size[1] - img.size[1]) / 2)
                elif align == "horizontal":
                    width = int((self.img.size[0] - img.size[0]) / 2)
                    height = pos[1]
                elif align == "vertical":
                    width = pos[0]
                    height = int((self.img.size[1] - img.size[1]) / 2)
                pos = (width, height)
        if isalpha:
            try:
                self.img.paste(img, pos, img)
            except ValueError:
                img = img.convert("RGBA")
                self.img.paste(img, pos, img)
        else:
            self.img.paste(img, pos)
        return pos, img.size

    def img_crop(self, box: Union[Box, str]):
        """
        说明: 根据box剪切处理图片
        :param box: 有box坐标及尺寸的元组，或在参考框集中字典的key
        :return: Image对象
        """
        if isinstance(box, str):
            if box not in self.boxes:
                raise ValueError(f'The "{box}" not in foundation_box')
            else:
                box_pos = self.boxes[box].pos
                box_size = self.boxes[box].size
        elif isinstance(box, Box):
            box_pos, box_size = box.pos, box.size
        else:
            raise ValueError('Param "box" expect string or Box object')
        start_pos = box_pos
        end_pos = (box_pos[0] + box_size[0], box_pos[1] + box_size[1])
        crop_region = self.img.crop((*start_pos, *end_pos))
        return crop_region

    def point(
        self,
        pos: Tuple[int, int],
        fill: Union[Tuple[int, int, int], Tuple[int, int, int, int]] = None,
    ):
        """
        说明：
            在处理图片上绘制点
        参数:
            :param pos:
            :param fill:
        """
        self.draw.point(pos, fill=fill)

    def ellipse(
        self,
        box: Union[Box, str],
        fill: Optional[Tuple[int, int, int]] = None,
        outline: Optional[Tuple[int, int, int]] = None,
        width: int = 1,
    ):
        """
        说明：
            绘制圆或椭圆
        参数：
            :param box: 有box坐标及尺寸的元组，或在参考框集中字典的key
            :param fill: 填充颜色
            :param outline: 描线颜色
            :param width: 描线宽度
        """
        if isinstance(box, str):
            if box not in self.boxes:
                raise ValueError(f'The "{box}" not in foundation_box')
            else:
                box_pos = self.boxes[box].pos
                box_size = self.boxes[box].size
        elif isinstance(box, Box):
            box_pos, box_size = box.pos, box.size
        else:
            raise ValueError('Param "box" expect string or Box object')
        start_pos = box_pos
        end_pos = (box_pos[0] + box_size[0], box_pos[1] + box_size[1])
        self.draw.ellipse((*start_pos, *end_pos), fill, outline, width)

    def rectangle(
        self,
        box: Union[Box, str],
        color: Union[Tuple[int, int, int], Tuple[int, int, int, int]] = None,
        outline: Union[Tuple[int, int, int], Tuple[int, int, int, int], str] = None,
        width: int = 1,
    ):
        """
        说明：
            绘制矩形
        参数：
            :param box: 矩形的box
            :param color: 填充颜色
            :param outline: 轮廓颜色
            :param width: 线宽
        """
        if isinstance(box, str):
            if box not in self.boxes:
                raise ValueError(f'The "{box}" not in foundation_box')
            else:
                box_pos = self.boxes[box].pos
                box_size = self.boxes[box].size
        elif isinstance(box, Box):
            box_pos, box_size = box.pos, box.size
        else:
            raise ValueError('Param "box" expect string or Box object')
        start_pos = box_pos
        end_pos = (box_pos[0] + box_size[0], box_pos[1] + box_size[1])
        if color is not None:
            if len(color) == 3 or type(color) == str:
                self.draw.rectangle((*start_pos, *end_pos), color, outline, width)
            elif len(color) == 4:
                self.img_paste(Image.new("RGBA", box_size, color=color), box_pos)
                self.draw.rectangle(
                    (*start_pos, *end_pos), outline=outline, width=width
                )
        else:
            self.draw.rectangle((*start_pos, *end_pos), color, outline, width)

    def line(
        self,
        xy: Tuple[int, int, int, int],
        fill: Optional[Union[Tuple[int, int, int], str]] = None,
        width: int = 1,
    ):
        """
        说明：
            绘制直线
        参数：
            :param xy: 坐标
            :param fill: 填充
            :param width: 线宽
        """
        self.draw.line(xy, fill, width)

    def resize(
        self,
        ratio: float = 0,
        w: int = 0,
        h: int = 0,
        mode: Optional[Literal["Equal"]] = None,
    ):
        """
        说明：
            压缩图片
        参数：
            :param ratio: 压缩倍率
            :param w: 压缩图片宽度至 w
            :param h: 压缩图片高度至 h
            :param mode: 等比缩放
        """
        if mode == "Equal" and (w == 0 or h == 0) and (w, h) != (0, 0):
            if w == 0:
                ratio = h / self.img.size[1]
                w = int(self.img.size[0] * ratio)
            if h == 0:
                ratio = w / self.img.size[0]
                h = int(self.img.size[1] * ratio)
        else:
            if not w and not h and not ratio:
                raise Exception("缺少参数...")
            if not w and not h and ratio:
                w = int(self.img.size[0] * ratio)
                h = int(self.img.size[1] * ratio)
        self.change_making_img(self.img.resize((w, h), Image.ANTIALIAS))

    def filter(self, filter_: str, aud: int = None):
        """
        说明：
            图片变化
        参数：
            :param filter_: 变化效果
            :param aud: 利率
        """
        _x = None
        if filter_ == "GaussianBlur":  # 高斯模糊
            _x = ImageFilter.GaussianBlur
        elif filter_ == "EDGE_ENHANCE":  # 锐化效果
            _x = ImageFilter.EDGE_ENHANCE
        elif filter_ == "BLUR":  # 模糊效果
            _x = ImageFilter.BLUR
        elif filter_ == "CONTOUR":  # 铅笔滤镜
            _x = ImageFilter.CONTOUR
        elif filter_ == "FIND_EDGES":  # 边缘检测
            _x = ImageFilter.FIND_EDGES
        if _x:
            if aud:
                img = self.img.filter(_x(aud))
            else:
                img = self.img.filter(_x)
        self.change_making_img(img)

    def show(self):
        """
        说明：
            展示基础图片
        """
        self.img.show()


def simple_text(
    text: str,
    size: int,
    font: str = "SIMYOU.TTF",
    color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = "black",
):
    """
    说明:
    :param text:
    :param size:
    :param font:
    :param color:
    :return:
    """
    using_font = ImageFont.truetype(font, size)
    pic_size = using_font.getsize(text)
    pic = Image.new("RGBA", pic_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(pic)
    draw.text((0, 0), text, fill=color, font=using_font)
    return pic


def calculate_text_size(text: str, size: int, font: Union[str, Path]):
    """
    说明:
    :param text:
    :param size:
    :param font:
    :return:
    """
    using_font = ImageFont.truetype(font, size)
    return using_font.getsize(text)


def multi_text(
    text: str,
    spacing: int = 0,
    default_font: str = "SIMYOU.TTF",
    default_color: Union[
        str, Tuple[int, int, int], Tuple[int, int, int, int]
    ] = "black",
    default_size: int = 20,
    default_stroke_width: int = 0,
    default_stroke_fill: Union[
        str, Tuple[int, int, int], Tuple[int, int, int, int]
    ] = "black",
    box_size: Tuple[int, int] = (0, 0),
    horizontal_align: Optional[Literal["left", "middle", "right"]] = "left",
    vertical_align: Optional[Literal["top", "middle", "bottom"]] = "bottom",
    h_border_ignore: bool = False,
    v_border_ignore: bool = False,
    get_surplus: bool = False,
) -> Union[Img, Tuple[Img, str]]:
    """
    说明：
        将富文本转换为透明底版图片
        特殊文本起止符：<ft ...> ... </ft>
        可选参数:
                fonts(字体）：str
                size（字体大小）：int
                color（字体颜色）：str（颜色英文/十六位颜色编码）、tuple(rgb)/tuple(rgba)
                stroke_width （字体粗细程度）: int
                stroke_fill
    :param text: 富文本字符串
    :param spacing: 行距 px
    :param default_font: 非特殊文本默认字体
    :param default_color: 非特殊文本默认颜色
    :param default_size: 非特殊文本默认大小
    :param default_stroke_width: 非特殊文本默认轮廓宽度
    :param default_stroke_fill: 非特殊文本默认轮廓颜色
    :param box_size: 目标转换的box大小 tuple(width, height) 长宽任一值非正，
                     视为该维度无边界限制，将根据转换实际文本大小自适应，同时
                     对应边界限制参数无效
    :param horizontal_align:
    :param vertical_align:
    :param h_border_ignore: 是否无视水平边界限制，默认为False
    :param v_border_ignore: 是否无视垂直边界限制，默认为False
    :param get_surplus: 是否获得多余的字符串
    :return: Img对象
    """
    if box_size[0] <= 0:
        h_border_ignore = True
    if box_size[1] <= 0:
        v_border_ignore = True
    source_box = box_size
    surplus_text = ""
    # 分割换行符
    enter_list = text.split("\n")
    total_lines = []
    # 解析原始文本
    for line in enter_list:
        # 根据特殊文本结束符号分片
        raw_split_list = line.split("</ft>")
        line_pieces = []
        for piece in raw_split_list:
            # 匹配<ft>中内容
            a = re.search(r"<ft(.*)>", piece)
            if a:
                # 匹配结果起始及结束下标
                start, end = a.span()
                font = default_font
                size = default_size
                color = default_color
                stroke_width = default_stroke_width
                stroke_fill = default_stroke_fill
                # 根据文本对参数赋值
                for param in a.group(1).split():
                    _param = param.split("=")
                    if _param[0] == "fonts":
                        font = _param[1]
                    elif _param[0] == "size":
                        size = int(_param[1])
                    elif _param[0] == "stroke_width":
                        stroke_width = int(_param[1])
                    elif _param[0] == "color":
                        rgba_result = re.findall(r"\d+", _param[1])
                        if len(rgba_result) in [3, 4]:
                            color = tuple((int(x) for x in rgba_result))
                        else:
                            color = _param[1]
                    elif _param[0] == "stroke_fill":
                        rgba_result = re.findall(r"\d+", _param[1])
                        if len(rgba_result) in [3, 4]:
                            stroke_fill = tuple((int(x) for x in rgba_result))
                        else:
                            stroke_fill = _param[1]
                # 特殊文本外的结果储存
                if piece[:start]:
                    front_piece = {
                        "fonts": default_font,
                        "size": default_size,
                        "color": default_color,
                        "stroke_width": default_stroke_width,
                        "stroke_fill": default_stroke_fill,
                        "text": piece[:start],
                    }
                    line_pieces.append(front_piece)
                # 特殊文本结果储存
                multi_piece = {
                    "fonts": font,
                    "size": size,
                    "color": color,
                    "stroke_width": stroke_width,
                    "stroke_fill": stroke_fill,
                    "text": piece[end:],
                }
                line_pieces.append(multi_piece)
            else:
                if piece:
                    other_piece = {
                        "fonts": default_font,
                        "size": default_size,
                        "color": default_color,
                        "stroke_width": default_stroke_width,
                        "stroke_fill": default_stroke_fill,
                        "text": piece,
                    }
                    line_pieces.append(other_piece)
        # 总行储存
        total_lines.append(line_pieces)
    # 是否自动换行处理
    if not h_border_ignore and box_size[0] > 0:
        if default_stroke_width > 0:
            box_size = (box_size[0] - default_stroke_width * 2, box_size[1])
        new_total_lines = []
        for line in total_lines:
            new_line = []
            new_line_width = 0
            new_piece_cha_list = []
            for i, piece in enumerate(line):
                using_font = ImageFont.truetype(piece["fonts"], piece["size"])
                for cha in piece["text"]:
                    cha_width, _ = using_font.getsize(cha)
                    new_line_width += cha_width
                    if new_line_width <= box_size[0]:
                        new_piece_cha_list.append(cha)
                    else:
                        new_text = "".join(new_piece_cha_list)
                        new_piece = piece.copy()
                        new_piece["text"] = new_text
                        new_line.append(new_piece)
                        new_total_lines.append(new_line)
                        new_line = []
                        new_line_width = cha_width
                        new_piece_cha_list = [cha]
                new_text = "".join(new_piece_cha_list)
                new_piece = piece.copy()
                new_piece["text"] = new_text
                new_line.append(new_piece)
                new_piece_cha_list = []
                if i == len(line) - 1:
                    new_total_lines.append(new_line)
        total_lines = new_total_lines
    # 是否超高舍去
    if not v_border_ignore and box_size[1] > 0:
        if default_stroke_width > 0:
            box_size = (box_size[0], box_size[1] - default_stroke_width * 2)
        total_height = 0
        for i, line in enumerate(total_lines):
            line_height = 0
            for piece in line:
                using_font = ImageFont.truetype(piece["fonts"], piece["size"])
                _, piece_height = using_font.getsize(piece["text"])
                if piece_height > line_height:
                    line_height = piece_height
            if total_height + line_height + spacing > box_size[1]:
                if get_surplus:
                    lines_text = []
                    for new_line in total_lines[i:]:
                        line_texts = []
                        for piece in new_line:
                            params = [
                                f"{key}={value}"
                                for key, value in piece.items()
                                if key != "text"
                            ]
                            piece_text = f'<ft {" ".join(params)}>{piece["text"]}</ft>'
                            line_texts.append(piece_text)
                        lines_text.append("".join(line_texts))
                    surplus_text = "\n".join(lines_text)

                    total_lines = total_lines[:i]
                else:
                    total_lines = total_lines[:i]
                break
            else:
                total_height += line_height + spacing
    # 整体测高
    if box_size[0] <= 0 or box_size[1] <= 0:
        total_height, total_width = 0, 0
        for i, line in enumerate(total_lines):
            line_height, line_width = 0, 0
            for piece in line:
                using_font = ImageFont.truetype(piece["fonts"], piece["size"])
                piece_width = using_font.getsize(piece["text"])[0]
                piece_height = using_font.getsize(piece["text"])[1]
                line_width += piece_width
                if piece_height > line_height:
                    line_height = piece_height
            total_height += line_height
            if i != len(total_lines) - 1:
                total_height += spacing
            if line_width > total_width:
                total_width = line_width
        if box_size[0] <= 0:
            box_size = (total_width, box_size[1])
        if box_size[1] <= 0:
            box_size = (box_size[0], total_height)
    true_box_size = (
        box_size[0] + default_stroke_width * 2,
        box_size[1] + default_stroke_width * 2,
    )
    if not h_border_ignore and source_box != (0, 0):
        true_box_size = (source_box[0], box_size[1] + default_stroke_width * 2)
    if not v_border_ignore and source_box != (0, 0):
        true_box_size = (box_size[0] + default_stroke_width * 2, source_box[1])
    img = Image.new("RGBA", true_box_size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pos = (0 + default_stroke_width, 0 + default_stroke_width)
    line_start_pos = list(pos)
    # 对片进行分行，测量，显示
    for x in total_lines:
        pieces_sizes = []
        for y in x:
            using_font = ImageFont.truetype(y["fonts"], y["size"])
            pieces_sizes.append(using_font.getsize(y["text"]))
        height_list = [x[1] for x in pieces_sizes]
        width_list = [x[0] for x in pieces_sizes]
        max_height = max(height_list)
        total_width = sum(width_list) + len(width_list) * spacing
        if horizontal_align == "left":
            pos = line_start_pos.copy()
        elif horizontal_align == "middle":
            pos = [int((true_box_size[0] - total_width) / 2), line_start_pos[1]]
        elif horizontal_align == "right":
            pos = [
                true_box_size[0] + line_start_pos[0] - total_width,
                line_start_pos[1],
            ]
        for index2, y in enumerate(x):
            if vertical_align == "top":
                pos[1] = line_start_pos[1]
            elif vertical_align == "middle":
                pos[1] = line_start_pos[1] + int(
                    (max_height - pieces_sizes[index2][1]) / 2
                )
            elif vertical_align == "bottom":
                pos[1] = line_start_pos[1] + max_height - pieces_sizes[index2][1]
            using_font = ImageFont.truetype(y["fonts"], y["size"])
            draw.text(
                pos,
                y["text"],
                fill=y["color"],
                font=using_font,
                stroke_width=y["stroke_width"],
                stroke_fill=y["stroke_fill"],
            )
            pos[0] += pieces_sizes[index2][0]
        line_start_pos[1] += max_height + spacing
    if get_surplus:
        return img, surplus_text
    else:
        return img


def arrange_img(
    img_list: List[Img],
    align: Optional[
        Literal[
            "horizontal-top",
            "horizontal-middle",
            "horizontal-bottom",
            "vertical-left",
            "vertical-middle",
            "vertical-right",
        ]
    ],
    spacing: int = 0,
) -> Img:
    """
    说明：
    :param img_list:
    :param align:
    :param spacing:
    :return:
    """
    if align in [
        "horizontal-top",
        "horizontal-middle",
        "horizontal-bottom",
        "vertical-left",
        "vertical-middle",
        "vertical-right",
    ]:
        direction, side = align.split("-")
    else:
        raise ValueError("Align value Error.")
    if direction == "horizontal":
        imgReturnHeight = max([img.size[1] for img in img_list])
        imgReturnWidth = sum([img.size[0] for img in img_list]) + spacing * (
            len([img.size[0] for img in img_list]) - 1
        )
        imgReturn = ImageFactory(
            Image.new("RGBA", (imgReturnWidth, imgReturnHeight), (255, 255, 255, 0))
        )
        if side == "top":
            pos = [0, 0]
            for index, img in enumerate(img_list):
                pos[0] += imgReturn.img_paste(img, pos=tuple(pos))[1][0] + spacing
        elif side == "middle":
            pos = (0, 0)
            for index, img in enumerate(img_list):
                last_pos = pos
                align_pos = imgReturn.align_box(
                    imgReturn.boxes["self"], img, align="vertical"
                )
                pos, _ = imgReturn.img_paste(img, (last_pos[0], align_pos[1]))
                pos = (pos[0] + img.size[0] + spacing, pos[1])
        elif side == "bottom":
            bottom = imgReturn.get_size()[1]
            pos = [0, 0]
            for index, img in enumerate(img_list):
                pos[1] = bottom - img.size[1]
                pos[0] += imgReturn.img_paste(img, pos=tuple(pos))[1][0] + spacing
    elif direction == "vertical":
        imgReturnHeight = sum([img.size[1] for img in img_list]) + spacing * (
            len([img.size[0] for img in img_list]) - 1
        )
        imgReturnWidth = max([img.size[0] for img in img_list])
        imgReturn = ImageFactory(
            Image.new("RGBA", (imgReturnWidth, imgReturnHeight), (255, 255, 255, 0))
        )
        if side == "left":
            pos = [0, 0]
            for index, img in enumerate(img_list):
                pos[0] += imgReturn.img_paste(img, pos=tuple(pos))[0][1] + spacing
        elif side == "middle":
            pos = (0, 0)
            for index, img in enumerate(img_list):
                last_pos = pos
                align_pos = imgReturn.align_box(
                    imgReturn.boxes["self"], img, align="horizontal"
                )
                pos, _ = imgReturn.img_paste(img, (align_pos[0], last_pos[1]))
                pos = (pos[0], pos[1] + img.size[1] + spacing)
        elif side == "right":
            right = imgReturn.get_size()[0]
            pos = [0, 0]
            for index, img in enumerate(img_list):
                pos[0] = right - img.size[0]
                pos[1] += imgReturn.img_paste(img, pos=tuple(pos))[0][1] + spacing
    return imgReturn.img


def alpha2white(img: Img) -> Img:
    """
    说明：
        将图片透明背景转化为白色
    参数：
        :param img: Image对象
    """
    img = img.convert("RGBA")
    width, height = img.size
    for yh in range(height):
        for xw in range(width):
            dot = (xw, yh)
            color_d = img.getpixel(dot)
            if color_d[3] == 0:
                color_d = (255, 255, 255, 255)
                img.putpixel(dot, color_d)
    return img


def rgb2greyscale(img: Img) -> Img:
    """
    说明:
        将rgb色彩图片转换为灰度图片
    参数：
    :param img:
    :return:
    """
    img = img.convert("L")
    return img


# RGB格式颜色转换为16进制颜色格式
def rgb_to_hex(rgb: Union[Tuple[int, int, int], Tuple[int, int, int, int]]) -> str:
    """
    说明:
        将rgb元组转换为16进制颜色
    参数:
        :param rgb: RGB或RGBA元组
        :return: 16进制颜色字符串
    """
    RGB = rgb[:3]  # 将RGB格式划分开来
    color = "#"
    for i in RGB:
        # 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
        color += str(hex(i))[-2:].replace("x", "0").upper()
    return color


# 16进制颜色格式颜色转换为RGB格式
def hex_to_rgb(hex_color: str, alpha: int = None) -> tuple:
    """
    说明：将16进制颜色转换为RGB格式
        :param hex_color: 16进制颜色字符串
        :param alpha: 透明度
        :return: RGB或RGBA元组
    """
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    if alpha is None:
        color = (r, g, b)
    else:
        color = (r, g, b, alpha)
    return color


def img2bytes(pic: Image) -> bytes:
    """
    说明：
        PIL图片转base64
    参数：
        :param pic: 通过PIL打开的图片文件
        :return base64字符串
    """
    buf = BytesIO()
    pic.save(buf, format="PNG")
    return buf.getvalue()


def pic2b64(path: Union[str, Path]) -> str:
    """
    说明：
        图片转base64
    参数：
        :param path: 图片路径
        :return base64字符串
    """
    if type(path) is str:
        path = Path(path)
    pic_bytes = path.read_bytes()
    base64_str = base64.b64encode(pic_bytes).decode()
    return base64_str


def is_valid(file: str) -> bool:
    """
    说明：
        判断图片是否损坏
    参数：
        :param file: 图片文件路径
    """
    valid = False
    try:
        Image.open(file).load()
    except OSError:
        valid = True
    return valid


def auto_resize_text(
    text: str,
    original_size: int,
    font: str,
    limit_box: Union[Box, Tuple[int, int]],
    color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = "black",
) -> Img:
    """
    说明：
        生成自适应Box大小的文本图片
        基础是simple_text
    参数：
        :param text:
        :param original_size:
        :param font:
        :param limit_box:
        :param color:
        :return:
    """
    if isinstance(limit_box, Box):
        limit_tuple = limit_box.size
    else:
        limit_tuple = limit_box
    init_text_img = simple_text(text, original_size, font, color)
    init_size = init_text_img.size
    # 计算超出比例，超出时对应维度的radio为正
    radio_comp = tuple(map(lambda x, y: (x - y) / y, init_size, limit_tuple))
    max_radio = max(radio_comp)
    if max_radio > 0:
        img = ImageFactory(init_text_img)
        img.resize(ratio=(1 / (max_radio + 1)))
        return img.img
    else:
        return init_text_img
