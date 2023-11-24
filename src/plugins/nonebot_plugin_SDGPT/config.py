# -*- coding: utf-8 -*-
import asyncio
import json
import os
from typing import NewType, Any
from .lib.cons import *
from .lib.utils import asBot
from configobj import ConfigObj
from validate import Validator
from .lib.check import check_ai, check_dir, check_proxy, check_api_key, check_command, check_file, check_ip, \
    ip_test_switch, check_token, check_model, check_id, check_any, check_preset, check_poetoken
from revChatGPT.V1 import AsyncChatbot as chatGPT
from revChatGPT.V3 import Chatbot as chatGPT_api
from EdgeGPT import Chatbot as Bing
import poe


def Proxy(DIR):
    if DIR['proxy'] and DIR['proxy'] != '':
        return DIR['proxy']


def Model(DIR):
    if DIR['model'] and DIR['model'] != '':
        return DIR['model']


async def load_chatgpt(DIR, outData):
    if not DIR['access_token'] or DIR['access_token'] == '':
        warn('配置检查', f'你设定的 chatgpt 的 access_token 为空，跳过载入')
        return ''
    else:
        add = ''
        bot = chatGPT(config={"access_token": DIR['access_token']})
        model = Model(DIR)
        proxy = Proxy(DIR)
        models = [
            'text-davinci-002-render-sha',
            'text-davinci-002-render-paid',
            'gpt-4'
        ]
        if proxy:
            bot.config['proxy'] = proxy
            add += f',代理: {proxy}'
        if model:
            outData['cfg']['runtime']['chatgpt_model'] = model
            add += f',模型: {model}'
        else:
            outData['cfg']['runtime']['chatgpt_model'] = ''
        suc('chatgpt', f'ChatGPT(网页): 已加载{add}')
        outData['chatgpt'] = bot
        return 'chatgpt'


async def load_chatgpt_api(DIR, outData):
    if not DIR['api_key'] or DIR['api_key'] == '' or ('sk-' not in DIR['api_key']):
        warn('配置检查', f'你设定的 chatgpt_api 的 api_key 为空或不合法，跳过载入')
        return ''
    else:
        add = ''
        bot = chatGPT_api(api_key=DIR['api_key'])
        models = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-32k",
            "gpt-4-32k-0314"
        ]
        model = Model(DIR)
        proxy = Proxy(DIR)
        if proxy:
            bot.proxy = proxy
            add += f',代理: {proxy}'
        if model:
            outData['cfg']['runtime']['chatgpt_api_model'] = model
            add += f',模型: {model}'
        suc('chatgpt-api', f'ChatGPT(api): 已加载{add}')
        outData['chatgpt-api'] = bot
        return 'chatgpt-api'


async def load_bing(DIR, outData):
    if not DIR['cookies_file_path'] or DIR['cookies_file_path'] == '':
        warn('配置检查', f'你设定的 bing 的 cookies_file_path 为空，跳过载入')
        return ''
    else:
        add = ''
        try:
            with open(DIR['cookies_file_path'], 'r') as f:
                cookies = json.load(f)
                bot = Bing(cookies=cookies)
            proxy = Proxy(DIR)
            model = Model(DIR)
            if proxy:
                bot.proxy = proxy
                add += f',代理: {proxy}'
            if model:
                outData['cfg']['runtime']['bing_model'] = model
                add += f',模型: {model}'
            suc('bing', f'Bing: 已加载{add}')
            outData['bing'] = bot
            return 'bing'
        except:
            warn('配置检查', 'bing cookies.json 加载失败,无法使用bing')
            return ''


async def load_poe(DIR, outData):
    if not DIR['token'] or DIR['token'] == '':
        warn('配置检查', f'你设定的 Poe 的 token 为空，跳过载入')
        return ''
    else:
        add = ''
        proxy = Proxy(DIR)
        model = Model(DIR)
        models = ['Sage',
                  'GPT-4',
                  'Claude+',
                  'Claude-instant',
                  'ChatGPT',
                  'Dragonfly']
        if proxy:
            add += f',代理: {proxy}'
            bot = poe.Client(token=DIR['token'], proxy=proxy)
        else:
            bot = poe.Client(token=DIR['token'])
        bots = bot.bot_names
        if model:
            models = list(bots.values())
            if model in models:
                outData['cfg']['runtime']['poe_model'] = model
                outData['cfg']['runtime']['poe_models'] = {value: key for key, value in bots.items()}
                add += f',模型: {model}'
        suc('poe', f'Poe: 已加载{add}')
        outData['poe'] = bot
        return 'poe'


async def load():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configspec.ini')
    config = ConfigObj('config.cfg', encoding='utf-8', default_encoding='utf-8', configspec=path,
                       indent_type=' ', write_empty_values=True)
    validator = Validator({
        'dir': check_dir,
        'ai': check_ai,
        'cmd': check_command,
        'proxy': check_proxy,
        'file': check_file,
        'apikey': check_api_key,
        'ip': check_ip,
        'ip_test_switch': ip_test_switch,
        'id': check_id,
        'any': check_any,
        'preset': check_preset,
        'token': check_token,
        'model': check_model,
        'poetoken': check_poetoken
    })
    config.validate(validator, copy=True, preserve_errors=True)
    config.write()
    outData = {'cfg': config}
    botList = [await load_chatgpt(config['AI']['chatgpt'], outData),
               await load_chatgpt_api(config['AI']['chatgpt-api'], outData),
               await load_bing(config['AI']['bing'], outData),
               await load_poe(config['AI']['poe'], outData)]
    botList = [x for x in botList if len(x) > 0]
    if len(botList) > 0:
        suc('所有AI', '已加载' + str(len(botList)) + '个AI: ' + ','.join(botList))
    else:
        error('配置检查', '没有一个AI成功被加载')
    outData['bots'] = botList
    if config['Chat']['defaultAI'] not in outData:
        warn('配置检查', '你配置的 defaultAI 不存在或未加载')
        outData['BotUse'] = asBot('*', 'None', outData)
        suc('默认AI', '默认AI自动切换为' + f"{outData['BotUse']}")
    else:
        outData['BotUse'] = config['Chat']['defaultAI']
    for item in config['preset']:
        key = item
        val = config['Chat']['presets_dir'] + '/' + config['preset'][item]
        suc('预设加载', f'{key} : {val}')
    return outData
