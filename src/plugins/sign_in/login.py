import json
from .write import write_file

send = 0
async def search(coint, qq, time):
    file_name = './data/sign_in/coints.json'
    with open(file_name) as f:
        data_user = json.load(f)
    last_time = data_user[f'{qq}login']
    global send
    if time == last_time:
        send = '今天已经签到过了，明天再来叭'
    else:
        await write_file(coint, qq, False, data_user, time)
        send = f'签到成功~ 好感 + {coint} ~~'
        
async def notice():#返回信息
    news = send
    return news