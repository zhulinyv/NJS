import imgkit
import cv2
import pypinyin
import json
import aiofiles

from typing import Optional
from pathlib import Path
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Bot
from nonebot_plugin_htmlrender import html_to_pic
from nonebot.log import logger

SAVE_PATH = Path().joinpath('data/al')
tool_path = SAVE_PATH.joinpath('wkhtmltopdf', 'bin', 'wkhtmltoimage.exe')
"""
方法名：print_img
参数列表：无
用处：调用打印工具，打印ship_info.html成图片
返回值：无返回值，从html文件夹里读取html文件，打印的图片输出到images文件夹
"""

async def save_img_ship(tag:Optional[str] = None,temp:bool = True):
    tep = '_temp' if temp else ''
    if not tag:
        with open(SAVE_PATH.joinpath('ship_html', 'ship_info.html'),'r',encoding='utf-8')as f:
            html = f.read()
        pic = await html_to_pic(html=html)
        with open(SAVE_PATH.joinpath('ship_html','images', 'ship_temp.png'),'wb')as f:
            f.write(pic)
    else:
        with open(SAVE_PATH.joinpath('ship_html', f'ship_{tag}.html'),'r',encoding='utf-8')as f:
            html = f.read()
        pic = await html_to_pic(html=html)
        with open(SAVE_PATH.joinpath('ship_html','images', f'ship_{tag}{tep}.png'),'wb')as f:
            f.write(pic)
            

def print_img_ship_retrofit():
    # path_wkimg = SAVE_PATH + '/\\wkhtmltopdf/\\bin/\\wkhtmltoimage.exe'  # 工具路径
    path_wkimg = tool_path
    cfg = imgkit.config(wkhtmltoimage=path_wkimg)
    options = {
        "encoding": "UTF-8",
        "enable-local-file-access": None
    }
    print("开始")
    imgkit.from_file(SAVE_PATH.joinpath('ship_html', 'ship_retrofit.html'),
                     SAVE_PATH.joinpath('images', 'ship_retrofit_temp.png'),
                     options=options, config=cfg)  # 不管怎么样都打印这张图片
    print("结束")



def img_process_ship_retrofit():
    # SAVE_PATH.joinpath('images', 'ship_temp.png'))
    img = cv2.imread(SAVE_PATH.joinpath('ship_html','images', 'ship_retrofit_temp.png'))
    image = img.shape
    cropped = img[0:image[0], 0:620]  # 裁剪坐标为[y0:y1, x0:x1]
    cv2.imwrite(SAVE_PATH.joinpath('ship_html','images', 'ship_retrofit.png'), cropped)

"""
方法名：print_img_skin
参数列表：无
用处：调用打印工具，打印ship_skin.html成图片
返回值：无返回值，从html文件夹里读取html文件，打印的图片输出到images文件夹
"""


def print_img_skin():
    path_wkimg = tool_path  # 工具路径
    cfg = imgkit.config(wkhtmltoimage=path_wkimg)
    options = {
        "encoding": "UTF-8",
        "enable-local-file-access": None
    }
    imgkit.from_file(SAVE_PATH.joinpath('ship_html', 'ship_skin.html'),
                     SAVE_PATH.joinpath('ship_html', 'images','ship_skin.png'),
                     options=options, config=cfg)  # 不管怎么样都打印这张图片


"""
方法名：img_process_ship_info
参数列表：无
用处：裁剪图片
返回值：无返回值
"""


def img_process_ship_info():
    # SAVE_PATH.joinpath('images', 'ship_temp.png'))
    img = cv2.imread(str(SAVE_PATH.joinpath('ship_html','images', 'ship_temp.png')))
    image = img.shape
    cropped = img[0:image[0], 0:620]  # 裁剪坐标为[y0:y1, x0:x1]
    cv2.imwrite(str(SAVE_PATH.joinpath('ship_html','images', 'ship_info.png')), cropped)

    """
    方法名：img_process_ship_weapon
    参数列表：无
    用处：裁剪图片
    返回值：无返回值
    """


def img_process_ship_weapon():
    # SAVE_PATH.joinpath('images', 'ship_weapon_temp.png'))
    img = cv2.imread(str(SAVE_PATH.joinpath('ship_html','images', 'ship_weapon_temp.png')))
    image = img.shape
    cropped = img[0:image[0], 0:620]  # 裁剪坐标为[y0:y1, x0:x1]
    cv2.imwrite(str(SAVE_PATH.joinpath('ship_html','images', 'ship_weapon.png')), cropped)


def translate_ship_type(english):
    if english == 'Aircraft Carrier':
        return ['航空母舰', 'CV']
    if english == 'Destroyer':
        return ['驱逐舰', 'DD']
    if english == 'Light Cruiser':
        return ['轻型巡洋舰', 'CL']
    if english == 'Heavy Cruiser':
        return ['重型巡洋舰', 'CA']
    if english == 'Battleship':
        return ['战列舰', 'BB']
    if english == 'Light Carrier':
        return ['轻型航空母舰', 'CVL']
    if english == 'Repair':
        return ['维修舰', 'AR']
    if english == 'Battlecruiser':
        return ['战列巡洋舰', 'BC']
    if english == 'Monitor':
        return ['浅水重炮舰', 'BM']
    if english == 'Submarine':
        return ['潜艇', 'SS']
    if english == 'Submarine Carrier':
        return ['浅水母舰', 'SSV']
    if english == 'Munition Ship':
        return ['运输舰', 'AE']
    if english == 'Large Cruise':
        return ['超级巡洋舰', 'CB']
    if english == 'Aviation Battleship':
        return ['航空战列舰', 'BBV']


def pinyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += "".join(i)
    return s


async def get_local_version():
    async with aiofiles.open(SAVE_PATH.joinpath('azurapi_data', 'version-info.json'), 'r',
              encoding='utf-8') as load_f:
        load_dict = await load_f.read()
        load_dict:dict = json.loads(load_dict)
        load_dict:dict = json.loads(load_dict) # 别删除，否则会有类型错误
    return load_dict['ships']

def render_forward_msg(msg_list: list, uid=1916714922, name='小加加(VC装甲钢36D版)',bot:Bot = None):
    try:
        uid = bot.self_id
        name = list(bot.config.nickname)[0]
    except Exception as e:
        logger.warning(f'获取bot信息错误\n{e}')
    forward_msg = []
    for msg in msg_list:
        forward_msg.append({
            "type": "node",
            "data": {
                "name": str(name),
                "uin": str(uid),
                "content": msg
            }
        })
    return forward_msg


