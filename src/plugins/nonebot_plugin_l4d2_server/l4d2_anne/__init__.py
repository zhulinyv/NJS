from typing import List

import pandas as pd
from nonebot.log import logger

from ..l4d2_data.players import L4D2Player
from ..l4d2_image import out_png
from ..l4d2_utils.seach import *
from .analysis import df_to_guoguanlv

# from .anne_telecom import ANNE_API


s = L4D2Player()


async def anne_html(name: str):
    """搜索里提取玩家信息，返回列表字典"""
    data_title = anne_search(name)
    if not data_title:
        return
    data = data_title[0]
    title = data_title[1]
    if len(data) == 0 or data[0] == "No Player found.":
        return []
    data_list: list = []
    logger.info(data)
    for i in data:
        i: BeautifulSoup
        try:
            Rank = i.find("td", {"data-title": "Rank:"}).text.strip()  # type: ignore
            player = i.find("td", {"data-title": "Player:"}).text.strip()  # type: ignore
            points = i.find("td", {"data-title": "Points:"}).text.strip()  # type: ignore
            # country = i.find('img')['alt']
            playtime = i.find("td", {"data-title": "Playtime:"}).text.strip()  # type: ignore
            last_online = i.find("td", {"data-title": "Last Online:"}).text.strip()  # type: ignore
        except AttributeError:
            Rank = i.find("td", {"data-title": "排名:"}).text.strip()  # type: ignore
            player = i.find("td", {"data-title": "玩家:"}).text.strip()  # type: ignore
            points = i.find("td", {"data-title": "分数:"}).text.strip()  # type: ignore
            playtime = i.find("td", {"data-title": "游玩时间:"}).text.strip()  # type: ignore
            last_online = i.find("td", {"data-title": "最后上线时间:"}).text.strip()  # type: ignore
        onclick = i["onclick"]
        steamid = onclick.split("=")[2].strip("'")  # type: ignore
        play_json = {
            title[0]: Rank,
            title[1]: player,
            title[2]: points,
            # title[3]:country,
            title[3]: playtime,
            title[4]: last_online,
            title[5]: steamid,
        }
        data_list.append(play_json)
    logger.info("搜寻数据")
    return data_list


def anne_html_msg(data_list: list):
    """从搜索结果的字典列表中，返回发送信息"""
    mes = "搜索到以下玩家信息"
    ns = 0

    for one in data_list:
        one: dict
        ns += 1
        x = 6

        titles = list(one.keys())
        for i in range(x):
            mes += "\n" + titles[i] + ":" + str(one[titles[i]])
        mes += "\n--------------------"
        if ns > 4:
            break
    return mes


async def write_player(id, msg: str, nickname: str):
    """绑定用户"""
    # 判断是steam
    if msg.startswith("STEAM"):
        # try:
        data_tuple = s._query_player_qq(id)
        if data_tuple != None:
            qq, nicknam, steamid = data_tuple
        else:
            nicknam = None
        await s._add_player_all(id, nicknam, msg)
        # except TypeError:
        # await s._add_player_steamid(id , msg)
        mes = "绑定成功喵~\nQQ:" + nickname + "\n" + "steamid:" + msg
        return mes
    else:
        # try:
        data_tuple = s._query_player_qq(id)
        if data_tuple != None:
            id, nicknam, steamid = data_tuple
        else:
            steamid = None
        await s._add_player_all(id, msg, steamid)
        # except TypeError:
        #     await s._add_player_nickname(id , msg )
        mes = "绑定成功喵~\nQQ:" + nickname + "\n" + "steam昵称:" + msg
        return mes


def del_player(id: str):
    """删除绑定信息,返回消息"""
    if not s._query_player_qq(id):
        return "你还没有绑定过，请使用[求生绑定+昵称/steamid]"
    if s._delete_player:
        return "删除成功喵~"


async def id_to_mes(name: str):
    """根据name从数据库,返回steamid、或者空白"""
    data_tuple = await s.search_data(None, name, None)
    if data_tuple:
        steamid = data_tuple[2]
        return steamid
    return None


def anne_rank_dict(name: str):
    """用steamid,查详情,输出字典"""
    data_dict = {}
    url = f"https://sb.trygek.com/l4d_stats/ranking/player.php?steamid={name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
    }
    data = httpx.get(url=url, headers=headers, timeout=5)
    if data.status_code != 200:
        return [f"查询错误，状态码{data.status_code}"]
    data = data.content.decode("utf-8")
    data = BeautifulSoup(data, "html.parser")
    detail = data.find_all("table")
    n = 0
    data_list: List[dict] = []
    while n < 2:
        detail2 = detail[n]
        tr = detail2.find_all("tr")
        for i in tr:
            title = i.find("td", {"class": "w-50"})
            value = title.find_next_sibling("td")
            new_dict = {title.text: value.text}
            data_dict.update(new_dict)
        data_list.append(data_dict)
        n += 1
    # 获取头像
    element: str = data.find_all(attrs={"style": "cursor:pointer"})[0].get("onclick")
    player_url = element.split("'")[1]
    data_list[0].update({"个人资料": player_url})
    # 获取一言
    message = data.select(
        "html body div.content.text-center.text-md-left div.container.text-left div.col-md-12.h-100 div.card-body.worldmap.d-flex.flex-column.justify-content-center.text-center span"
    )
    msg_list = []
    for i in message:
        msg_list.append(i.text)
    data_list[0].update({"一言": msg_list})
    return data_list


def anne_rank_dict_msg(data_list):
    """字典转msg"""
    msg = ""
    for data_dict in data_list:
        mes = ""
        for i in data_dict:
            mes += "\n" + i + data_dict[i]
        mes += "\n--------------------"
        msg += mes
    return msg


async def anne_message(name: str, usr_id: str):
    """获取anne信息可输出信息"""
    if name:
        logger.info("关键词查询" + name)
        if not name.startswith("STEAM"):
            steamid = await id_to_mes(name)
            if not steamid:
                logger.info("没有找到qq，使用默认头像")
                message = await anne_html(name)
                if not message:
                    return
                usr_id = "1145149191810"
                if len(message) == 0:
                    return "没有叫这个名字的...\n"
                if len(message) > 1:
                    return anne_html_msg(message)
                name = message[0]["steamid"]
            else:
                name = steamid

        # steamid
        msg = anne_rank_dict(name)[0]
        if isinstance(msg, dict):
            msg.update(await df_to_guoguanlv(await anne_map_msg(name)))
            logger.info("使用图片")
            msg = await out_png(usr_id, msg)
        return msg
    else:
        """
        1、qq>数据>没有数据，返回
        2、qq>数据>steamid>查询
        3、qq>数据>昵称>查询
        """
        logger.info("qq信息查询")
        data_tuple = s._query_player_qq(usr_id)
        logger.info(data_tuple)
        if not data_tuple:
            return f"没有绑定信息...请使用【求生绑定 xxx】\n"
        # 只有名字，先查询数据在判断
        elif data_tuple[2]:
            name = data_tuple[2]
        elif data_tuple[1]:
            name = await id_to_mes(data_tuple[1])  # type: ignore
            logger.info(name)
            if not name:
                message = await anne_html(data_tuple[1])
                if not message:
                    return
                usr_id = "1145149191810"
                if len(message) == 0:
                    return "没有叫这个名字的...\n"
                if len(message) > 1:
                    return anne_html_msg(message)
                name = message[0]["steamid"]

        # name是steamid
        msg = anne_rank_dict(name)[0]
        if isinstance(msg, dict):
            msg.update(await df_to_guoguanlv(await anne_map_msg(name)))
            logger.info("使用图片")
            msg = await out_png(usr_id, msg)
        return msg


async def anne_map_msg(steamid: str):
    """steamid->地图信息"""
    url = f"https://sb.trygek.com/l4d_stats/ranking/timedmaps.php?steamid={steamid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
    }
    data = httpx.get(url, headers=headers, timeout=5).content.decode("utf-8")
    soup = BeautifulSoup(data, "html.parser")
    data_list = []
    cards = soup.select("div.card.rounded-0")
    for card in cards:
        tbodies = card.select("tbody")
        for tbody in tbodies:
            rows = [td.text.strip() for td in tbody.find_all("td")]
            for i in range(0, len(rows), 9):
                row = rows[i : i + 9]
                data_list.append(row)
    df = pd.DataFrame(
        data_list,
        columns=["游戏模式", "地图", "难度", "完成时间", "特感数量", "刷新间隔", "B数使用", "刷特模式", "Anne版本"],
    )
    return df
