from nonebot import require

GuildMessageEvent = require('nonebot_plugin_guild_patch').GuildMessageEvent
from .logger import info, error, warn, err, debug, suc, success,err
from nonebot.adapters.onebot.v11.event import PrivateMessageEvent, GroupMessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot import get_driver
from nonebot.message import event_postprocessor
from nonebot.adapters import Event