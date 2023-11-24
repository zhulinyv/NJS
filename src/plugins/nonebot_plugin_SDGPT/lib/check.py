import os
from .cons import *
import socket
import nonebot

global switch


def iptest(value):
    global switch
    if not switch: return value
    port = int(value.split(':')[1])
    ip = value.split(':')[0]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.close()
        success('ping', value)
        return True
    except Exception as Err:
        warn('ip-test', 'ping ip[' + value + '] 失败' + str(Err))
        return False


def er(value: any, string: str):
    if type(value) != str: value = str(value)
    err('配置检查', '“' + value + '” :' + string)


def es(value: any, string: str):
    if type(value) != str: value = str(value)
    error('配置检查', '“' + value + '” :' + string)


def stop():
    err('配置检查', '配置读取中止')
    raise Exception


def wr(value: any, string: str):
    if type(value) != str: value = str(value)
    warn('配置检查', '“' + value + '” :' + string)


def check_dir(value):
    if os.path.isdir(value):
        return value
    else:
        try:
            wr(value, '不存在，尝试创建文件夹')
            os.makedirs(value)  # create the directory if it does not exist
            return value
        except OSError:
            es(value, '输入不合法')
            raise ValueError('not a valid directory path')


def check_ai(value):
    return value


def check_command(value):
    cmd = value[0]
    nonebot.init(command_start={cmd})
    if len(value) > 1:
        return value
    er(value, '命令为空')
    raise ValueError


def check_proxy(value):
    if value is None:
        return ''
    if value == '':
        return value
    if ':' not in value:
        er(value, 'proxy输入非法')
        raise ValueError
    if iptest(value):
        return value
    else:
        stop()


def check_ip(value):
    if value.startswith('^'):
        return value.replace('^', '')
    if ':' not in value:
        er(value, 'ip输入不合法')
        raise ValueError
    iptest(value)
    return value


def check_file(value):
    if os.path.isfile(value):
        return value
    es(value, '文件不存在')
    return value


def check_api_key(value):
    if value.startswith('sk-'): return value
    if value == '':
        return value
    es(value, 'api_key不合法')
    raise ValueError


def check_token(value):
    if len(value) > 20: return value
    if value == '':
        return value
    es(value, 'access_token不合法')
    raise ValueError

def check_poetoken(value):
    return value

def ip_test_switch(value):
    global switch
    if value == 'True':
        switch = True
    else:
        switch = False
    return value


def check_model(value):
    return value


def check_id(value):
    return value

def check_any(value):
    return value

def check_preset(value):
    return value

