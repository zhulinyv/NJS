import json
from .write import write_file # 调用写入模块
from .login import search

send = 1
async def read_data(coint, qq, time):
    file_name = './data/sign_in/coints.json'
    global send
    try:
        with open(file_name) as f:
            data_user = json.load(f)
        if qq in data_user: # 判断用户是不是第一次签到
            await search(coint, qq, time)
        else:
            await write_file(coint, qq, True, data_user, time)
            send = f'签到成功~ 好感 + {coint} ~~'

    except FileNotFoundError:
        data = {'null':0}
        with open(file_name,'w') as f:
           json.dump(data,f)
        with open(file_name) as f:
            data_2 = json.load(f)
        await write_file(coint, qq, True, data_2, time)

async def notice2():
    news = send
    return news