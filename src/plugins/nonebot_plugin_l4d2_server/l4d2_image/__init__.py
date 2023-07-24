from typing import List, Optional

import jinja2
from bs4 import BeautifulSoup
from nonebot.log import logger
from nonebot_plugin_htmlrender import html_to_pic

# from .htmlimg import dict_to_dict_img
# from ..l4d2_anne.anne_telecom import ANNE_API
from ..l4d2_utils.config import TEXT_PATH, l4_config
from .download import get_head_by_user_id_and_save
from .send_image_tool import convert_img

template_path = TEXT_PATH / "template"

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)


async def out_png(usr_id, data_dict: dict):
    """使用html来生成图片"""

    with open((template_path / "anne.html"), "r", encoding="utf-8") as file:
        data_html = file.read()
    # content = template.render_async()
    soup = BeautifulSoup(data_html, "html.parser")
    msg_dict = await dict_to_html(usr_id, data_dict, soup)
    template = env.get_template("anne.html")
    html = await template.render_async(data=msg_dict)
    pic = await html_to_pic(
        html,
        wait=0,
        viewport={"width": 1100, "height": 800},
        template_path=f"file://{template_path.absolute()}",
    )
    return pic


async def dict_to_html(usr_id, DETAIL_MAP: dict, soup: BeautifulSoup):
    """输入qq、字典，获取新的msg替换html"""
    DETAIL_right = {}
    DETAIL_right["name"] = DETAIL_MAP["Steam 名字:"]
    DETAIL_right["Steam_ID"] = DETAIL_MAP["Steam ID:"]
    DETAIL_right["play_time"] = DETAIL_MAP["游玩时间:"]
    DETAIL_right["last_online"] = DETAIL_MAP["最后上线:"]
    DETAIL_right["rank"] = DETAIL_MAP["排行:"]
    DETAIL_right["points"] = DETAIL_MAP["分数:"]
    DETAIL_right["point_min"] = DETAIL_MAP["每分钟获取分数:"]
    DETAIL_right["killed"] = DETAIL_MAP["感染者消灭:"]
    DETAIL_right["shut"] = DETAIL_MAP["爆头:"]
    DETAIL_right["out"] = DETAIL_MAP["爆头率:"]
    DETAIL_right["playtimes"] = DETAIL_MAP["游玩地图数量:"]
    DETAIL_right["url"] = DETAIL_MAP["个人资料"]
    DETAIL_right["one_msg"] = DETAIL_MAP["一言"]
    DETAIL_right["last_one"] = DETAIL_MAP["救援关"]
    # html_text = soup.prettify()
    # for key, value in DETAIL_right.items():
    #     html_text = html_text.replace(key,value)
    # 头像
    temp = await get_head_by_user_id_and_save(usr_id)
    # temp = await get_head_steam_and_save(usr_id,DETAIL_right['url'])
    if not temp:
        return
    res = await convert_img(temp, is_base64=True)
    DETAIL_right["header"] = f"data:image/png;base64,{res}"
    data_list: List[dict] = [DETAIL_right]
    return data_list


async def server_ip_pic(msg_list: List[dict]):
    """
    输入一个字典列表，输出图片
    msg_dict:folder/name/map_/players/max_players/Players/[Name]
    """
    for server_info in msg_list:
        server_info[
            "max_players"
        ] = f"{server_info['players']}/{server_info['max_players']}"
        players_list = []
        if "Players" in server_info:
            sorted_players = sorted(
                server_info["Players"], key=lambda x: x.get("Score", 0), reverse=True
            )[:4]
            for player_info in sorted_players:
                player_str = f"{player_info['name']} | {player_info['Duration']}"
                players_list.append(player_str)
            while len(players_list) < 4:
                players_list.append("")
            server_info["Players"] = players_list
    pic = await get_help_img(msg_list)
    if pic:
        logger.success("正在输出图片")
    else:
        logger.warning("我的图图呢")
    return pic


async def get_help_img(plugins: List[dict]) -> Optional[bytes]:
    try:
        if l4_config.l4_style == "black":
            template = env.get_template("help_dack.html")
        else:
            template = env.get_template("help.html")
        content = await template.render_async(plugins=plugins)
        return await html_to_pic(
            content,
            wait=0,
            viewport={"width": 100, "height": 100},
            template_path=f"file://{template_path.absolute()}",
        )
    except Exception as e:
        logger.warning(f"Error in get_help_img: {e}")
        return None
