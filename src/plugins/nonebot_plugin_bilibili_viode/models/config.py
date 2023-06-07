from pydantic import BaseModel


class _BaseItem(BaseModel):
    """
    基础配置项
    """
    visible: bool = False  # 是否显示
    x: int = 0  # X轴坐标
    y: int = 0  # Y轴坐标


class ImageItem(_BaseItem):
    """
    图片
    """
    path: str = None  # 图片路径
    color: str = None  # 图片颜色
    width: int = None  # 图片宽度
    height: int = None  # 图片高度
    radius: int = None  # 图片圆角半径


class TextItem(_BaseItem):
    """
    文本
    """
    font: str = "Arial"  # 字体
    font_size: int = 12  # 字体大小
    font_color: str = "#000000"  # 字体颜色
    font_max_width: int = None  # 单行最大宽度
    font_max_lines: int = 1  # 最大行数
