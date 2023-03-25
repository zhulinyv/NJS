import abc
import json
from pathlib import Path
from typing import List, Tuple

from PIL import Image

from .data_struct import FuncData, PluginMenuData
from .img_tool import (
    Box,
    ImageFactory,
    auto_resize_text,
    calculate_text_size,
    multi_text,
    simple_text,
)


class PicTemplate(metaclass=abc.ABCMeta):  # 模板类
    def __init__(self):
        pass

    @abc.abstractmethod
    def load_resource(self):
        """
        模板文件加载抽象方法
        """
        pass

    @abc.abstractmethod
    def generate_main_menu(self, data: Tuple[List, List]) -> Image:
        """
        生成一级菜单抽象方法
        :param data: Tuple[List(插件名), List(插件des)]
        :return: Image对象
        """
        pass

    @abc.abstractmethod
    def generate_plugin_menu(self, plugin_data: PluginMenuData) -> Image:
        """
        生成二级菜单抽象方法
        :param plugin_data: PluginMenuData对象
        :return: Image对象
        """
        pass

    @abc.abstractmethod
    def generate_original_plugin_menu(self, plugin_data: PluginMenuData) -> Image:
        """
        在插件的PluginMetadata中extra无menu_data的内容时，使用该方法生成简易版图片
        :param plugin_data: PluginMetadata对象
        :return: Image对象
        """
        pass

    @abc.abstractmethod
    def generate_command_details(self, func_data: FuncData) -> Image:
        """
        生成三级级菜单抽象方法
        :param func_data: FuncData对象
        :return: Image对象
        """
        pass


class DefaultTemplate(PicTemplate):
    def __init__(self):
        super().__init__()
        self.name = "default"
        self.load_resource()
        self.colors = {
            "blue": (34, 52, 73),
            "yellow": (224, 164, 25),
            "white": (237, 239, 241),
        }
        self.basic_font_size = 25

    def load_resource(self):
        cwd = Path.cwd()
        with (cwd / "menu_config" / "config.json").open("r", encoding="utf-8") as fp:
            config = json.loads(fp.read())
        self.using_font = config["default"]

    def generate_main_menu(self, data) -> Image:
        # 列数
        column_count = len(data) + 1
        # 数据行数
        row_count = len(data[0])
        # 数据及表头尺寸测算
        row_size_list = [
            tuple(
                map(
                    lambda _x: calculate_text_size(
                        _x, self.basic_font_size, self.using_font
                    ),
                    ("序号", "插件名", "插件描述"),
                )
            )
        ]
        # 计算id，插件名，插件描述的尺寸
        for x in range(row_count):
            index_size = calculate_text_size(
                str(x + 1), self.basic_font_size, self.using_font
            )
            plugin_name_size = calculate_text_size(
                data[0][x], self.basic_font_size, self.using_font
            )
            plugin_description_size = multi_text(
                data[1][x],
                default_font=self.using_font,
                default_size=25,
                box_size=(300, 0),
            ).size
            row_size_list.append(
                (index_size, plugin_name_size, plugin_description_size)
            )
        # 单元格边距
        margin = 10
        # 确定每行的行高
        row_height_list = [
            max(map(lambda i: i[1], row_size_list[x])) + margin * 2
            for x in range(row_count + 1)
        ]
        # 确定每列的列宽
        col_max_width_tuple = (
            max((x[0][0] + margin * 2 for x in row_size_list)),
            max((x[1][0] + margin * 2 for x in row_size_list)),
            max((x[2][0] + margin * 2 for x in row_size_list)),
        )
        # 确定表格底版的长和宽
        table_width = sum(col_max_width_tuple) + 3
        table_height = sum(row_height_list) + 3
        table = ImageFactory(
            Image.new("RGBA", (table_width, table_height), self.colors["white"])
        )
        # 绘制基点和移动锚点
        initial_point, basis_point = (1, 1), [1, 1]
        # 为单元格添加box和绘制边框
        for row_id in range(row_count + 1):
            for col_id in range(column_count):
                box_size = (col_max_width_tuple[col_id], row_height_list[row_id])
                table.add_box(
                    f"box_{row_id}_{col_id}", tuple(basis_point), tuple(box_size)
                )
                table.rectangle(
                    f"box_{row_id}_{col_id}", outline=self.colors["blue"], width=2
                )
                basis_point[0] += box_size[0]
            basis_point[0] = initial_point[0]
            basis_point[1] += row_height_list[row_id]
        # 向单元格中填字
        for i, text in enumerate(("序号", "插件名", "插件描述")):
            header = simple_text(
                text, self.basic_font_size, self.using_font, self.colors["blue"]
            )
            table.img_paste(
                header,
                table.align_box(f"box_0_{i}", header, align="center"),
                isalpha=True,
            )
        for x in range(row_count):
            row_id = x + 1
            id_text = simple_text(
                str(row_id), self.basic_font_size, self.using_font, self.colors["blue"]
            )
            table.img_paste(
                id_text,
                table.align_box(f"box_{row_id}_0", id_text, align="center"),
                isalpha=True,
            )
            plugin_name_text = simple_text(
                data[0][x], self.basic_font_size, self.using_font, self.colors["blue"]
            )
            table.img_paste(
                plugin_name_text,
                table.align_box(f"box_{row_id}_1", plugin_name_text, align="center"),
                isalpha=True,
            )
            plugin_description_text = multi_text(
                data[1][x],
                box_size=(300, 0),
                default_font=self.using_font,
                default_color=self.colors["blue"],
                default_size=self.basic_font_size,
            )
            table.img_paste(
                plugin_description_text,
                table.align_box(
                    f"box_{x+1}_2", plugin_description_text, align="center"
                ),
                isalpha=True,
            )
        table_size = table.img.size
        # 添加注释
        note_basic_text = simple_text(
            "注：",
            size=self.basic_font_size,
            color=self.colors["blue"],
            font=self.using_font,
        )
        note_text = multi_text(
            "使用下方命令获取插件详情\n[菜单 <ft color=(224,164,25)>插件名称或序号</ft>]",
            box_size=(table_size[0] - 30 - note_basic_text.size[0] - 10, 0),
            default_font=self.using_font,
            default_color=self.colors["blue"],
            default_size=self.basic_font_size,
            spacing=4,
            horizontal_align="middle",
        )
        note_img = ImageFactory(
            Image.new(
                "RGBA",
                (
                    note_text.size[0] + 10 + note_basic_text.size[0],
                    max((note_text.size[1], note_basic_text.size[1])),
                ),
                self.colors["white"],
            )
        )
        note_img.img_paste(note_basic_text, (0, 0), isalpha=True)
        note_img.img_paste(note_text, (note_basic_text.size[0] + 10, 0), isalpha=True)
        main_menu = ImageFactory(
            Image.new(
                "RGBA",
                (table_size[0] + 140, table_size[1] + note_img.img.size[1] + 210),
                color=self.colors["white"],
            )
        )
        main_menu.img_paste(
            note_img.img,
            main_menu.align_box("self", table.img, pos=(0, 140), align="horizontal"),
        )
        main_menu.img_paste(
            table.img,
            main_menu.align_box(
                "self",
                table.img,
                pos=(0, 160 + note_img.img.size[1]),
                align="horizontal",
            ),
        )
        main_menu.add_box(
            "border_box",
            main_menu.align_box(
                "self",
                (table_size[0] + 40, table_size[1] + note_img.img.size[1] + 80),
                pos=(0, 100),
                align="horizontal",
            ),
            (table_size[0] + 40, table_size[1] + note_img.img.size[1] + 90),
        )
        main_menu.rectangle("border_box", outline=self.colors["blue"], width=5)
        border_box_top_left = main_menu.boxes["border_box"].topLeft
        main_menu.rectangle(
            Box((border_box_top_left[0] - 25, border_box_top_left[1] - 25), (50, 50)),
            outline=self.colors["yellow"],
            width=5,
        )
        main_menu.add_box("title_box", (0, 0), (main_menu.get_size()[0], 100))
        title = auto_resize_text(
            "插件菜单", 60, self.using_font, (table_width - 60, 66), self.colors["blue"]
        )
        main_menu.img_paste(
            title, main_menu.align_box("title_box", title, align="center"), isalpha=True
        )
        return main_menu.img

    def generate_plugin_menu(self, plugin_data: PluginMenuData) -> Image:
        plugin_name = plugin_data.name
        data = plugin_data.funcs
        column_count = 5
        row_count = len(data)
        # 数据及表头尺寸测算
        row_size_list = [
            tuple(
                map(
                    lambda _x: calculate_text_size(
                        _x, self.basic_font_size, self.using_font
                    ),
                    ("序号", "功能", "触发方式", "触发条件", "功能简述"),
                )
            )
        ]
        for index, func_data in enumerate(data):
            index_size = calculate_text_size(
                str(index + 1), self.basic_font_size, self.using_font
            )
            func_size = calculate_text_size(
                func_data.func, self.basic_font_size, self.using_font
            )
            method_size = calculate_text_size(
                func_data.trigger_method, self.basic_font_size, self.using_font
            )
            condition_size = calculate_text_size(
                func_data.trigger_condition, self.basic_font_size, self.using_font
            )
            brief_des_size = multi_text(
                func_data.brief_des,
                default_font=self.using_font,
                default_size=25,
                box_size=(300, 0),
            ).size
            row_size_list.append(
                (index_size, func_size, method_size, condition_size, brief_des_size)
            )
        # 边距
        margin = 10
        # 测行高
        row_height_list = [
            max(map(lambda i: i[1], row_size_list[x])) + margin * 2
            for x in range(row_count + 1)
        ]
        col_max_width_tuple = (
            max((x[0][0] + margin * 2 for x in row_size_list)),
            max((x[1][0] + margin * 2 for x in row_size_list)),
            max((x[2][0] + margin * 2 for x in row_size_list)),
            max((x[3][0] + margin * 2 for x in row_size_list)),
            max((x[4][0] + margin * 2 for x in row_size_list)),
        )
        # 建立表格画板
        table_width = sum(col_max_width_tuple) + 3
        table_height = sum(row_height_list) + 3
        table = ImageFactory(
            Image.new("RGBA", (table_width, table_height), self.colors["white"])
        )
        initial_point, basis_point = (1, 1), [1, 1]
        # 建立基准box
        for row_id in range(row_count + 1):
            for col_id in range(column_count):
                box_size = (col_max_width_tuple[col_id], row_height_list[row_id])
                table.add_box(
                    f"box_{row_id}_{col_id}", tuple(basis_point), tuple(box_size)
                )
                table.rectangle(
                    f"box_{row_id}_{col_id}", outline=self.colors["blue"], width=2
                )
                basis_point[0] += box_size[0]
            basis_point[0] = initial_point[0]
            basis_point[1] += row_height_list[row_id]
        # 向单元格中填字
        for i, text in enumerate(("序号", "功能", "触发方式", "触发条件", "功能简述")):
            header = simple_text(
                text, self.basic_font_size, self.using_font, self.colors["blue"]
            )
            table.img_paste(
                header,
                table.align_box(f"box_0_{i}", header, align="center"),
                isalpha=True,
            )
        # 填字
        for index, func_data in enumerate(data):
            row_id = index + 1
            # 第一个cell填id
            id_text = simple_text(
                str(row_id), self.basic_font_size, self.using_font, self.colors["blue"]
            )
            table.img_paste(
                id_text,
                table.align_box(f"box_{row_id}_0", id_text, align="center"),
                isalpha=True,
            )
            # 第二个cell里填func（功能）
            func_text = simple_text(
                func_data.func,
                self.basic_font_size,
                self.using_font,
                self.colors["blue"],
            )
            table.img_paste(
                func_text,
                table.align_box(f"box_{row_id}_1", func_text, align="center"),
                isalpha=True,
            )
            # 第三个cell里填trigger_method（触发方式）
            trigger_method_text = simple_text(
                func_data.trigger_method,
                self.basic_font_size,
                self.using_font,
                self.colors["blue"],
            )
            table.img_paste(
                trigger_method_text,
                table.align_box(f"box_{row_id}_2", trigger_method_text, align="center"),
                isalpha=True,
            )
            # 第四个cell里填trigger_condition（触发条件）
            trigger_condition_text = simple_text(
                func_data.trigger_condition,
                self.basic_font_size,
                self.using_font,
                self.colors["blue"],
            )
            table.img_paste(
                trigger_condition_text,
                table.align_box(
                    f"box_{row_id}_3", trigger_condition_text, align="center"
                ),
                isalpha=True,
            )
            # 第五个cell里填brief_des（功能简述）
            brief_des_text = multi_text(
                func_data.brief_des,
                box_size=(300, 0),
                default_font=self.using_font,
                default_color=self.colors["blue"],
                default_size=self.basic_font_size,
            )
            table.img_paste(
                brief_des_text,
                table.align_box(f"box_{row_id}_4", brief_des_text, align="center"),
                isalpha=True,
            )
        # 获取table尺寸
        table_size = table.img.size
        # 用法
        usage_basic_text = simple_text(
            "用法：",
            size=self.basic_font_size,
            color=self.colors["blue"],
            font=self.using_font,
        )
        usage_text = multi_text(
            plugin_data.usage or "无",
            box_size=(table_size[0] - 30 - usage_basic_text.size[0] - 10, 0),
            default_font=self.using_font,
            default_color=self.colors["blue"],
            default_size=self.basic_font_size,
        )
        # 提示
        tip_basic_text = simple_text(
            "提示：",
            size=self.basic_font_size,
            color=self.colors["blue"],
            font=self.using_font,
        )
        tip_text = multi_text(
            (
                "使用下方命令获取插件功能详情\n"
                f"[菜单 {plugin_data.name} <ft color=(224,164,25)>功能名称或序号</ft>]"
            ),
            box_size=(table_size[0] - 30 - tip_basic_text.size[0] - 10, 0),
            default_font=self.using_font,
            default_color=self.colors["blue"],
            default_size=self.basic_font_size,
        )
        # 合成usage文字图片
        usage_img = ImageFactory(
            Image.new(
                "RGBA",
                (
                    max(
                        usage_text.size[0] + 10 + usage_basic_text.size[0],
                        tip_text.size[0] + 10 + tip_basic_text.size[0],
                    ),
                    usage_text.size[1] + 20 + tip_text.size[1],
                ),
                self.colors["white"],
            )
        )
        # 用法
        usage_img.img_paste(usage_basic_text, (0, 0), isalpha=True)
        usage_img.img_paste(
            usage_text, (usage_basic_text.size[0] + 10, 0), isalpha=True
        )
        # 提示
        usage_img.img_paste(tip_basic_text, (0, usage_text.size[1] + 20), isalpha=True)
        usage_img.img_paste(
            tip_text,
            (tip_basic_text.size[0] + 10, usage_text.size[1] + 20),
            isalpha=True,
        )
        usage_text_size = usage_img.img.size
        # 底部画板，大小根据table大小和usage文字大小确定
        main_menu = ImageFactory(
            Image.new(
                "RGBA",
                (table_size[0] + 140, table_size[1] + usage_text_size[1] + 210),
                color=self.colors["white"],
            )
        )
        # 在底部画板上粘贴usage
        pos, a = main_menu.img_paste(
            usage_img.img,
            main_menu.align_box(
                "self", usage_img.img, pos=(0, 130), align="horizontal"
            ),
            isalpha=True,
        )
        # 在底部画板上粘贴表格
        main_menu.img_paste(
            table.img,
            main_menu.align_box(
                "self",
                table.img,
                pos=(0, pos[1] + usage_text_size[1] + 20),
                align="horizontal",
            ),
        )
        # 给表格添加装饰性边框
        main_menu.add_box(
            "border_box",
            main_menu.align_box(
                "self",
                (table_size[0] + 40, table_size[1] + 70),
                pos=(0, 100),
                align="horizontal",
            ),
            (table_size[0] + 40, table_size[1] + usage_text_size[1] + 70),
        )
        main_menu.rectangle("border_box", outline=self.colors["blue"], width=5)
        border_box_top_left = main_menu.boxes["border_box"].topLeft
        main_menu.rectangle(
            Box((border_box_top_left[0] - 25, border_box_top_left[1] - 25), (50, 50)),
            outline=self.colors["yellow"],
            width=5,
        )
        main_menu.add_box("title_box", (0, 0), (main_menu.get_size()[0], 100))
        # 添加插件名title
        title = auto_resize_text(
            plugin_name,
            60,
            self.using_font,
            (table_width - 60, 66),
            self.colors["blue"],
        )
        main_menu.img_paste(
            title, main_menu.align_box("title_box", title, align="center"), isalpha=True
        )
        return main_menu.img

    def generate_original_plugin_menu(self, plugin_data: PluginMenuData) -> Image:
        usage_basic_text = simple_text(
            "用法：",
            size=self.basic_font_size,
            color=self.colors["blue"],
            font=self.using_font,
        )
        usage_text = multi_text(
            plugin_data.usage,
            box_size=(600, 0),
            default_font=self.using_font,
            default_color=self.colors["blue"],
            default_size=self.basic_font_size,
        )
        # 合成usage文字图片
        usage_img = ImageFactory(
            Image.new(
                "RGBA",
                (
                    usage_text.size[0] + 10 + usage_basic_text.size[0],
                    max((usage_text.size[1], usage_basic_text.size[1])),
                ),
                self.colors["white"],
            )
        )
        usage_img.img_paste(usage_basic_text, (0, 0), isalpha=True)
        usage_img.img_paste(
            usage_text, (usage_basic_text.size[0] + 10, 0), isalpha=True
        )
        usage_text_size = usage_img.img.size
        # 主画布
        main_menu = ImageFactory(
            Image.new(
                "RGBA",
                (usage_text_size[0] + 140, usage_text_size[1] + 210),
                color=self.colors["white"],
            )
        )
        # 添加边框Box
        main_menu.add_box(
            "border_box",
            main_menu.align_box(
                "self",
                (usage_text_size[0] + 60, usage_text_size[1] + 70),
                pos=(0, 100),
                align="horizontal",
            ),
            (usage_text_size[0] + 70, usage_text_size[1] + 70),
        )
        # 粘贴usage文字图片
        main_menu.img_paste(
            usage_img.img,
            main_menu.align_box("border_box", usage_img.img, align="center"),
            isalpha=True,
        )
        # 添加装饰性边框
        main_menu.rectangle("border_box", outline=self.colors["blue"], width=5)
        border_box_top_left = main_menu.boxes["border_box"].topLeft
        main_menu.rectangle(
            Box((border_box_top_left[0] - 25, border_box_top_left[1] - 25), (50, 50)),
            outline=self.colors["yellow"],
            width=5,
        )
        main_menu.add_box("title_box", (0, 0), (main_menu.get_size()[0], 100))
        # 添加插件名title
        title = auto_resize_text(
            plugin_data.name,
            60,
            self.using_font,
            (usage_text_size[0] - 40, 66),
            self.colors["blue"],
        )
        main_menu.img_paste(
            title, main_menu.align_box("title_box", title, align="center"), isalpha=True
        )
        return main_menu.img

    def generate_command_details(self, func_data: FuncData) -> Image:
        # 需要生成的列表
        string_list = [
            func_data.func,
            func_data.trigger_method,
            func_data.trigger_condition,
            func_data.detail_des,
        ]
        # 获取标签文字
        basis_text_list = [
            simple_text(
                text, self.basic_font_size, self.using_font, self.colors["blue"]
            )
            for text in ["功能：", "触发方式：", "触发条件：", "详细描述："]
        ]
        # 获取标签文字的大小
        basis_text_size_list = [x.size for x in basis_text_list]
        # 信息起始位置
        info_text_start_x = max([x[0] for x in basis_text_size_list])
        # 将文字转换为图片
        text_img_list = []
        for x in string_list:
            text_img_list.append(
                multi_text(
                    x,
                    box_size=(680 - info_text_start_x, 0),
                    default_font=self.using_font,
                    default_color=self.colors["blue"],
                    default_size=self.basic_font_size,
                    v_border_ignore=True,
                )
            )
        # 获取文字图片的大小
        text_size_list = [x.size for x in text_img_list]
        # 获取同一行最大高度
        line_max_height_list = [
            max(x)
            for x in zip(
                map(lambda y: y[1], text_size_list),
                map(lambda y: y[1], basis_text_size_list),
            )
        ]
        # 文字画板，每行间距30
        text_img = ImageFactory(
            Image.new(
                "RGBA",
                (
                    info_text_start_x + 40 + text_img_list[0].size[0],
                    sum(line_max_height_list) + 90,
                ),
                color=self.colors["white"],
            )
        )
        # - 添加func的box
        text_img.add_box(
            "func_box",
            (0, 0),
            (680, max((basis_text_size_list[0][1], text_size_list[0][1]))),
        )
        # 粘贴func标签
        pos, _ = text_img.img_paste(
            basis_text_list[0],
            text_img.align_box("func_box", basis_text_list[0]),
            isalpha=True,
        )
        # 粘贴func图片
        text_img.img_paste(
            text_img_list[0],
            text_img.align_box(
                "func_box", text_img_list[0], pos=(info_text_start_x + 40, pos[1])
            ),
            isalpha=True,
        )
        # - 添加trigger_method的box
        text_img.add_box(
            "trigger_method_box",
            (0, text_img.boxes["func_box"].bottom + 30),
            (680, max((basis_text_size_list[1][1], text_size_list[1][1]))),
        )
        # 粘贴trigger_method标签
        pos, _ = text_img.img_paste(
            basis_text_list[1],
            text_img.align_box("trigger_method_box", basis_text_list[1]),
            isalpha=True,
        )
        # 粘贴trigger_method图片
        text_img.img_paste(
            text_img_list[1],
            text_img.align_box(
                "trigger_method_box",
                text_img_list[1],
                pos=(info_text_start_x + 40, pos[1]),
            ),
            isalpha=True,
        )
        # - 添加trigger_condition的box
        text_img.add_box(
            "trigger_condition_box",
            (0, text_img.boxes["trigger_method_box"].bottom + 30),
            (680, max((basis_text_size_list[2][1], text_size_list[2][1]))),
        )
        # 粘贴trigger_condition标签
        pos, _ = text_img.img_paste(
            basis_text_list[2],
            text_img.align_box("trigger_condition_box", basis_text_list[2]),
            isalpha=True,
        )
        # 粘贴trigger_condition图片
        text_img.img_paste(
            text_img_list[2],
            text_img.align_box(
                "trigger_condition_box",
                text_img_list[2],
                pos=(info_text_start_x + 40, pos[1]),
            ),
            isalpha=True,
        )
        # - 添加detail_des的box
        text_img.add_box(
            "detail_des_box",
            (0, text_img.boxes["trigger_condition_box"].bottom + 30),
            (680, max((basis_text_size_list[3][1], text_size_list[3][1]))),
        )
        # 粘贴detail_des标签
        pos, _ = text_img.img_paste(
            basis_text_list[3],
            text_img.align_box("detail_des_box", basis_text_list[3]),
            isalpha=True,
        )
        # 粘贴detail_des图片
        text_img.img_paste(
            text_img_list[3],
            text_img.align_box(
                "detail_des_box", text_img_list[3], pos=(info_text_start_x + 40, pos[1])
            ),
            isalpha=True,
        )
        text_img_size = text_img.img.size
        detail_img = ImageFactory(
            Image.new("RGBA", (800, text_img_size[1] + 180), color=self.colors["white"])
        )
        detail_img.add_box("text_border_box", (20, 100), (760, text_img_size[1] + 60))
        detail_img.rectangle("text_border_box", outline=self.colors["blue"], width=1)
        detail_img.img_paste(
            text_img.img,
            detail_img.align_box("text_border_box", text_img.img, align="center"),
        )
        detail_img.add_box("upper_box", (0, 0), (800, 100))
        detail_img.add_box(
            "blue_box",
            detail_img.align_box("upper_box", (700, 20), align="center"),
            (700, 20),
        )
        detail_img.rectangle("blue_box", outline=self.colors["blue"], width=5)
        detail_img.add_box(
            "yellow_box",
            (
                detail_img.boxes["blue_box"].left - 25,
                detail_img.boxes["blue_box"].top - 15,
            ),
            (50, 50),
        )
        detail_img.rectangle("yellow_box", outline=self.colors["yellow"], width=5)
        return detail_img.img
