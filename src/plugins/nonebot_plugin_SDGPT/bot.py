import asyncio
import re
import time

from .lib.cons import *
from .lib.base import *
from .lib.utils import load_preset, switchModel
from .config import load as cfg_load

global dotenv_file
global chatgpt
global chatgpt_api
global bing
global config
global L_chatgpt
global L_chatgpt_api
global L_bing
global L_poe
global poe


async def bot_start():
    global L_chatgpt
    global L_chatgpt_api
    global L_bing
    global L_poe
    global chatgpt
    global chatgpt_api
    global bing
    global poe
    global config
    cfg = await cfg_load()
    if 'chatgpt' in cfg: chatgpt = cfg['chatgpt']
    if 'chatgpt-api' in cfg: chatgpt_api = cfg['chatgpt-api']
    if 'bing' in cfg: bing = cfg['bing']
    if 'poe' in cfg: poe = cfg['poe']

    config = cfg['cfg']
    if config['Chat']['reload_presets']:
        config['runtime']['preset'] = ''
        config.write()

    L_chatgpt = asyncio.Lock()
    # L_chatgpt_api = asyncio.Lock()
    L_bing = asyncio.Lock()
    L_poe = asyncio.Lock()

    return cfg


async def msg_end():
    return


async def Chat(event, foo, BOT, message, p='', noStream=False, noOut=False):
    if noOut:
        noStream = True
    if len(p) == 0 and len(config['runtime']['preset']) > 2:
        p = await load_preset(config['Chat']['presets_dir'], config['runtime']['preset'])
        info('预设', p)
    elif len(p) > 0:
        p = await load_preset(config['Chat']['presets_dir'], config['preset'][p])

    reply = config['Chat']['reply']
    if type(event) == GroupMessageEvent:
        stream = config['Function']['Group']['stream']
    elif type(event) == GuildMessageEvent:
        stream = config['Function']['Guild']['stream']
    elif type(event) == PrivateMessageEvent:
        stream = config['Function']['Private']['stream']
    else:
        return
    if noStream:
        stream = False
    if stream:
        await ask_stream(event, foo, BOT, message, p)
    else:
        out = await ask(BOT, message, p)
        if noStream:
            out = re.sub(r".*\.AIP", "", out)
        if noOut:
            return out
        await foo.send(event, out, reply_message=reply)


async def ask(bot, message, prompt=''):
    if bot == 'chatgpt':
        async with L_chatgpt:
            if len(prompt) > 1: message = promptBase.replace("$prompt$", prompt) + message
            info('ASK', message)
            if config['runtime']['chatgpt_model'] and config['runtime']['chatgpt_model'] != '':
                switchModel(chatgpt, 'chatgpt', config['runtime']['chatgpt_model'])
            async for data in chatgpt.ask(message):
                out = data['message']
            return out
    if bot == 'chatgpt-api':
        chatgpt_api.system_prompt = prompt
        switchModel(chatgpt, 'chatgpt-api', config['runtime']['chatgpt_api_model'])
        out = await chatgpt_api.ask_async(message)
        return out
    if bot == 'bing':
        async with L_bing:
            if len(prompt) > 1: message = promptBase + message
            out = await bing.ask(message, conversation_style=config['runtime']['bing_model'])
            if out['item']['messages'][-1]['author'] != 'bot':
                bot.reset()
                out = await bing.ask(message, conversation_style=config['runtime']['bing_model'])
            out = out['item']['messages'][-1]['text']
            out = re.sub(r'\[\^\d\^]','',out)
            return out
    if bot == 'poe':
        async with L_poe:
            if len(prompt) > 1: message = promptBase + message
            for chunk in poe.send_message(config['runtime']['poe_models'][config['runtime']['poe_model']], message):
                pass
            out = chunk["text"]
            return out


async def ask_stream(event, func, bot, message, prompt=''):
    text = ''
    timeNow = time.time()
    wait_time = config['Chat']['stream_wait_time']
    end_str = tuple(config['Chat']['stream_endStr'])
    before = ''
    info('ASK', prompt + message)

    async def stream_process(name, end=''):
        nonlocal timeNow
        nonlocal text
        nonlocal func
        nonlocal before
        nonlocal isTrue
        if len(end) > 0:
            end = end.replace(before, '')
            await func.send(event, end)
            info(name + 'end', end)
            return True
        if time.time() - timeNow > wait_time and text.endswith(end_str):
            out = text.replace(before, '')
            if out.startswith('\n'):
                out = out.replace(r'^\n*', '')
            timeNow = time.time()
            info(name + 'time', out)
            await func.send(event, out)
            before = text
            return False

    if bot == 'chatgpt':
        async with L_chatgpt:
            if len(prompt) > 1: message = promptBase.replace("$prompt$", prompt) + message
            async for data in chatgpt.ask(message):
                text = data['message']
                isEnd = await stream_process('chatgpt')
                if isEnd and len(text.replace(before, '').replace(' ', '')) > 1:
                    await stream_process('chatgpt', text)
    if bot == 'chatgpt-api':
        async with L_chatgpt_api:
            chatgpt_api.system_prompt = prompt
            async for data in chatgpt_api.ask_stream_async(message):
                text += data
                isEnd = await stream_process('chatgpt-api')
                if isEnd and len(text.replace(before, '').replace(' ', '')) > 1:
                    await stream_process('chatgpt-api', text)
    if bot == 'bing':
        async with L_bing:
            if len(prompt) > 1: message = promptBase + message
            async for data in bing.ask_stream(message):
                isTrue, textdata = data
                if type(textdata) == str:
                    text = textdata
                    await stream_process('Bing')
                else:
                    await stream_process('bing', text)
    if bot == 'poe':
        async with L_poe:
            if len(prompt) > 1: message = promptBase + message
            for chunk in poe.send_message(config['runtime']['poe_models'][config['runtime']['poe_model']], message):
                text += chunk["text_new"]
                isEnd = await stream_process('poe')
                if isEnd and len(text.replace(before, '').replace(' ', '')) > 1:
                    await stream_process('poe', text)
