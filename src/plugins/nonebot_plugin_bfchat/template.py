from pathlib import Path
import time
import json

CURRENT_FOLDER = Path(__file__).parent.resolve()
BFV_PLAYERS_DATA = CURRENT_FOLDER/'bfv_players'

BFV_BANNER = 'https://s1.ax1x.com/2022/12/14/z54oIs.jpg'

BF1_BANNER = "https://s1.ax1x.com/2022/12/15/zoMaxe.jpg"

with open(CURRENT_FOLDER/'template.html', encoding='utf-8') as f:
    MAIN_TEMPLATE = f.read()

with open(CURRENT_FOLDER/'weapon_card.html', encoding='utf-8') as f:
    WEAPON_CARD = f.read()

with open(CURRENT_FOLDER/'vehicle_card.html', encoding='utf-8') as f:
    VEHICLE_CARD = f.read()

with open(CURRENT_FOLDER/'src.js', encoding='utf-8') as f:
    SRC = f.read()

with open(CURRENT_FOLDER/'style.css', encoding='utf-8') as f:
    STYLE = f.read()

def sort_list_of_dicts(list_of_dicts, key):
    return sorted(list_of_dicts, key=lambda k: k[key], reverse=True)

def list_to_html_table(list_2d):
    html = "<table>"
    for idx,row in enumerate(list_2d):
        if idx:
            html += "<tr>"
        else:
            html += "<tr style=\"font-weight: 600;\">"
        for col in row:
            html += "<td>" + str(col) + "</td>"
        html += "</tr>"
    html += "</table>"
    return html

def get_group_list(dlist:list):
    dlist = sort_list_of_dicts(dlist,'rank')

    l = [['ID','等级','击杀数','KD','KPM','SPM','爆头率','拉人数']]
    fmt = '{0[userName]}/{0[rank]}/{0[kills]}/{0[killDeath]}/{0[killsPerMinute]}/{0[scorePerMinute]}/{0[headshots]}/{0[revives]:.0f}'
    for d in dlist:
        l.append(fmt.format(d).split('/'))
    
    return list_to_html_table(l)

def get_weapons_data(d:dict, lens:int):
    weapons_list = d['weapons']
    weapons_list = sort_list_of_dicts(weapons_list, 'kills')
    s = ''
    for w in weapons_list[:lens]:
        w['__timeEquippedHours'] = w['timeEquipped']/3600
        s += WEAPON_CARD.format(w=w)

    return s

def get_weapons_data_md(d:dict, lens:int):
    weapons_list = d['weapons']
    weapons_list = sort_list_of_dicts(weapons_list, 'kills')
    l = [['武器名称','使用时间', '击杀', 'KPM', '爆头率', '击发数', '命中数', '准度']]
    for w in weapons_list[:lens]:
        w['__timeEquippedHours'] = w['timeEquipped']/3600
        l.append([
            w['weaponName'],f"{w['__timeEquippedHours']:.1f}h",f"{w['kills']:,}",w['killsPerMinute'],w['headshots'],f"{w['shotsFired']:,}", f"{w['shotsHit']:,}",w['accuracy']
        ])

        

    return list_to_html_table(l)

def get_vehicles_data(d:dict, lens:int):
    vehicles_list = d['vehicles']
    vehicles_list = sort_list_of_dicts(vehicles_list, 'kills')
    s = ''
    for v in vehicles_list[:lens]:
        v['__timeInHour'] = v['timeIn']/3600
        s += VEHICLE_CARD.format(v=v)

    return s

def get_vehicles_data_md(d:dict, lens:int):
    vehicles_list = d['vehicles']
    vehicles_list = sort_list_of_dicts(vehicles_list, 'kills')
    l = [['载具名称','使用时间','击杀','KPM','摧毁载具数']]
    for v in vehicles_list[:lens]:
        v['__timeInHour'] = v['timeIn']/3600
        l.append([
            v['vehicleName'],f"{v['__timeInHour']:.1f}h",f"{v['kills']:,}",v['killsPerMinute'],f"{v['destroyed']:,}"
        ])


    return list_to_html_table(l)

def get_server_md(d:dict):
    d = sort_list_of_dicts(d['servers'],'playerAmount')

    l = [['','区域','服务器名称','玩家','模式','地图']]
    fmt = '<img src="{0[url]}" width=80/>|{0[region]}|{0[prefix]}|{0[playerAmount]}/{0[maxPlayers]}[{0[inQue]}]|{0[mode]}|{0[currentMap]}'
    for d in d:
        l.append(fmt.format(d).split('|'))
    
    return list_to_html_table(l)


def apply_template(d,game='bfv',prefix='/')->str:
    d['__hoursPlayed'] = d['secondsPlayed']/3600
    update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d['__update_time']))
    weapons = get_weapons_data(d,5)
    vehicles = get_vehicles_data(d,5)
    banner = BFV_BANNER if game=='bfv' else BF1_BANNER
    return MAIN_TEMPLATE.format(d=d, update_time=update_time,weapons=weapons, vehicles=vehicles, src=SRC, style=STYLE, banner=banner,game=game,prefix=prefix)
    
