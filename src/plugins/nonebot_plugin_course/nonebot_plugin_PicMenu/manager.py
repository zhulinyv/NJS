import importlib
import json
from pathlib import Path
from typing import List, Tuple, Union

import nonebot.plugin
from fuzzywuzzy import fuzz, process
from nonebot import logger
from nonebot.plugin import PluginMetadata
from PIL import Image
from pydantic import error_wrappers

from .data_struct import PluginMenuData
from .template import DefaultTemplate, PicTemplate


def fuzzy_match_and_check(item: str, match_list: List[str]) -> Union[None, str]:
    """
    模糊匹配函数
    :param item: 待匹配数据
    :param match_list: 全部数据的列表
    :return: 最合适匹配结果
    """
    if item in match_list:  # 在列表中直接返回结果
        return item
    else:
        vague_result = [
            x[0]
            for x in process.extract(
                item, match_list, scorer=fuzz.partial_ratio, limit=10
            )
        ]
        vague_result = [
            x[0]
            for x in process.extract(item, vague_result, scorer=fuzz.WRatio, limit=10)
        ]
        result = list(process.extract(item, vague_result, scorer=fuzz.ratio, limit=1))[
            0
        ]
        if result[1] < 45:  # 置信度过小返回空值
            return None
        else:
            return result[0]


class DataManager(object):
    def __init__(self):
        self.plugin_menu_data_list: List[PluginMenuData] = []  # 存放menu数据的列表
        self.plugin_names: List[str] = []  # 有menu_data的插件名列表

    def load_plugin_info(self):
        def load_from_dict(_meta_data: PluginMetadata):
            self.plugin_menu_data_list.append(
                PluginMenuData(
                    name=_meta_data.name,
                    description=_meta_data.description,
                    usage=_meta_data.usage,
                    funcs=_meta_data.extra["menu_data"]
                    if "menu_data" in _meta_data.extra
                    else None,
                    template=_meta_data.extra["menu_template"]
                    if "menu_template" in _meta_data.extra
                    else "default",
                )
            )

        def load_from_json(_json_path: Path):
            menu_data_dict = json.loads(_json_path.read_text(encoding="utf-8"))
            menu_data = PluginMenuData(**menu_data_dict)
            self.plugin_menu_data_list.append(menu_data)

        for plugin in nonebot.plugin.get_loaded_plugins():
            json_path = Path(
                Path.cwd() / "data" / "menu_config" / "menus" / f"{plugin.name}.json"
            )
            if json_path.exists():
                try:
                    load_from_json(json_path)
                    logger.opt(colors=True).debug(
                        f"<y>{plugin.name}</y> 菜单数据已加载 <c>(from json)</c>"
                    )
                except json.JSONDecodeError as e:
                    logger.opt(colors=True).error(
                        f"<y>{plugin.name}</y> 菜单数据加载失败 <c>(from json)</c>\n"
                        f"<y>json解析失败</y>: {e}"
                    )
                except error_wrappers.ValidationError as e:
                    logger.opt(colors=True).error(
                        f"<y>{plugin.name}</y> 菜单数据加载失败 <c>(from json)</c>\n"
                        f"<y>json缺少必要键值对</y>: \n"
                        f"{e}"
                    )
            else:
                meta_data = plugin.metadata
                if meta_data is None:
                    continue
                else:
                    try:
                        load_from_dict(meta_data)
                        logger.opt(colors=True).debug(
                            f"<y>{plugin.name}</y> 菜单数据已加载 <c>(from code)</c>"
                        )
                    except error_wrappers.ValidationError as e:
                        logger.opt(colors=True).error(
                            f"<y>{plugin.name}</y> 菜单数据加载失败 <c>(from code)</c>\n"
                            f'<y>__plugin_meta__.extra["menu_data"] 缺少必要键值对</y>: \n'
                            f"{e}"
                        )
        self.plugin_menu_data_list.sort(key=lambda x: x.name.encode("gbk"))
        self.plugin_names = [menu_data.name for menu_data in self.plugin_menu_data_list]

    def get_main_menu_data(self) -> Tuple[List, List]:
        """
        获取生成主菜单的信息
        :return: 元组（列表[插件名]，列表[插件描述]）
        """
        descriptions = [
            menu_data.description for menu_data in self.plugin_menu_data_list
        ]
        return self.plugin_names, descriptions

    def get_plugin_menu_data(
        self, plugin_name: str
    ) -> Union[PluginMenuData, PluginMetadata, str]:
        """
        获取生成插件菜单的数据
        :param plugin_name: 插件名
        :return:
        """
        if plugin_name.isdigit():  # 判断是否为下标，是则进行下标索引，否则进行模糊匹配
            index = int(plugin_name) - 1
            if 0 <= index < len(self.plugin_menu_data_list):
                return self.plugin_menu_data_list[index]
            else:  # 超限处理
                return "PluginIndexOutRange"
        else:  # 模糊匹配
            result = fuzzy_match_and_check(plugin_name, self.plugin_names)
            # 空值返回异常字符串
            if result is None:
                return "CannotMatchPlugin"
            else:
                return next(
                    filter(lambda x: result == x.name, self.plugin_menu_data_list)
                )

    def get_command_details_data(self, plugin_data: PluginMenuData, func: str):
        """
        获取生成命令详细菜单的数据
        :param plugin_data: 插件名（从聊天中直接获得的初始数据）
        :param func: 命令（从聊天中直接获得的初始数据）
        :return:
        """
        funcs = plugin_data.funcs
        if func.isdigit():  # 判断是否为下标，是则进行下标索引，否则进行模糊匹配
            index = int(func) - 1
            if 0 <= index < len(funcs):
                return funcs[index]
            else:  # 超限处理
                return "CommandIndexOutRange"
        else:
            func_list = [func.func for func in funcs]  # 功能名的列表
            fuzzy_func = fuzzy_match_and_check(func, func_list)  # 模糊匹配
            if fuzzy_func is not None:
                return next(filter(lambda x: fuzzy_func == x.func, funcs))
            else:  # 过于模糊
                return "CannotMatchCommand"


class TemplateManager(object):
    def __init__(self):
        self.template_container = {"default": DefaultTemplate}  # 模板装载对象
        self.templates_path = Path.cwd() / "data" / "menu_config" / "template"  # 模板路径
        self.load_templates()

    def load_templates(self):  # 从文件加载模板
        template_list = [template for template in self.templates_path.glob("*.py")]
        template_name_list = [
            template.stem for template in self.templates_path.glob("*.py")
        ]
        for template_name, template_path in zip(template_name_list, template_list):
            template_spec = importlib.util.spec_from_file_location(
                template_name, template_path
            )
            template = importlib.util.module_from_spec(template_spec)
            template_spec.loader.exec_module(template)
            self.template_container.update({template_name: template.DefaultTemplate})

    def select_template(self, template_name: str) -> PicTemplate:  # 选择模板
        if template_name in self.template_container:
            return self.template_container[template_name]
        else:
            raise KeyError(f"There is no template named {template_name}")


class MenuManager(object):  # 菜单总管理
    def __init__(self):
        self.cwd = Path.cwd()
        self.config_folder_make()
        self.data_manager = DataManager()
        self.template_manager = TemplateManager()

    def load_plugin_info(self):
        self.data_manager.load_plugin_info()

    # 初始化文件结构
    def config_folder_make(self):
        if not (self.cwd / "data" / "menu_config").exists():
            (self.cwd / "data" / "menu_config").mkdir()
        if not (self.cwd / "data" / "menu_config" / "fonts").exists():
            (self.cwd / "data" / "menu_config" / "fonts").mkdir()
        if not (self.cwd / "data" / "menu_config" / "templates").exists():
            (self.cwd / "data" / "menu_config" / "templates").mkdir()
        if not (self.cwd / "data" / "menu_config" / "menus").exists():
            (self.cwd / "data" / "menu_config" / "menus").mkdir()
        if not (self.cwd / "data" / "menu_config" / "config.json").exists():
            with (self.cwd / "data" / "menu_config" / "config.json").open(
                "w", encoding="utf-8"
            ) as fp:
                fp.write(json.dumps({"default": "font_path"}))

    def generate_main_menu_image(self) -> Image.Image:  # 生成主菜单图片
        data = self.data_manager.get_main_menu_data()
        template = self.template_manager.select_template("default")
        return template().generate_main_menu(data)

    def generate_plugin_menu_image(self, plugin_name) -> Image.Image:  # 生成二级菜单图片
        init_data = self.data_manager.get_plugin_menu_data(plugin_name)
        if isinstance(init_data, str):  # 判断是否匹配到插件
            return init_data
        else:
            template = self.template_manager.select_template(init_data.template)  # 获取模板
            if init_data.funcs is not None:
                return template().generate_plugin_menu(init_data)
            else:
                return template().generate_original_plugin_menu(init_data)

    def generate_func_details_image(self, plugin_name, func) -> Image.Image:  # 生成三级菜单图片
        plugin_data = self.data_manager.get_plugin_menu_data(plugin_name)
        if isinstance(plugin_data, str):  # 判断是否匹配到插件
            return plugin_data
        else:
            if isinstance(plugin_data, PluginMetadata):
                return "PluginNoFuncData"
            init_data = self.data_manager.get_command_details_data(plugin_data, func)
        if isinstance(init_data, str):  # 判断是否匹配到功能
            return init_data
        else:
            template = self.template_manager.select_template(
                plugin_data.template
            )  # 获取模板
            return template().generate_command_details(init_data)
