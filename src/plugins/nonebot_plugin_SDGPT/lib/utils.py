import aiofiles
from .logger import err
from .cons import *
from .base import *


async def load_preset(dir, filename):
    try:
        async with aiofiles.open(dir + "/" + filename, mode="r", encoding='utf-8') as f:
            text = await f.read()
        return text
    except Exception as ERR:
        print(ERR)
        return err('load_preset', f'读取预设文件{dir + "/" + filename}失败')


def rules(cmdName, config, event):
    if config['Bot']['owner'] == event.get_user_id():
        return True
    group = config['Function']['Group']
    private = config['Function']['Private']
    guild = config['Function']['Guild']
    if isinstance(event, GroupMessageEvent):
        if not group['switch']: return
        if event.group_id not in group['groups'] and ('*' not in group['groups']): return
        if cmdName not in group['function'] and ('*' not in group['function']): return
    if isinstance(event, PrivateMessageEvent):
        if not private['switch']: return
        if event.user_id not in private['member'] and ('*' not in private['member']): return
        if cmdName not in private['function'] and ('*' not in private['function']): return
    if isinstance(event, GuildMessageEvent):
        if not guild['switch']: return
        if event.guild_id not in guild['guilds'] and ('*' not in guild['guilds']): return
        if cmdName not in guild['function'] and ('*' not in guild['function']): return
    return True


def getThis(event):
    if isinstance(event, GroupMessageEvent):
        return event.group_id
    if isinstance(event, PrivateMessageEvent):
        return event.user_id
    if isinstance(event, GuildMessageEvent):
        return event.guild_id


def asBot(botList, botUse, cfg):
    if botUse != 'None': return botUse
    if botList == '*': botList = AI_list
    if botList == 'chat': botList = asChat
    for bot in botList:
        if bot in cfg:
            return bot
    err('无可用ai', '此功能可用ai列表中无已加载的ai' + ', '.join(botList))
    return False


def switchModel(bot, botName, model):
    if botName == 'chatgpt':
        bot.config['model'] = model
    if botName == 'chatgpt-api':
        bot.engine = model
    if botName == 'bing':
        error('switchModel', 'bing')
    if botName == 'poe':
        error('switchModel', 'poe')


