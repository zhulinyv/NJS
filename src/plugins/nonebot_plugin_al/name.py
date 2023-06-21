from pathlib import Path

BOT_PATH = Path.cwd()
DATA_PATH = Path().joinpath('data/al')
PATH = str(DATA_PATH.joinpath('azurapi_data'))
BACK_PATH = DATA_PATH.joinpath('azurapi_data_bak')
DATA_PATH_STR = str(DATA_PATH)
SAVE_PATH = DATA_PATH
MAIN_URL = "https://ghproxy.com/https://raw.githubusercontent.com/AzurAPI"    ##https://raw.fastgit.org可以根据需要配置不同代理，结合网络情况自行修改
SHIP_LIST = f"{MAIN_URL}/azurapi-js-setup/master/ships.json"
CHAPTER_LIST = f"{MAIN_URL}/azurapi-js-setup/master/chapters.json"
EQUIPMENT_LIST = f"{MAIN_URL}/azurapi-js-setup/master/equipments.json"
VERSION_INFO = f"{MAIN_URL}/azurapi-js-setup/master/version-info.json"
MEMORIES_INFO = f"{MAIN_URL}/azurapi-js-setup/master/memories.json"
AVAILABLE_LANGS = ["en", "cn", "jp", "kr", "code", "official"]

# 代码合并时请修改这里的路径！！！！！

FONT_GACHA_LV = DATA_PATH.joinpath('fonts', 'number.ttf')                   # 抽卡时等级的字体文件
FONT_GACHA_NM = DATA_PATH.joinpath('fonts', 'ZhunYuan.otf')                 # 抽卡时下面文字的字体文件
PATH_ROOT_GACHA = DATA_PATH.joinpath('gacha_data')                          # 图片资源根目录
PATH_EDGE_GACHA = DATA_PATH.joinpath('gacha_data', 'image_frame')           # 外边框目录
PATH_CHAR_GACHA = DATA_PATH.joinpath('gacha_data', 'character_image')       # 角色立绘目录
PATH_STAR_GACHA = DATA_PATH.joinpath('gacha_data', 'star')                  # 星星图片目录
PATH_TYPE_GACHA = DATA_PATH.joinpath('gacha_data', 'type_icon')             # 舰种图片目录
PATH_BG_GACHA = DATA_PATH.joinpath('gacha_data', 'level_background')        # 背景图片目录

import aiofiles
import difflib

try:
    import ujson as json
except:
    import json


'''
这个模块定义了名字系统及其对应的操作方法。引入的库都是py的标准库，无需额外安装
id: [
    cn_name,
    jp_name,
    kr_name,
    en_name,
    nickname1,
    nickname2,
    ...
],
'''




'''
function: StringSimilar
args: 
    str1, str2: str 比较的两个字符串
return:
    返回一个数字，表示两个字符串的相似程度

检查两个字符串的相似程度
'''
def StringSimilar(str1: str, str2: str):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


'''
function: UpdateName
args: null
return: 返回整数，0表示成功，其他数字表示失败

初始化名称文件，在执行脚本更新之后应该执行一次这个方法。
对于已经在名字系统里面存在的船只，不做任何处理；对于新加入的船，会进行添加。
'''
async def UpdateName():
    ships = {}

    # 判断文件是否存在，不存在的话就不进行读取
    try:
        async with aiofiles.open(DATA_PATH_STR + '/azurapi_data/names.json', 'r', encoding='utf-8') as fp:
            load_dict = str(await fp.read())
            ships = await str_to_json(load_dict)
    except:
        pass

    async with aiofiles.open(DATA_PATH_STR + '/azurapi_data/ships.json', 'r', encoding='utf-8') as fp:
        load_dict = str(await fp.read())
        data = await str_to_json(load_dict)
        print(f'data的类型是{type(data)}')

    for item in data:
        if item['id'] in ships.keys():
            continue
        ships[item['id']] = [item['names']['cn'], item['names']['jp'], item['names']['kr'], item['names']['en']]

    # print(ships)
    async with aiofiles.open(DATA_PATH_STR + '/azurapi_data/names.json', 'w', encoding='utf-8') as fp:
        # json.dump(ships, fp, indent=2, ensure_ascii=False)
        await fp.write(json.dumps(ships, indent=2, ensure_ascii=False))

    return 0


'''
function: AddName
args: 
    id: str 待添加的船只的id，这个id应该通过GetIDByNickname方法获取
    nickname: str 待添加的别名
return: 返回整数，0表示成功，其他数字表示失败

为舰船上传新的别名，在调用这个方法的时候用该特别注意权限控制
'''
ERR_NAMEALREADYEXISTS = -1
async def AddName(id: str, nickname: str):

    async with aiofiles.open(DATA_PATH_STR + '/azurapi_data/names.json', 'r', encoding='utf-8') as fp:
        load_dict = str(await fp.read())
        data = await str_to_json(load_dict)

    if nickname in data[str(id)]:
        return ERR_NAMEALREADYEXISTS
    data[id].append(nickname)

    async with aiofiles.open(DATA_PATH_STR + '/azurapi_data/names.json', 'w', encoding='utf-8') as fp:
        await fp.write(json.dumps(data, indent=2, ensure_ascii=False))

    return 0


'''
function: DelName
args: 
    id: str 待删除的船只的id，这个id应该通过GetIDByNickname方法获取
    nickname: str 待删除的别名
return: 返回整数，0表示成功，其他数字表示失败

为舰船删除已有的别名，在调用这个方法的时候用该特别注意权限控制
'''
ERR_NICKNAMENOTFOUND = -1
async def DelName(id: str, nickname: str):

    async with aiofiles.open(DATA_PATH_STR + '/azurapi_data/names.json', 'r', encoding='utf-8') as fp:
        load_dict = str(await fp.read())
        data = await str_to_json(load_dict)

    try:
        data[id].remove(nickname)
    except:
        return ERR_NICKNAMENOTFOUND

    async with aiofiles.open(DATA_PATH_STR + '/azurapi_data/names.json', 'w', encoding='utf-8') as fp:
        await fp.write(json.dumps(data, indent=2, ensure_ascii=False))

    return 0


'''
function: GetStandredNameByNickname
args: 
    nickname: str 名称字符串，可以是船只的本名或者别名
return:
    如果查找到船只，返回一个包含船只id，标准名和相似度的字典
    如果没有查找到船只，返回ERR_SHIPNOTFOUND整数值，该值为-1

根据船只的标准名或者别名，查找船只的id和标准名
'''
ERR_SHIPNOTFOUND = -1
async def GetIDByNickname(nickname: str):

    async with aiofiles.open(DATA_PATH_STR + '/azurapi_data/names.json', 'r', encoding='utf-8') as fp:
        load_dict = str(await fp.read())
        data = await str_to_json(load_dict)

    # data = {}
    retvalue = {}
    for item in data.items():
        if nickname in item[1]:
            retvalue = {
                'id': item[0],
                'standred_name': item[1][0],     # 使用cn_name作为标准名
                'similarity': 1.0
            }
            break
    else:
        # 完全匹配失败的时候采用模糊匹配，使用匹配到的第一个
        s_before = 0
        for item in data.items():
            for name in item[1]:
                s_after = StringSimilar(name, nickname)
                if s_after < s_before:
                    continue
                if s_after > 0.5:       # 相似度阈值是0.5
                    # print(1)
                    retvalue = {
                        'id': item[0],
                        'standred_name': item[1][0],
                        'simil1arity': s_after
                    }
                    s_before = s_after
                    continue
        if retvalue == {}:
            # 模糊匹配没有匹配到，返回-1
            retvalue = ERR_SHIPNOTFOUND


    return retvalue


'''
function: GetAllNickname
args: 
    id: str 舰船的id，通过GetIDByNickname方法获取
return:
    返回一个数组，里面包含这个舰船的所有名称

根据舰船的标准名，返回这个舰船的所有名称
'''
async def GetAllNickname(id: str):

    async with aiofiles.open(DATA_PATH_STR + '/azurapi_data/names.json', 'r', encoding='utf-8') as fp:
        load_dict = str(await fp.read())
        data = await str_to_json(load_dict)

    return data[id]

async def str_to_json(data:str):
    while isinstance(data,str):
        data = json.loads(data)
    return data