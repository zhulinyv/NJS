import httpx
from bs4 import BeautifulSoup


def anne_search(name: str):
    """输入名字返回列表["""
    url = "https://sb.trygek.com/l4d_stats/ranking/search.php"
    data = {"search": name}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = httpx.post(url, data=data, headers=headers, timeout=60).content.decode(
        "utf-8"
    )
    soup = BeautifulSoup(data, "html.parser")
    # 获取标题
    title = []
    thead = soup.find("thead")
    if not thead:
        return
    for i in thead.find_all("td"):  # type: ignore
        tag = i.text.strip()
        title.append(tag)
    title.append("steamid")
    # 角色信息
    datas_table = soup.find("table")
    if not datas_table:
        return
    datas_tbody = datas_table.find("tbody")
    if not datas_tbody:
        return
    datas = datas_tbody.find_all("tr")  # type: ignore
    return [datas, title]


def name_steamid_html(name):
    """您称通过网页来返回求生steamid"""
    data_title = anne_search(name)
    if not data_title:
        return
    data = data_title[0]
    for i in data:
        onclick: str = i["onclick"]
        steamid = onclick.split("=")[2].strip("'")
        return steamid
