import html
import re
import sys

from nonebot.log import logger_id, default_filter
from nonebot import logger

logger.remove(logger_id)


def formatter(record):
    level = record['level'].name
    add = ''
    Dir = {
        'INFO': '<cyan>',
        'ERROR': '<RED>[ERROR]</RED><red>',
        'WARNING': '<LIGHT-YELLOW><black>[WARN]</black></><light-yellow>',
        'DEBUG': '<bold>',
        'SUCCESS': '<green>',
        'FBOT': '<fg #bf0060>',
        'suc': '<GREEN>[OK]</GREEN><green>',
        'err': '<RED>[ERROR]</RED><RED><white>',
        'STDOUT': '<cyan>'
    }
    color_tag = Dir[level]
    if not color_tag:
        color_tag = ''
    match = re.match(r'^\s*\[([^]]+)]', record['message'])
    if match:
        func_name = '[' + match[1] + ']'
        record['message'] = record['message'].replace(func_name, '')
    else:
        func_name = '[' + record['name'] + ']'
    if level == 'ERROR':
        add = "{exception}"
    if level == 'err':
        add = "</>"
    return color_tag + func_name + "</>" + '{message}' + "\n" + add


logger.add(sys.stdout, format=formatter, level=0, filter=default_filter, diagnose=True, serialize=False)
logger.level('suc', no=25)
logger.level('err', no=40)
logger.level('FBOT', no=20)


def info(app: str, text: str): logger.opt(colors=True).log('FBOT', f"[{app}] {html.escape(text)}")


def error(app: str, text: str): logger.opt(colors=True).error(f"[{app}] {html.escape(text)}")


def success(app: str, text: str): logger.opt(colors=True).success(f"[{app}] {html.escape(text)}")


def warn(app: str, text: str): logger.opt(colors=True).warning(f"[{app}] {html.escape(text)}")


def debug(app: str, text: str): logger.opt(colors=True).debug(f"[{app}] {html.escape(text)}")


def suc(app: str, text: str): logger.opt(colors=True).log('suc', f"[{app}] {html.escape(text)}")


def err(app: str, text: str): logger.opt(colors=True).log('err', f"[{app}] {html.escape(text)}")


