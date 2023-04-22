from nonebot import get_driver


from nonebot import on_command
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import CommandArg, Depends, _command_arg
from nonebot.adapters.onebot.v11 import GROUP, Message, MessageEvent, MessageSegment, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER

import requests
import json

from nonebot_plugin_htmlrender import md_to_pic, html_to_pic

import os
from pathlib import Path

import time

from .config import Config
from .template import apply_template, get_vehicles_data_md, get_weapons_data_md, get_group_list, get_server_md

CODE_FOLDER = Path(__file__).parent.resolve()

global_config = get_driver().config
config = Config(**global_config.dict())
PREFIX = config.bfchat_prefix

CURRENT_FOLDER = Path(config.bfchat_dir).resolve()
CURRENT_FOLDER.mkdir(exist_ok=True)
BFV_PLAYERS_DATA = CURRENT_FOLDER/'bfv_players'
BF1_PLAYERS_DATA = CURRENT_FOLDER/'bf1_players'

BFV_PLAYERS_DATA.mkdir(exist_ok=True)
BF1_PLAYERS_DATA.mkdir(exist_ok=True)

def get_bf1_player_data(player_name:str)->dict:

    url = f'https://api.gametools.network/bf1/all/?name={player_name}&lang=zh-tw'

    res = requests.get(url)
    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise requests.HTTPError

def get_player_data(player_name:str)->dict:

    url = f'https://api.gametools.network/bfv/all/?name={player_name}&lang=zh-cn'

    res = requests.get(url)
    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise requests.HTTPError

def get_server_data(server_name:str,game='bfv')->dict:
    url = f'https://api.gametools.network/{game}/servers/?name={server_name}&platform=pc&limit=20&lang={"zh-cn" if game=="bfv" else "zh-tw"}'

    res = requests.get(url)
    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise requests.HTTPError    


BF_INIT = on_command(f'{PREFIX}bf init', block=True, priority=1, permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER)
BF_HELP = on_command(f"{PREFIX}bf help", block=True, priority=1)

@BF_INIT.handle()
async def bf_init(event:MessageEvent, state:T_State):
    if isinstance(event,GroupMessageEvent):
        session = event.group_id
        try:
            (BFV_PLAYERS_DATA/f'{session}').mkdir()
            (BF1_PLAYERS_DATA/f'{session}').mkdir()
            await BF_INIT.send(f'初始化本群绑定功能成功！\n\n群员使用 {PREFIX}bf1 bind [玩家id] 可绑定战地一账号到本群。\n群员使用 {PREFIX}bfv bind [玩家id] 可绑定战地五账号到本群。\n绑定后使用{PREFIX}bf1 me 或 {PREFIX}bfv me 可查询战绩')
        except FileExistsError:
            await BF_INIT.send(f'本群已初始化绑定功能。\n\n群员使用 {PREFIX}bf bind [玩家id] 可绑定战地一账号到本群。\n群员使用 {PREFIX}bfv bind [玩家id] 可绑定战地五账号到本群。\n绑定后使用{PREFIX}bf1 me 或 {PREFIX}bfv me 可查询战绩')

@BF_HELP.handle()
async def bf_help(event:MessageEvent, state:T_State):
    with open(CODE_FOLDER/'help.md',encoding='utf-8') as f:
        md_help = f.read()
    
    md_help = md_help.format(p=PREFIX)

    pic = await md_to_pic(md_help, css_path=CODE_FOLDER/"github-markdown-dark.css",width=1200)

    await BF_HELP.send(MessageSegment.image(pic))

BF1_BIND = on_command(f'{PREFIX}bf1 bind', block=True, priority=1)

BF1_LS = on_command(f'{PREFIX}bf1 list', block=True, priority=1)

BF1_SERVER = on_command(f'{PREFIX}bf1 server', block=True, priority=1)

BF1F = on_command(f'{PREFIX}bf1', block=True, priority=1)

@BF1_BIND.handle()
async def BF1_binding(event:GroupMessageEvent, state:T_State):
    message = _command_arg(state) or event.get_message()
    player = message.extract_plain_text().strip()
    user = event.get_user_id()
    session = event.group_id
    try:
        result = get_bf1_player_data(player)
    except:
        await BF1_BIND.send('无法获取到玩家数据，请检查玩家id是否正确。')
        return
    
    result['__update_time'] = time.time()
    try:
        with open(BF1_PLAYERS_DATA/f'{session}'/f'{user}.json','w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        await BF1_BIND.send(f'已绑定玩家id {player}，输入"{PREFIX}bf1 me"可查看战绩。')
    except FileNotFoundError:
        await BF1_BIND.send(f'该群未初始化bf1 me功能，请联系管理员使用{PREFIX}bf1 init 初始化')

@BF1_LS.handle()
async def bf1_ls(event:GroupMessageEvent, state:T_State):
    message = _command_arg(state) or event.get_message()
    session = event.group_id
    dlist = []
    for fp in (BF1_PLAYERS_DATA/f'{session}').iterdir():
        with open(fp,encoding='utf-8') as f:
            dlist.append(json.load(f))

    md_result = f"""# 本群已绑定战地一玩家数据

按等级排序

{get_group_list(dlist)}"""

    pic = await md_to_pic(md_result, css_path=CODE_FOLDER/"github-markdown-dark.css",width=700)
    await BF1F.send(MessageSegment.image(pic))
    
@BF1_SERVER.handle()
async def bf1_server(event:MessageEvent, state:T_State):
    message = _command_arg(state) or event.get_message()
    server_name = message.extract_plain_text().strip()
    server_data = get_server_data(server_name,'bf1')

    md_result = f"""# 搜索服务器：{server_name}
已找到符合要求的服务器 {len(server_data['servers'])} 个，最多显示20个
{get_server_md(server_data)}"""

    pic = await md_to_pic(md_result, css_path=CODE_FOLDER/"github-markdown-dark.css",width=700)
    await BF1F.send(MessageSegment.image(pic))




@BF1F.handle()
async def bf1_handler(event:MessageEvent, state:T_State):
    message = _command_arg(state) or event.get_message()
    args = message.extract_plain_text().strip().split(' ')
    player = args[0]
    if player == 'me' and isinstance(event, GroupMessageEvent):
        user = event.get_user_id()
        session = event.group_id
        try:
            with open(BF1_PLAYERS_DATA/f'{session}'/f'{user}.json','r', encoding='utf-8') as f:
                result = json.load(f)
        except FileNotFoundError:
            if (BF1_PLAYERS_DATA/f'{session}').exists():
                await BF1F.send(f'未找到绑定玩家数据，请使用"{PREFIX}bf1 bind [玩家id]"进行绑定')
            else:
                await BF1F.send(f'该群未初始化bf1 me功能，请联系管理员使用{PREFIX}bf1 init 初始化')
            return

        
        player = result['userName']
        if time.time() - result['__update_time'] > 3600:
            result = get_bf1_player_data(player)
            result['__update_time'] = time.time()
            with open(BF1_PLAYERS_DATA/f'{session}'/f'{user}.json','w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4) 
    else:
        result = get_bf1_player_data(player)
        result['__update_time'] = time.time()



    if len(args)==1:
        html = apply_template(result,'bf1',PREFIX)
        pic = await html_to_pic(html, viewport={"width": 700,"height":10})
        # md_result = mdtemplate(result)
        # print(md_result)
    elif args[1] == 'weapons':
        md_result = f"""## {player} 武器数据

仅展示击杀数前50数据

{get_weapons_data_md(result,50)}"""
        pic = await md_to_pic(md_result, css_path=CODE_FOLDER/"github-markdown-dark.css",width=700)
    elif args[1] == 'vehicles':
        md_result = f"""## {player} 载具数据

仅展示击杀数前50数据

{get_vehicles_data_md(result,50)}"""        


        pic = await md_to_pic(md_result, css_path=CODE_FOLDER/"github-markdown-dark.css",width=700)
    

    await BF1F.send(MessageSegment.image(pic))

BFV_BIND = on_command(f'{PREFIX}bfv bind', block=True, priority=1)

BFV_LS = on_command(f'{PREFIX}bfv list', block=True, priority=1)

BFV_SERVER = on_command(f'{PREFIX}bfv server', block=True, priority=1)

BFVF = on_command(f'{PREFIX}bfv', block=True, priority=1)




@BFV_BIND.handle()
async def bfv_binding(event:GroupMessageEvent, state:T_State):
    message = _command_arg(state) or event.get_message()
    player = message.extract_plain_text().strip()
    user = event.get_user_id()
    session = event.group_id
    try:
        result = get_player_data(player)
    except:
        await BFV_BIND.send('无法获取到玩家数据，请检查玩家id是否正确。')
        return
    
    result['__update_time'] = time.time()
    try:
        with open(BFV_PLAYERS_DATA/f'{session}'/f'{user}.json','w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        await BFV_BIND.send(f'已绑定玩家id {player}，输入"{PREFIX}bfv me"可查看战绩。')
    except FileNotFoundError:
        await BFVF.send(f'该群未初始化bfv me功能，请联系管理员使用{PREFIX}bf init 初始化')

@BFV_LS.handle()
async def bfv_ls(event:GroupMessageEvent, state:T_State):
    message = _command_arg(state) or event.get_message()
    session = event.group_id
    dlist = []
    for fp in (BFV_PLAYERS_DATA/f'{session}').iterdir():
        with open(fp,encoding='utf-8') as f:
            dlist.append(json.load(f))

    md_result = f"""# 本群已绑定战地五玩家数据

按等级排序

{get_group_list(dlist)}"""

    pic = await md_to_pic(md_result, css_path=CODE_FOLDER/"github-markdown-dark.css",width=700)
    await BFVF.send(MessageSegment.image(pic))
    
@BFV_SERVER.handle()
async def bfv_server(event:MessageEvent, state:T_State):
    message = _command_arg(state) or event.get_message()
    server_name = message.extract_plain_text().strip()
    server_data = get_server_data(server_name)

    md_result = f"""# 搜索服务器：{server_name}
已找到符合要求的服务器 {len(server_data['servers'])} 个，最多显示20个
{get_server_md(server_data)}"""

    pic = await md_to_pic(md_result, css_path=CODE_FOLDER/"github-markdown-dark.css",width=700)
    await BFVF.send(MessageSegment.image(pic))




@BFVF.handle()
async def bfv_handler(event:MessageEvent, state:T_State):
    message = _command_arg(state) or event.get_message()
    args = message.extract_plain_text().strip().split(' ')
    player = args[0]
    if player == 'me' and isinstance(event, GroupMessageEvent):
        user = event.get_user_id()
        session = event.group_id
        try:
            with open(BFV_PLAYERS_DATA/f'{session}'/f'{user}.json','r', encoding='utf-8') as f:
                result = json.load(f)
        except FileNotFoundError:
            if (BFV_PLAYERS_DATA/f'{session}').exists():
                await BFVF.send(f'未找到绑定玩家数据，请使用"{PREFIX}bfv bind [玩家id]"进行绑定')
            else:
                await BFVF.send(f'该群未初始化bfv me功能，请联系管理员使用{PREFIX}bf init 初始化')
            return

        
        player = result['userName']
        if time.time() - result['__update_time'] > 3600:
            result = get_player_data(player)
            result['__update_time'] = time.time()
            with open(BFV_PLAYERS_DATA/f'{session}'/f'{user}.json','w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4) 
    else:
        result = get_player_data(player)
        result['__update_time'] = time.time()



    if len(args)==1:
        html = apply_template(result,'bfv', PREFIX)
        pic = await html_to_pic(html, viewport={"width": 700,"height":10})
        # md_result = mdtemplate(result)
        # print(md_result)
    elif args[1] == 'weapons':
        md_result = f"""## {player} 武器数据

仅展示击杀数前50数据

{get_weapons_data_md(result,50)}"""
        pic = await md_to_pic(md_result, css_path=CODE_FOLDER/"github-markdown-dark.css",width=700)
    elif args[1] == 'vehicles':
        md_result = f"""## {player} 载具数据

仅展示击杀数前50数据

{get_vehicles_data_md(result,50)}"""        


        pic = await md_to_pic(md_result, css_path=CODE_FOLDER/"github-markdown-dark.css",width=700)
    

    await BFVF.send(MessageSegment.image(pic))













