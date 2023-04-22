from typing import Dict

import httpx

from .manager import plugin_manager


# 获取商店插件列表
def __get_store_plugin_list() -> dict:
    return {
        plugin["module_name"]: plugin
        for plugin in httpx.get(
            "https://cdn.jsdelivr.net/gh/nonebot/nonebot2/website/static/plugins.json"
        ).json()
    }


def get_store_plugin_list() -> Dict[str, bool]:
    plugin_list = plugin_manager.get_plugin()
    return {plugin: plugin in plugin_list for plugin in __get_store_plugin_list()}


def get_plugin_info(plugin: str) -> str:
    store_plugin_list = __get_store_plugin_list()
    if plugin in store_plugin_list:
        plugin = store_plugin_list[plugin]
        return (
            f"ID: {plugin['module_name']}\n"
            f"Name: {plugin['name']}\n"
            f"Description: {plugin['desc']}\n"
            f"Latest Version: {httpx.get('https://pypi.org/pypi/'+plugin['project_link']+'/json').json()['info']['version']}\n"
            f"Author: {plugin['author']}\n"
            f"HomePage: {plugin['homepage']}"
        )
    else:
        return "查无此插件！"
