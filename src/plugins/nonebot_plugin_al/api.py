import aiohttp
import json
import random
from random import choice
import aiofiles
from bs4 import BeautifulSoup
from typing import Optional

from .utils import *



from .name import *

async def get_data(url:str ,mode:Optional[str] = None):
    """获取网页内容"""
    headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=600) as response:
            if response.status == 200:
                if mode == "html":
                    html = await response.text()  # 获取网页源代码
                    soup = BeautifulSoup(html, 'html.parser')  # 创建BeautifulSoup对象
                    return soup
                elif mode == "str":
                    return await response.text()
                else:
                    return await response.read()
            else:
                return None
            
        



async def get_ship_id_by_name(name):
    async with aiofiles.open(DATA_PATH.joinpath('azurapi_data', 'ships.json'),mode='r',encoding='utf-8'
                             )as load_f:
        load_dict = await load_f.read()
        load_dict = await str_to_json(load_dict)
        id = None

        for result in load_dict:
            if str(result['names']['cn']) == str(name):
                id = (result['id'])
            else:
                continue
    return id


"""
方法名：get_ship_data_by_name
参数：name(string)
返回值：result(字典)
说明：该方法作用是通过碧蓝航线api，用舰船名称获取舰船数据，返回一个数据字典供html适配数据调用
"""


async def get_ship_data_by_name(name):
    async with aiofiles.open(DATA_PATH.joinpath('azurapi_data', 'ships.json'),mode='r',encoding='utf-8'
                             )as load_f:
        load_dict = await load_f.read()
        load_dict = await str_to_json(load_dict)
    for result in load_dict:
        if str(result['names']['cn']) == str(name):
            return result
        else:
            continue
    return None


"""
方法名：get_ship_data_by_id
参数：name(string)
返回值：result(字典)
说明：该方法作用是通过碧蓝航线api，用舰船id获取舰船数据，返回一个数据字典供html适配数据调用
"""

async def get_ship_data_by_id(id):
    async with aiofiles.open(DATA_PATH.joinpath('azurapi_data', 'ships.json'),mode='r',encoding='utf-8'
                             )as load_f:
        load_dict = await load_f.read()
        load_dict = await str_to_json(load_dict)
    for result in load_dict:
        if str(result['id']) == str(id):
            return result
        else:
            continue
    return None
"""
方法名：format_data_into_html
参数：data(字典)
返回值：无
说明：该方法作用是通过传入的舰船数据字典，用beautifulsoup适配数据到html
"""


async def format_data_into_html(data):
    # 读入html备用
    soup = BeautifulSoup(open(DATA_PATH.joinpath('ship_html', 'ship_temp.html'), encoding='UTF-8'), "lxml")
    # 读入bwiki数据
    with open('test.json','w') as f:
        json.dump(data,f, ensure_ascii=True,indent=4)
    async with aiofiles.open(DATA_PATH.joinpath('ship_html', 'ships_plus.json'),mode='r',encoding='utf-8'
                            )as load_f:
        load_dict = await load_f.read()
        load_dict = await str_to_json(load_dict)
    data_plus = {}
    try:
        for i in range(0, len(load_dict)):
            if str(data['id']) == str(load_dict[i]['编号']):
                data_plus = load_dict[i]
                break
    except:
        pass

    # 船名
    try:
        ship_name = str(data['names']['code']) + "【" + str(data['names']['cn']) + "】"
    except:
        ship_name = str(data['names'])
    soup.find(id='ship_name').string = ship_name

    # 头像 avatar = "<img src='" + str(data['thumbnail']) + "'/>"
    # soup.find(id='avatar').img.replace_with(soup.new_tag("img", src=str(data['thumbnail']).replace(
    #     "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")))
    soup.find(id='avatar').img.replace_with(soup.new_tag("img", src="images/Texture2D/" + await get_ship_id_by_name(str(data['names']['cn'])) + '.png'))

    # 建造时长
    building_time = str(data['construction']['constructionTime'])
    soup.find(id='building_time').string = building_time

    # id
    id = str(data['id'])
    soup.find(id='id').string = id

    # 稀有度
    rarity = str(data['rarity'])
    if rarity == 'Priority':
        # rarity = "<img src='rate_icon/75px-Priority.png'/><br/>最高方案★★★★★★"
        soup.find(id='rarity').string = ''
        soup.find(id='rarity').append(soup.new_tag("img", src="rate_icon/75px-Priority.png"))
        soup.find(id='rarity')['style'] = "background-color:PaleGoldenrod"
        soup.find(id='avatar')['style'] = "background-color:PaleGoldenrod"
        soup.find(id='rarity').append(soup.new_tag("br"))
        soup.find(id='rarity').append("最高方案★★★★★★")
    if rarity == 'Decisive':
        # rarity = "<img src='rate_icon/50px-Decisive.png'/><br/>决战方案★★★★★★"
        soup.find(id='rarity').string = ''
        soup.find(id='rarity').append(soup.new_tag("img", src="rate_icon/50px-Decisive.png"))
        soup.find(id='rarity')['style'] = "background-image:url('rate_icon/UR_BG.png')"
        soup.find(id='avatar')['style'] = "background-image:url('rate_icon/UR_BG.png')"
        soup.find(id='rarity').append(soup.new_tag("br"))
        soup.find(id='rarity').append("决战方案★★★★★★")
    if rarity == 'Elite':
        # rarity = "<img src='rate_icon/50px-Elite.png'/><br/>精锐★★★★★"
        soup.find(id='rarity').string = ''
        soup.find(id='rarity').append(soup.new_tag("img", src="rate_icon/50px-Elite.png"))
        soup.find(id='rarity')['style'] = "background-color:Plum"
        soup.find(id='avatar')['style'] = "background-color:Plum"
        soup.find(id='rarity').append(soup.new_tag("br"))
        soup.find(id='rarity').append("精锐★★★★★")
    if rarity == 'Super Rare':
        # rarity = "<img src='rate_icon/50px-SuperRare.png'/><br/>超稀有★★★★★★"
        soup.find(id='rarity').string = ''
        soup.find(id='rarity').append(soup.new_tag("img", src="rate_icon/50px-SuperRare.png"))
        soup.find(id='rarity')['style'] = "background-color:PaleGoldenrod"
        soup.find(id='avatar')['style'] = "background-color:PaleGoldenrod"
        soup.find(id='rarity').append(soup.new_tag("br"))
        soup.find(id='rarity').append("超稀有★★★★★★")
    if rarity == 'Ultra Rare':
        # rarity = "<img src='rate_icon/50px-UltraRare.png'/><br/>海上传奇★★★★★★"
        soup.find(id='rarity').string = ''
        soup.find(id='rarity').append(soup.new_tag("img", src="rate_icon/50px-UltraRare.png"))
        soup.find(id='rarity').append(soup.new_tag("br"))
        soup.find(id='rarity')['style'] = "background-image:url('rate_icon/UR_BG.png')"
        soup.find(id='avatar')['style'] = "background-image:url('rate_icon/UR_BG.png');"
        soup.find(id='rarity').append("海上传奇★★★★★★")
    if rarity == 'Rare':
        # rarity = "<img src='rate_icon/50px-Rare.png'/><br/>稀有★★★★★"
        soup.find(id='rarity').string = ''
        soup.find(id='rarity').append(soup.new_tag("img", src="rate_icon/50px-Rare.png"))
        soup.find(id='rarity')['style'] = "background-color:PowderBlue"
        soup.find(id='avatar')['style'] = "background-color:PowderBlue"
        soup.find(id='rarity').append(soup.new_tag("br"))
        soup.find(id='rarity').append("稀有★★★★★")
    if rarity == 'Normal':
        rarity = "<img src='rate_icon/50px-Rarity_Normal.png'/><br/>普通★★★★"
        soup.find(id='rarity').string = ''
        soup.find(id='rarity').append(soup.new_tag("img", src="rate_icon/50px-Rarity_Normal.png"))
        soup.find(id='rarity')['style'] = "background-color:Gainsboro"
        soup.find(id='avatar')['style'] = "background-color:Gainsboro"
        soup.find(id='rarity').append(soup.new_tag("br"))
        soup.find(id='rarity').append("普通★★★★")
    # 阵营
    faction = str(data['nationality'])
    if faction == 'Sakura Empire':
        # faction = "<img src='faction_icon/50px-Jp_1.png'/>重樱"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Jp_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("重樱")
    if faction == 'Universal':
        # faction = "<img src='faction_icon/50px-Cm_1.png'/>突破材料"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Cm_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("突破材料")
    if faction == 'Eagle Union':
        # faction = "<img src='faction_icon/50px-Us_1.png'/>白鹰"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Us_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("白鹰")
    if faction == 'Royal Navy':
        # faction = "<img src='faction_icon/50px-En_1.png'/>皇家"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-En_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("皇家")
    if faction == 'Venus Vacation':
        # faction = "<img src='faction_icon/50px-Um_1.png'/>沙滩排球"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("沙滩排球")
    if faction == 'Iron Blood':
        # faction = "<img src='faction_icon/50px-De_1.png'/>铁血"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-De_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("铁血")
    if faction == 'Dragon Empery':
        # faction = "<img src='faction_icon/50px-Cn_1.png'/>东煌"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Cn_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("东煌")
    if faction == 'Vichya Dominion':
        # faction = "<img src='faction_icon/50px-Vf_1.png'/>维希教廷"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Vf_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("维希教廷")
    if faction == 'Sardegna Empire':
        # faction = "<img src='faction_icon/50px-Rn_1.png'/>撒丁帝国"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Rn_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("撒丁帝国")
    if faction == 'Bilibili':
        # faction = "<img src='faction_icon/50px-Bi_1.png'/>哔哩哔哩"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Bi_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("哔哩哔哩")
    if faction == 'Utawarerumono':
        # faction = "<img src='faction_icon/50px-Um_1.png'/>传颂之物"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("传颂之物")
    if faction == 'Northern Parliament':
        # faction = "<img src='faction_icon/50px-Northunion_orig.png'/>北方联合"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Northunion_orig.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("北方联合")
    if faction == 'META':
        # faction = "<img src='faction_icon/50px-Meta_1.png'/>META"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Meta_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("META")
    if faction == 'Neptunia':
        # faction = "<img src='faction_icon/50px-Np_1.png'/>海王星"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Np_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("海王星")
    if faction == 'Hololive':
        # faction = "<img src='faction_icon/50px-Um_1.png'/>Hololive"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("Hololive")
    if faction == 'KizunaAI':
        # faction = "<img src='faction_icon/50px-Um_1.png'/>KizunaAI"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("KizunaAI")
    if faction == 'The Idolmaster':
        faction = "<img src='faction_icon/50px-Um_1.png'/>偶像大师"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("偶像大师")
    if faction == 'Iris Libre':
        faction = "<img src='faction_icon/50px-Ff_1.png'/>自由鸢尾"
        soup.find(id='faction').string = ''
        soup.find(id='faction').append(soup.new_tag("img", src="faction_icon/50px-Ff_1.png"))
        soup.find(id='faction').append(soup.new_tag("br"))
        soup.find(id='faction').append("自由鸢尾")
    # 舰种舰级
    class_ = str(data['class'])
    soup.find(id='class').string = class_
    type = str(data['hullType'])
    retrofitHullType = None
    if 'retrofitHullType' in data:
        retrofitHullType = translate_ship_type(str(data['retrofitHullType']))
    if type == 'Aircraft Carrier':
        # type = "<img src='type_icon/30px-CV_img40.png'/> 航空母舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-CV_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("航空母舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Destroyer' and str(data['id']) != '472':
        # type = "<img src='type_icon/30px-DD_img40.png'/> 驱逐舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-DD_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("驱逐舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Light Cruiser':
        # type = "<img src='type_icon/30px-CL_img40.png'/> 轻型巡洋舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-CL_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("轻型巡洋舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Heavy Cruiser':
        # type = "<img src='type_icon/30px-CA_img40.png'/> 重型巡洋舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-CA_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("重型巡洋舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Battleship':
        # type = "<img src='type_icon/30px-BB_img40.png'/> 战列舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-BB_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("战列舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Light Carrier':
        # type = "<img src='type_icon/30px-CVL_img40.png'/> 轻型航空母舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-CVL_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("轻型航空母舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Repair':
        # type = "<img src='type_icon/30px-AR_img40.png'/> 维修舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-AR_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("维修舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Battlecruiser':
        # type = "<img src='type_icon/30px-BC_img40.png'/> 战列巡洋舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-BC_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("战列巡洋舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Monitor':
        # type = "<img src='type_icon/30px-BM_img40.png'/> 浅水重炮舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-BM_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("浅水重炮舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Submarine':
        # type = "<img src='type_icon/30px-SS_img40.png'/> 潜艇"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-SS_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("潜艇")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Submarine Carrier':
        # type = "<img src='type_icon/30px-SSV_img40.png'/> 潜水母舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-SSV_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("潜水母舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Munition Ship' or str(data['id']) == '472':
        # type = "<img src='type_icon/30px-AE_img40.png'/> 运输舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-AE_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("运输舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Large Cruiser':
        # type = "<img src='type_icon/30px-CB_img40.png'/> 超级巡洋舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-CB_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("超级巡洋舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    if type == 'Aviation Battleship':
        # type = "<img src='type_icon/30px-BBV_img40.png'/> 航空战列舰"
        soup.find(id='type').string = ''
        soup.find(id='type').append(soup.new_tag("img", src="type_icon/30px-BBV_img40.png"))
        soup.find(id='type').append(soup.new_tag("br"))
        soup.find(id='type').append("航空战列舰")
        if retrofitHullType is not None:
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append("改")
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(
                soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
            soup.find(id='type').append(soup.new_tag("br"))
            soup.find(id='type').append(str(retrofitHullType[0]))
    # 性格
    character = str(data_plus.get('性格',''))
    soup.find(id='character').string = character
    # 身份
    who = str(data_plus.get('身份',''))
    soup.find(id='who').string = who
    # 关键词
    keyword = str(data_plus.get('关键词',''))
    soup.find(id='keyword').string = keyword
    # 持有物
    holdings = str(data_plus.get('持有物',''))
    soup.find(id='holdings').string = holdings
    # 发色瞳色
    hair = str(data_plus.get('发色',''))
    eyes = str(data_plus.get('瞳色',''))
    soup.find(id='hair_eyes').string = hair
    soup.find(id='hair_eyes').append(soup.new_tag('br'))
    soup.find(id="hair_eyes").append(eyes)
    # 萌点
    adorable = str(data_plus.get('萌点',''))
    soup.find(id='adorable').string = adorable
    # 评价
    if '评价' in data_plus:
        appraise = str(data_plus['评价'])
        soup.find(id='appraise_content').string = appraise
    else:
        soup.find(id='appraise_content').string = "暂无评价"

    # 备注
    if '备注' in data_plus:
        memo = str(data_plus['备注'])
        soup.find(id='memo_content').string = memo
    else:
        soup.find(id='memo_content').string = "暂无备注"

    # 声优和画师
    artist = str(data['misc']['artist']['name'])
    soup.find(id='artist').string = artist
    if data['misc']['voice'] is not None:
        cv = str(data['misc']['voice']['name'])
        soup.find(id='cv').string = cv
    else:
        soup.find(id='cv').string = '暂无'

    # 120级满破数据
    duration_120 = str(data['stats']['level120']['health'])  # HP
    soup.find(id='duration-120').string = duration_120
    armor_120 = str(data['stats']['level120']['armor'])  # 装甲
    if armor_120 == 'Heavy':
        soup.find(id='armor-120').string = '重型'
    if armor_120 == 'Light':
        soup.find(id='armor-120').string = '轻型'
    if armor_120 == 'Medium':
        soup.find(id='armor-120').string = '中型'
    refill_120 = str(data['stats']['level120']['reload'])  # 装填
    soup.find(id='refill-120').string = refill_120
    luck_120 = str(data['stats']['level120']['luck'])  # 幸运
    soup.find(id='luck-120').string = luck_120
    firepower_120 = str(data['stats']['level120']['firepower'])  # 炮击
    soup.find(id='firepower-120').string = firepower_120
    torpedo_120 = str(data['stats']['level120']['torpedo'])  # 雷击
    soup.find(id='torpedo-120').string = torpedo_120
    evasion_120 = str(data['stats']['level120']['evasion'])  # 机动
    soup.find(id='evasion-120').string = evasion_120
    speed_120 = str(data['stats']['level120']['speed'])  # 航速
    soup.find(id='speed-120').string = speed_120
    antiAir_120 = str(data['stats']['level120']['antiair'])  # 防空
    soup.find(id='antiAir-120').string = antiAir_120
    aviation_120 = str(data['stats']['level120']['aviation'])  # 航空
    soup.find(id='aviation-120').string = aviation_120
    consumption_120 = str(data['stats']['level120']['oilConsumption'])  # 油耗
    soup.find(id='consumption-120').string = consumption_120
    hit_120 = str(data['stats']['level120']['accuracy'])  # 命中
    soup.find(id='hit-120').string = hit_120
    asw_120 = str(data['stats']['level120']['antisubmarineWarfare'])  # 反潜
    soup.find(id='asw-120').string = asw_120

    # 100级满破数据
    duration_100 = str(data['stats']['level100']['health'])
    soup.find(id='duration-100').string = duration_100
    armor_100 = str(data['stats']['level100']['armor'])
    if armor_100 == 'Heavy':
        soup.find(id='armor-100').string = '重型'
    if armor_100 == 'Light':
        soup.find(id='armor-100').string = '轻型'
    if armor_100 == 'Medium':
        soup.find(id='armor-100').string = '中型'
    refill_100 = str(data['stats']['level100']['reload'])
    soup.find(id='refill-100').string = refill_100
    luck_100 = str(data['stats']['level100']['luck'])
    soup.find(id='luck-100').string = luck_100
    firepower_100 = str(data['stats']['level100']['firepower'])
    soup.find(id='firepower-100').string = firepower_100
    torpedo_100 = str(data['stats']['level100']['torpedo'])
    soup.find(id='torpedo-100').string = torpedo_100
    evasion_100 = str(data['stats']['level100']['evasion'])
    soup.find(id='evasion-100').string = evasion_100
    speed_100 = str(data['stats']['level100']['speed'])
    soup.find(id='speed-100').string = speed_100
    antiAir_100 = str(data['stats']['level100']['antiair'])
    soup.find(id='antiAir-100').string = antiAir_100
    aviation_100 = str(data['stats']['level100']['aviation'])
    soup.find(id='aviation-100').string = aviation_100
    consumption_100 = str(data['stats']['level100']['oilConsumption'])
    soup.find(id='consumption-100').string = consumption_100
    hit_100 = str(data['stats']['level100']['accuracy'])
    soup.find(id='hit-100').string = hit_100
    asw_100 = str(data['stats']['level100']['antisubmarineWarfare'])
    soup.find(id='asw-100').string = asw_100
    # 基础数据
    duration = str(data['stats']['baseStats']['health'])
    soup.find(id='duration-1').string = duration
    armor = str(data['stats']['baseStats']['armor'])
    if armor == 'Heavy':
        soup.find(id='armor-1').string = '重型'
    if armor == 'Light':
        soup.find(id='armor-1').string = '轻型'
    if armor == 'Medium':
        soup.find(id='armor-1').string = '中型'
    refill = str(data['stats']['baseStats']['reload'])
    soup.find(id='refill-1').string = refill
    luck = str(data['stats']['baseStats']['luck'])
    soup.find(id='luck-1').string = luck
    firepower = str(data['stats']['baseStats']['firepower'])
    soup.find(id='firepower-1').string = firepower
    torpedo = str(data['stats']['baseStats']['torpedo'])
    soup.find(id='torpedo-1').string = torpedo
    evasion = str(data['stats']['baseStats']['evasion'])
    soup.find(id='evasion-1').string = evasion
    speed = str(data['stats']['baseStats']['speed'])
    soup.find(id='speed-1').string = speed
    antiAir = str(data['stats']['baseStats']['antiair'])
    soup.find(id='antiAir-1').string = antiAir
    aviation = str(data['stats']['baseStats']['aviation'])
    soup.find(id='aviation-1').string = aviation
    consumption = str(data['stats']['baseStats']['oilConsumption'])
    soup.find(id='consumption-1').string = consumption
    hit = str(data['stats']['baseStats']['accuracy'])
    soup.find(id='hit-1').string = hit
    asw = str(data['stats']['baseStats']['antisubmarineWarfare'])
    soup.find(id='asw-1').string = asw

    # 1号栏武器装备
    slots_1_efficiency = str(data['slots'][0]['minEfficiency']) + "% → " + str(data['slots'][0]['maxEfficiency']) + "%"
    soup.find(id='slots_1_efficiency').string = slots_1_efficiency
    slots_1_equippable = str(data_plus.get('武器装备',[{}])[0].get('类型',str(data['slots'][0]['type'])))  # str(data['slots'][0]['type'])
    soup.find(id='slots_1_equippable').string = slots_1_equippable
    slots_1_max = str(data['slots'][0]['max'])
    soup.find(id='slots_1_max').string = slots_1_max

    # 2号栏武器装备
    slots_2_efficiency = str(data['slots'][1]['minEfficiency']) + "% → " + str(data['slots'][1]['maxEfficiency']) + "%"
    soup.find(id='slots_2_efficiency').string = slots_2_efficiency
    slots_2_equippable = str(data_plus.get('武器装备',[{},{}])[1].get('类型',str(data['slots'][1]['type'])))  # str(data['slots'][1]['type'])
    soup.find(id='slots_2_equippable').string = slots_2_equippable
    slots_2_max = str(data['slots'][1]['max'])
    soup.find(id='slots_2_max').string = slots_2_max

    # 3号栏武器装备
    slots_3_efficiency = str(data['slots'][2]['minEfficiency']) + "% → " + str(data['slots'][2]['maxEfficiency']) + "%"
    soup.find(id='slots_3_efficiency').string = slots_3_efficiency
    slots_3_equippable = str(data_plus.get('武器装备',[{},{},{}])[2].get('类型',str(data['slots'][2]['type'])))  # str(data['slots'][2]['type'])
    soup.find(id='slots_3_equippable').string = slots_3_equippable
    slots_3_max = str(data['slots'][2]['max'])
    soup.find(id='slots_3_max').string = slots_3_max

    # 技能,各船技能数量不同，所以先返回数组再迭代处理
    skills = data['skills']
    skill_text = ''
    soup.find(id='skill').clear()
    try:
        for i in range(0, len(skills)):
            skill_text += ("<tr><td ><img src='" + str(skills[i]['icon']).replace(
                "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "") \
                           + "' width='60px' height='60px'/>" + str(skills[i]['names']['cn']) \
                           + "</td></tr><tr><td>" + str(data_plus.get('技能', [{},{},{},{},{},{}])[i].get('效果',str(skills[i]['description']))) + "</td></tr>")  # 被逼无奈只能这样
    except:
        pass
    extraSoup = BeautifulSoup(skill_text, "lxml")
    soup.find(id='skill').append(extraSoup)

    # 突破,更恶心，二维数组,布里，科研船，普通船都不一样
    breaks = data.get("limitBreaks", -1)
    soup.find(id='break').string = ''
    if breaks is not None and breaks != -1:
        breaks_tr_body = ''
        break_text = []
        break_1 = break_2 = break_3 = str_1 = str_2 = str_3 = ''
        for break_ in breaks[0]:
            str_1 += ("" + str(break_) + "<br>")
        break_1 = ("" + str(data_plus.get('突破',[{},{}])[1].get('一阶',str_1)).replace('/', '<br>●'))
        break_text.append(break_1)
        for break_ in breaks[1]:
            str_2 += ("" + str(break_) + "<br>")
        break_2 = ("●" + str(data_plus.get('突破',[{},{},{}])[2].get('二阶',str_2)).replace('/', '<br>●'))
        break_text.append(break_2)
        for break_ in breaks[2]:
            str_3 += ("" + str(break_) + "<br>")
        break_3 = ("●" + str(data_plus.get('突破',[{},{},{},{}])[3].get('三阶',str_3)).replace('/', '<br>●'))
        break_text.append(break_3)
        for i in range(0, 3):
            breaks_tr_body += (
                    "<tr><th colspan='1' scope='col' width='100px'>" + str(i) + "破</th><td colspan='2'>" + str(
                break_text[i]) + "</td></tr>")
        breaksoup = BeautifulSoup(breaks_tr_body, 'lxml')
        soup.find(id='break').append(breaksoup)

    elif breaks == -1:
        breaks = data["devLevels"]  # 数组
        breaks_tr_body = ''
        break_text = []
        break_1 = break_2 = break_3 = break_4 = break_5 = break_6 = str_1 = str_2 = str_3 = str_4 = str_5 = str_6=''
        for break_ in breaks[0]['buffs']:
            str_1 += ("●" + str(break_) + "<br>")
        break_1 = ("●" + str(data_plus.get('突破',[{},{},{}])[2].get('5级',str_1)).replace('/', '<br>●'))
        break_text.append(break_1)
        for break_ in breaks[1]['buffs']:
            str_2 += ("●" + str(break_) + "<br>")
        break_2 = ("●" + str(data_plus.get('突破',[{},{},{},{}])[3].get('10级',str_2)).replace('/', '<br>●'))
        break_text.append(break_2)
        for break_ in breaks[2]['buffs']:
            str_3 += ("●" + str(break_) + "<br>")
        break_3 = ("●" + str(data_plus.get('突破',[{},{},{},{},{}])[4].get('15级',str_3)).replace('/', '<br>●'))
        break_text.append(break_3)
        for break_ in breaks[3]['buffs']:
            str_4 += ("●" + str(break_) + "<br>")
        break_4 = ("●" + str(data_plus.get('突破',[{},{},{},{},{},{}])[5].get('20级',str_4)).replace('/', '<br>●'))
        break_text.append(break_4)
        for break_ in breaks[4]['buffs']:
            str_5 += ("●" + str(break_) + "<br>")
        break_5 = ("●" + str(data_plus.get('突破',[{},{},{},{},{},{},{}])[6].get('25级',str_5)).replace('/', '<br>●'))
        break_text.append(break_5)
        for break_ in breaks[5]['buffs']:
            str_6 += ("●" + str(break_) + "<br>")
        break_6 = ("●" + str(data_plus.get('突破',[{},{},{},{},{},{},{},{}])[7].get('30级',str_6)).replace('/', '<br>●'))
        break_text.append(break_6)
        for i in range(0, 6):
            breaks_tr_body += (
                    "<tr><th colspan='1' scope='col' width='100px'>科研" + str(
                (i + 1) * 5) + "级</th><td colspan='2'>" + str(break_text[i]) + "</td></tr>")
        breaksoup = BeautifulSoup(breaks_tr_body, "html.parser")
        soup.find(id='break').append(breaksoup)
    else:
        new_tag = soup.new_tag("td")
        new_tag.string = '不可突破'
        soup.find(id='break').append(new_tag)

    # 科技点
    # collection = "<img src='res_icon/25px-TechPoint.png'/>" + str(data['fleetTech']['techPoints']['collection'])
    soup.find(id='collection').string = ''
    soup.find(id='collection').append(soup.new_tag('img', src='res_icon/25px-TechPoint.png'))
    soup.find(id='collection').append(str(data['fleetTech']['techPoints']['collection']))
    # maxLB = "<img src='res_icon/25px-TechPoint.png'/>" + str(data['fleetTech']['techPoints']['maxLimitBreak'])
    soup.find(id='maxLB').string = ''
    soup.find(id='maxLB').append(soup.new_tag('img', src='res_icon/25px-TechPoint.png'))
    soup.find(id='maxLB').append(str(data['fleetTech']['techPoints']['maxLimitBreak']))
    # lv120 = "<img src='res_icon/25px-TechPoint.png'/>" + str(data['fleetTech']['techPoints']['maxLevel'])
    soup.find(id='lv120').string = ''
    soup.find(id='lv120').append(soup.new_tag('img', src='res_icon/25px-TechPoint.png'))
    soup.find(id='lv120').append(str(data['fleetTech']['techPoints']['maxLevel']))
    # total = "<img src='res_icon/25px-TechPoint.png'/>" + str(data['fleetTech']['techPoints']['total'])
    soup.find(id='total').string = ''
    soup.find(id='total').append(soup.new_tag('img', src='res_icon/25px-TechPoint.png'))
    soup.find(id='total').append(str(data['fleetTech']['techPoints']['total']))
    # 退役，有的船不能退役,能退役的就三种返现：油，钱，章
    scrapValues = data['scrapValue']
    coin = ""
    oil = ""
    medal = ""
    if scrapValues is not None:
        # 退役不再返油
        coin = str(data['scrapValue']['coin'])
        soup.find(id='coin').string = coin
        # oil = str(data['scrapValue']['oil'])
        soup.find(id='oil').string = oil
        medal = str(data['scrapValue']['medal'])
        soup.find(id='medal').string = medal
    else:
        soup.find(id='coin').string = soup.find(id='oil').string = soup.find(id='medal').string = "不可食用"

    # 皮肤列表
    skin_list = data['skins']  # 数组
    skin_text = ''
    soup.find(id='skin_list').string = ""
    for skin in skin_list:
        if skin['name'] == "Default" or skin['name'] == "Original Art":
            continue
        else:
            try:
                live2d = ''
                if skin['info']['live2dModel'] == True:
                    live2d = "是"
                else:
                    live2d = "否"
                if skin['name'] == "Retrofit":
                    skin_text += (
                            "<tr><th  scope='col' width='100px'>名称</th><td>" + "改造" + "</td><th  scope='col'width='100px'>Live2D</th><td>" + live2d + "</td></tr>")

                skin_text += ("<tr><th  scope='col' width='100px'>名称</th><td>" + str(skin['info'][
                                                                                        'cnClient']) + "</td><th  scope='col'width='100px'>Live2D</th><td>" + live2d + "</td></tr>")
            except:
                continue
    extraSoup = BeautifulSoup(skin_text, "lxml")
    soup.find(id='skin_list').append(extraSoup)

    # 处理完毕，保存

    async with aiofiles.open(DATA_PATH.joinpath('ship_html', 'ship_info.html'),
              'w', encoding="utf-8") as fp:
        await fp.write(str(soup.prettify()))

    if 'retrofitHullType' in data:
        # 读入html备用
        retrofit_soup = BeautifulSoup(
            open(DATA_PATH.joinpath('ship_html', 'ship_retrofit_temp.html'),
                 encoding='UTF-8'),
            "lxml")
        retrofit_soup.find(id='ship_name').string = ship_name
        retrofit_soup.find(id='id').string = id
        if faction == 'Sakura Empire':
            # faction = "<img src='faction_icon/50px-Jp_1.png'/>重樱"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Jp_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("重樱")
        if faction == 'Universal':
            # faction = "<img src='faction_icon/50px-Cm_1.png'/>突破材料"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Cm_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("突破材料")
        if faction == 'Eagle Union':
            # faction = "<img src='faction_icon/50px-Us_1.png'/>白鹰"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Us_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("白鹰")
        if faction == 'Royal Navy':
            # faction = "<img src='faction_icon/50px-En_1.png'/>皇家"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-En_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("皇家")
        if faction == 'Venus Vacation':
            # faction = "<img src='faction_icon/50px-Um_1.png'/>沙滩排球"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("沙滩排球")
        if faction == 'Iron Blood':
            # faction = "<img src='faction_icon/50px-De_1.png'/>铁血"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-De_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("铁血")
        if faction == 'Dragon Empery':
            # faction = "<img src='faction_icon/50px-Cn_1.png'/>东煌"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Cn_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("东煌")
        if faction == 'Vichya Dominion':
            # faction = "<img src='faction_icon/50px-Vf_1.png'/>维希教廷"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Vf_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("维希教廷")
        if faction == 'Sardegna Empire':
            # faction = "<img src='faction_icon/50px-Rn_1.png'/>撒丁帝国"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Rn_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("撒丁帝国")
        if faction == 'Bilibili':
            # faction = "<img src='faction_icon/50px-Bi_1.png'/>哔哩哔哩"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Bi_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("哔哩哔哩")
        if faction == 'Utawarerumono':
            # faction = "<img src='faction_icon/50px-Um_1.png'/>传颂之物"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("传颂之物")
        if faction == 'Northern Parliament':
            # faction = "<img src='faction_icon/50px-Northunion_orig.png'/>北方联合"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Northunion_orig.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("北方联合")
        if faction == 'META':
            # faction = "<img src='faction_icon/50px-Meta_1.png'/>META"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Meta_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("META")
        if faction == 'Neptunia':
            # faction = "<img src='faction_icon/50px-Np_1.png'/>海王星"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Np_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("海王星")
        if faction == 'Hololive':
            # faction = "<img src='faction_icon/50px-Um_1.png'/>Hololive"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("Hololive")
        if faction == 'KizunaAI':
            # faction = "<img src='faction_icon/50px-Um_1.png'/>KizunaAI"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("KizunaAI")
        if faction == 'The Idolmaster':
            faction = "<img src='faction_icon/50px-Um_1.png'/>偶像大师"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Um_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("偶像大师")
        if faction == 'Iris Libre':
            faction = "<img src='faction_icon/50px-Ff_1.png'/>自由鸢尾"
            retrofit_soup.find(id='faction').string = ''
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("img", src="faction_icon/50px-Ff_1.png"))
            retrofit_soup.find(id='faction').append(retrofit_soup.new_tag("br"))
            retrofit_soup.find(id='faction').append("自由鸢尾")

        # 120级满破改造数据
        duration_120_r = str(data['stats']['level120Retrofit']['health'])  # HP
        retrofit_soup.find(id='duration-120').string = duration_120_r
        armor_120_r = str(data['stats']['level120Retrofit']['armor'])  # 装甲
        if armor_120_r == 'Heavy':
            retrofit_soup.find(id='armor-120').string = '重型'
        if armor_120_r == 'Light':
            retrofit_soup.find(id='armor-120').string = '轻型'
        if armor_120_r == 'Medium':
            retrofit_soup.find(id='armor-120').string = '中型'
        refill_120_r = str(data['stats']['level120Retrofit']['reload'])  # 装填
        retrofit_soup.find(id='refill-120').string = refill_120_r
        luck_120_r = str(data['stats']['level120Retrofit']['luck'])  # 幸运
        retrofit_soup.find(id='luck-120').string = luck_120_r
        firepower_120_r = str(data['stats']['level120Retrofit']['firepower'])  # 炮击
        retrofit_soup.find(id='firepower-120').string = firepower_120_r
        torpedo_120_r = str(data['stats']['level120Retrofit']['torpedo'])  # 雷击
        retrofit_soup.find(id='torpedo-120').string = torpedo_120_r
        evasion_120_r = str(data['stats']['level120Retrofit']['evasion'])  # 机动
        retrofit_soup.find(id='evasion-120').string = evasion_120_r
        speed_120_r = str(data['stats']['level120Retrofit']['speed'])  # 航速
        retrofit_soup.find(id='speed-120').string = speed_120_r
        antiAir_120_r = str(data['stats']['level120Retrofit']['antiair'])  # 防空
        retrofit_soup.find(id='antiAir-120').string = antiAir_120_r
        aviation_120_r = str(data['stats']['level120Retrofit']['aviation'])  # 航空
        retrofit_soup.find(id='aviation-120').string = aviation_120_r
        consumption_120_r = str(data['stats']['level120Retrofit']['oilConsumption'])  # 油耗
        retrofit_soup.find(id='consumption-120').string = consumption_120_r
        hit_120_r = str(data['stats']['level120Retrofit']['accuracy'])  # 命中
        retrofit_soup.find(id='hit-120').string = hit_120_r
        asw_120_r = str(data['stats']['level120Retrofit']['antisubmarineWarfare'])  # 反潜
        retrofit_soup.find(id='asw-120').string = asw_120_r

        # 100级满破改造数据
        duration_100_r = str(data['stats']['level100Retrofit']['health'])
        retrofit_soup.find(id='duration-100').string = duration_100_r
        armor_100_r = str(data['stats']['level100Retrofit']['armor'])
        if armor_100_r == 'Heavy':
            retrofit_soup.find(id='armor-100').string = '重型'
        if armor_100_r == 'Light':
            retrofit_soup.find(id='armor-100').string = '轻型'
        if armor_100_r == 'Medium':
            retrofit_soup.find(id='armor-100').string = '中型'
        refill_100_r = str(data['stats']['level100Retrofit']['reload'])
        retrofit_soup.find(id='refill-100').string = refill_100_r
        luck_100_r = str(data['stats']['level100Retrofit']['luck'])
        retrofit_soup.find(id='luck-100').string = luck_100_r
        firepower_100_r = str(data['stats']['level100Retrofit']['firepower'])
        retrofit_soup.find(id='firepower-100').string = firepower_100_r
        torpedo_100_r = str(data['stats']['level100Retrofit']['torpedo'])
        retrofit_soup.find(id='torpedo-100').string = torpedo_100_r
        evasion_100_r = str(data['stats']['level100Retrofit']['evasion'])
        retrofit_soup.find(id='evasion-100').string = evasion_100_r
        speed_100_r = str(data['stats']['level100Retrofit']['speed'])
        retrofit_soup.find(id='speed-100').string = speed_100_r
        antiAir_100_r = str(data['stats']['level100Retrofit']['antiair'])
        retrofit_soup.find(id='antiAir-100').string = antiAir_100_r
        aviation_100_r = str(data['stats']['level100Retrofit']['aviation'])
        retrofit_soup.find(id='aviation-100').string = aviation_100_r
        consumption_100_r = str(data['stats']['level100Retrofit']['oilConsumption'])
        retrofit_soup.find(id='consumption-100').string = consumption_100_r
        hit_100_r = str(data['stats']['level100Retrofit']['accuracy'])
        retrofit_soup.find(id='hit-100').string = hit_100_r
        asw_100_r = str(data['stats']['level100Retrofit']['antisubmarineWarfare'])
        retrofit_soup.find(id='asw-100').string = asw_100_r
        retrofit_soup.find(id='type').string = ''
        retrofit_soup.find(id='type').append(
            retrofit_soup.new_tag("img", src="type_icon/30px-" + str(retrofitHullType[1]) + "_img40.png"))
        retrofit_soup.find(id='type').append(retrofit_soup.new_tag("br"))
        retrofit_soup.find(id='type').append(str(retrofitHullType[0]))

        retrofit_soup.find(id='avatar').img.replace_with(retrofit_soup.new_tag("img", src="images/Texture2D/" + pinyin(
            str(data['names']['cn']).replace("·", "").replace("-", "").replace(" ", "").replace(".", "")) + '_g.png'))
        async with aiofiles.open(DATA_PATH.joinpath('ship_html', 'ship_retrofit.html'),
                  'w', encoding="utf-8") as fp:
            await fp.write(str(retrofit_soup.prettify()))
        return 1  # 1可以改造，就去适配改造数据
    else:
        return 0  # 0不可以改造，就跳过

"""
方法名：get_ship_skin_by_name
参数：ship_name(string),skin_name(string),if_chibi(string)
返回值：0 / 1
说明：该方法作用是通过碧蓝航线api，用舰船名称获取舰船皮肤数据，再调用openCV把图片合成，供机器人发送 ,成功0 失败1
"""


async def get_ship_skin_by_id(id, skin_name):
    soup = BeautifulSoup(
        open(DATA_PATH.joinpath('ship_html', 'ship_skin.html'),
             encoding='UTF-8'),
        "lxml")
    result = await get_ship_data_by_id(str(id))
    ship_skin_list = result['skins']
    image_path = ''
    background_path = ''
    chibi_path = ''
    # 处理原皮
    if skin_name == '原皮':
        # image_path = str(ship_skin_list[0]['image']).replace(
        #     "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "data/al/ship_html/")
        # background_path = str(ship_skin_list[0]['background']).replace(
        #     "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "data/al/ship_html/")
        # chibi_path = str(ship_skin_list[0]['chibi']).replace(
        #     "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "data/al/ship_html/")
        # 在线
        image_path = str(ship_skin_list[0]['image']).replace(
            "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", 
            "https://ghproxy.com/https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/")
        background_path = str(ship_skin_list[0]['background']).replace(
            "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", 
            "https://ghproxy.com/https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/")
        chibi_path = str(ship_skin_list[0]['chibi']).replace(
            "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", 
            "https://ghproxy.com/https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/")

        soup.find(id='img-content')['style'] = "background-image: url('" + background_path + "')"
        soup.find(id='img-content').string = ''
        soup.find(id='img-content').append(soup.new_tag('img', src=image_path, style="height: 720px"))
        soup.find(id='img-content').append(
            soup.new_tag('img', src=chibi_path, style="position: fixed;bottom: 0;left: 0;"))
        DATA_PATH.joinpath('ship_html', 'ship_skin.html')
        async with aiofiles.open(DATA_PATH.joinpath('ship_html', 'ship_skin.html'),
                  'w', encoding="utf-8") as fp:
            await fp.write(str(soup.prettify()))
        return 0

    if len(ship_skin_list) < 2:
        return 1
    # 处理婚纱
    if skin_name == '婚纱':
        for skin in ship_skin_list:
            if skin['name'] == 'Wedding':
                image_path = str(skin['image']).replace(
                    "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
                background_path = str(skin['background']).replace(
                    "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
                chibi_path = str(skin['chibi']).replace(
                    "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
                soup.find(id='img-content')['style'] = "background-image: url('" + background_path + "')"
                soup.find(id='img-content').string = ''
                soup.find(id='img-content').append(soup.new_tag('img', src=image_path, style="height: 720px"))
                soup.find(id='img-content').append(
                    soup.new_tag('img', src=chibi_path, style="position: fixed;bottom: 0;left: 0;"))

                async with aiofiles.open(DATA_PATH.joinpath('ship_html', 'ship_skin.html'),
                          'w', encoding="utf-8") as fp:
                    await fp.write(str(soup.prettify()))
                return 0
    # 处理改造
    if skin_name == '改造':
        for skin in ship_skin_list:
            if skin['name'] == 'Retrofit':
                image_path = str(skin['image']).replace(
                    "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
                background_path = str(skin['background']).replace(
                    "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
                chibi_path = str(skin['chibi']).replace(
                    "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
                soup.find(id='img-content')['style'] = "background-image: url('" + background_path + "')"
                soup.find(id='img-content').string = ''
                soup.find(id='img-content').append(soup.new_tag('img', src=image_path, style="height: 720px"))
                soup.find(id='img-content').append(
                    soup.new_tag('img', src=chibi_path, style="position: fixed;bottom: 0;left: 0;"))

                async with aiofiles.open(DATA_PATH.joinpath('ship_html', 'ship_skin.html'),
                          'w', encoding="utf-8") as fp:
                    await fp.write(str(soup.prettify()))
                return 0
    # 处理普通皮肤
    for i in range(1, len(ship_skin_list)):
        if str(ship_skin_list[i]['name']) == 'Original Art':
            continue
        try:
            if str(ship_skin_list[i]['info']['cnClient']) == skin_name:
                image_path = str(ship_skin_list[i]['image']).replace(
                    "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
                background_path = str(ship_skin_list[i]['background']).replace(
                    "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
                chibi_path = str(ship_skin_list[i]['chibi']).replace(
                    "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
                soup.find(id='img-content')['style'] = "background-image: url('" + background_path + "')"
                soup.find(id='img-content').string = ''
                soup.find(id='img-content').append(soup.new_tag('img', src=image_path, style="height: 720px"))
                soup.find(id='img-content').append(
                    soup.new_tag('img', src=chibi_path, style="position: fixed;bottom: 0;left: 0;"))

                async with aiofiles.open(DATA_PATH.joinpath('ship_html', 'ship_skin.html'),
                          'w', encoding="utf-8") as fp:
                    await fp.write(str(soup.prettify()))
                return 0
            else:
                continue
        except:
            continue
    return 4



async def get_ship_skin_by_id_with_index(id, index):
    soup = BeautifulSoup(
        open(DATA_PATH.joinpath('ship_html', 'ship_skin.html'),
             encoding='UTF-8'),
        "lxml")
    result = await get_ship_data_by_id(str(id))
    ship_skin_list = result['skins']
    image_path = ''
    background_path = ''
    chibi_path = ''
    # 处理原皮
    if index > len(ship_skin_list):
        return -1
    else:
        image_path = str(ship_skin_list[index]['image']).replace(
            "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
        background_path = str(ship_skin_list[index]['background']).replace(
            "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")
        chibi_path = str(ship_skin_list[index]['chibi']).replace(
            "https://raw.githubusercontent.com/AzurAPI/azurapi-js-setup/master/", "")

        soup.find(id='img-content')['style'] = "background-image: url('" + background_path + "')"
        soup.find(id='img-content').string = ''
        soup.find(id='img-content').append(soup.new_tag('img', src=image_path, style="height: 720px"))
        soup.find(id='img-content').append(
            soup.new_tag('img', src=chibi_path, style="position: fixed;bottom: 0;left: 0;"))
        DATA_PATH.joinpath('ship_html', 'ship_skin.html')
        async with aiofiles.open(DATA_PATH.joinpath('ship_html', 'ship_skin.html'),
                  'w', encoding="utf-8") as fp:
            await fp.write(str(soup.prettify()))
        return 0





"""
方法名：get_random_gallery
参数：无
返回值：字符串
说明：该方法随机返回游戏加载图像的随机文件名
"""


def get_random_gallery():
    gallery_path = Path(DATA_PATH, 'ship_html', 'images', 'gallery').resolve()
    files = [f.relative_to(gallery_path) for f in gallery_path.iterdir() if f.is_file()]
    rfile = random.choice(files)
    return str(rfile)


"""
方法名：get_pve_recommendation
参数列表：无
用处：爬取bwiki的PVE舰船推荐图表
返回值：div_list(数组)，url集合
"""


async def get_pve_recommendation():
    url = "https://wiki.biligame.com/blhx/%E4%BA%95%E5%8F%B7%E7%A2%A7%E8%93%9D%E6%A6%9C%E5%90%88%E9%9B%86"
    response_text:str = await get_data(url,mode='text')
    soup = BeautifulSoup(response_text, "lxml")
    div_list = soup.find_all(class_='floatnone')
    return div_list


"""
方法名：get_ship_weapon_by_ship_name
参数列表：name(string)
用处：根据船名获取bwiki的推荐装备，生成html
返回值：无
"""


async def get_ship_weapon_by_ship_name(name):
    # 这里不知道怎么改，先注释问原作者
    # url = "https://wiki.biligame.com/blhx/" + str(name)
    # response_text:str = await get_data(url,mode='text')
    # soup = BeautifulSoup(response_text, "lxml")
    # div_list = soup.find(class_='row zb-table')
    target_soup = BeautifulSoup(
        open(DATA_PATH.joinpath('ship_html', 'ship_weapon_temp.html'),
             encoding='UTF-8'), "lxml")
    # target_soup.find('body').append(div_list)
    async with aiofiles.open(DATA_PATH.joinpath('ship_html', 'ship_weapon.html'),
              'w', encoding="utf-8") as fp:
        await fp.write(str(target_soup.prettify()))


async def force_update_offline():
    Path(SAVE_PATH, 'azurapi_data').mkdir(parents=True, exist_ok=True)
    ship_list = await get_data(SHIP_LIST,mode = 'str')
    chapter_list = await get_data(CHAPTER_LIST,mode = 'str')
    equipment_list = await get_data(EQUIPMENT_LIST,mode = 'str')
    version_info = await get_data(VERSION_INFO,mode = 'str')
    memories_info = await get_data(MEMORIES_INFO,mode = 'str')

    async with aiofiles.open(SAVE_PATH.joinpath('azurapi_data', 'ships.json'), 'wb') as f:
        await f.write(json.dumps(ship_list, ensure_ascii=False).encode())
    async with aiofiles.open(SAVE_PATH.joinpath('azurapi_data', 'chapters.json'), 'wb') as f:
        await f.write(json.dumps(chapter_list, ensure_ascii=False).encode())
    async with aiofiles.open(SAVE_PATH.joinpath( 'azurapi_data', 'equipments.json'), 'wb') as f:
        await f.write(json.dumps(equipment_list, ensure_ascii=False).encode())
    async with aiofiles.open(SAVE_PATH.joinpath('azurapi_data', 'version-info.json'), 'wb') as f:
        await f.write(json.dumps(version_info, ensure_ascii=False).encode())
    async with aiofiles.open(SAVE_PATH.joinpath('azurapi_data', 'memories.json'), 'wb') as f:
        await f.write(json.dumps(memories_info, ensure_ascii=False).encode())


async def get_recent_event():
    base_url='https://wiki.biligame.com'
    url = "https://wiki.biligame.com/blhx/首页"
    response_text:str = await get_data(url,mode='text')
    soup = BeautifulSoup(response_text, "lxml")
    div_list=soup.find(class_='wikitable eventCalendar noselect')
    if div_list.a['href'] is not None and str( div_list.a['href'])!='':
        return base_url+str(div_list.a['href'])
    else:
        return None


async def gacha_heavy_10():
    gacha_result = []
    async with aiofiles.open(DATA_PATH.joinpath('gacha_data', 'pools.json'),
                             'r',
                             encoding='UTF-8') as load_f:
        load_dict = await load_f.read()
        load_dict = await str_to_json(load_dict)
        for i in range(0,10):
            flag = random.randint(0,999)
            if flag < 70:
                superRare= await get_ship_id_by_name (choice(load_dict['HeavyShipBuildingListSuperRare']))
                gacha_result.append({'id':superRare})
            if 70 <= flag < 190:
                elite = await get_ship_id_by_name (choice(load_dict['HeavyShipBuildingListElite']))
                gacha_result.append({'id': elite})
            if 190 <= flag < 450:
                rare = await get_ship_id_by_name (choice(load_dict['HeavyShipBuildingListRare']))
                gacha_result.append({'id': rare})
            if 450 <= flag < 1000:
                normal = await get_ship_id_by_name (choice(load_dict['HeavyShipBuildingListNormal']))
                gacha_result.append({'id': normal})
    return gacha_result



async def gacha_special_10():
    gacha_result = []
    async with aiofiles.open(DATA_PATH.joinpath('gacha_data', 'pools.json'),
                             'r',
                             encoding='UTF-8') as load_f:
        load_dict = await load_f.read()
        load_dict = await str_to_json(load_dict)
        for i in range(0,10):
            flag = random.randint(0,999)
            if flag < 70:
                superRare= await get_ship_id_by_name (choice(load_dict['SpecialShipBuildingListSuperRare']))
                gacha_result.append({'id':superRare})
            if 70 <= flag < 190:
                elite = await get_ship_id_by_name (choice(load_dict['SpecialShipBuildingListElite']))
                gacha_result.append({'id': elite})
            if 190 <= flag < 450:
                rare = await get_ship_id_by_name (choice(load_dict['SpecialShipBuildingListRare']))
                gacha_result.append({'id': rare})
            if 450 <= flag < 1000:
                normal = await get_ship_id_by_name (choice(load_dict['SpecialShipBuildingListNormal']))
                gacha_result.append({'id': normal})
    return gacha_result



async def gacha_light_10():
    gacha_result = []
    async with aiofiles.open(DATA_PATH.joinpath('gacha_data', 'pools.json'),
                             'r',
                             encoding='UTF-8') as load_f:
        load_dict = await load_f.read()
        load_dict = await str_to_json(load_dict)
        for i in range(0,10):
            flag = random.randint(0,999)
            if flag < 70:
                superRare= await get_ship_id_by_name (choice(load_dict['LightShipBuildingListSuperRare']))
                gacha_result.append({'id':superRare})
            if 70 <= flag < 190:
                elite = await get_ship_id_by_name (choice(load_dict['LightShipBuildingListElite']))
                gacha_result.append({'id': elite})
            if 190 <= flag < 450:
                rare = await get_ship_id_by_name (choice(load_dict['LightShipBuildingListRare']))
                gacha_result.append({'id': rare})
            if 450 <= flag < 1000:
                normal = await get_ship_id_by_name (choice(load_dict['LightShipBuildingListNormal']))
                gacha_result.append({'id': normal})
    return gacha_result

