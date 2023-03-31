from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from .read import notice2, read_data
from .login import notice
import time
import json
import httpx
import random
import asyncio
import requests



qd = on_regex(pattern = r'^签到$')

@qd.handle()
async def lj(event: MessageEvent):
    coints = random.randint(1,10)
    qq_id = str(event.user_id)
    local_time = time.localtime(event.time)
    login_time = time.strftime('%d', local_time)
    file_name = './data/sign_in/coints.json'
    # 签到
    with open(file_name) as f:
            data_user = json.load(f)
    if qq_id in data_user: # 判断用户是不是第一次签到
        await read_data(coints, qq_id, login_time)  # 首次使用签到功能需要先执行一次签到
        lovelive_send = await notice()
    else:
        await read_data(coints, qq_id, login_time)  # 首次使用签到功能需要先执行一次签到
        lovelive_send = await notice2()
    # 等级
    f.close()
    with open(file_name) as f:
            data_user = json.load(f)
    money = data_user[f'{qq_id}']
    level_msg = level_up(money)
    try:
        # 一言部分
        url = 'https://api.juncikeji.xyz/api/mryy.php'
        get_data = requests.get(url=url, timeout=20, verify=False)
        get_txt = get_data.text
    except Exception:
        get_txt = ""
    # 整合信息
    msg = f"\n{lovelive_send}\n{level_msg}\n\n{get_txt}"
    # 图片
    res = httpx.get(url='https://dev.iw233.cn/api.php?sort=pc&type=json', headers={'Referer':'http://www.weibo.com/'})
    res = res.text
    res = ''.join(x for x in res if x.isprintable())
    res = json.loads(res)["pic"]
    async with httpx.AsyncClient() as client:
        task_list = []
        for url in res:
            task = asyncio.create_task(func(client,url))
            task_list.append(task)
        image_list = await asyncio.gather(*task_list)
    image_list = [image for image in image_list if image]
    pic_url = image_list[0]
    await qd.finish(msg + MessageSegment.image(file=pic_url), at_sender=True)

def level_up(money):
    level1 = 10
    level2 = 25
    level3 = 50
    level4 = 75
    level5 = 100
    level6 = 125
    level7 = 150
    level8 = 180
    level9 = 250
    level10 = 520

    if money < level1:
        level = f'当前好感: {money}/{level1}\n当前等级: 1'
    elif money < level2:
        level = f'当前好感: {money}/{level2}\n当前等级: 2'
    elif money < level3:
        level = f'当前好感: {money}/{level3}\n当前等级: 3'
    elif money < level4:
        level = f'当前好感: {money}/{level4}\n当前等级: 4'
    elif money < level5:
        level = f'当前好感: {money}/{level5}\n当前等级: 5'
    elif money < level6:
        level = f'当前好感: {money}/{level6}\n当前等级: 6'
    elif money < level7:
        level = f'当前好感: {money}/{level7}\n当前等级: 7'
    elif money < level8:
        level = f'当前好感: {money}/{level8}\n当前等级: 8'
    elif money < level9:
        level = f'当前好感: {money}/{level9}\n当前等级: 9'
    else:
        level = f'当前好感:{money}/{level10}\n当前等级:10'
    
    return level





hg = on_regex(pattern = r'^我的好感$')

@hg.handle()
async def lj(event: MessageEvent):
    qq_id = str(event.user_id)
    lovelive_send = await search_qq(qq_id)
    await hg.send(Message(str(lovelive_send)), at_sender=True)

send = 0
async def search_qq(qq):
    global send
    file_name = './data/sign_in/coints.json'
    with open(file_name) as f:
        data_user = json.load(f)
    try:
        money = data_user[f'{qq}']
        data_time = data_user[f'{qq}login']

        time_tuple = time.localtime(time.time())
        sys_time = "当前时间为: \n{}年{}月{}日{}点{}分{}秒".format(time_tuple[0],time_tuple[1],time_tuple[2],time_tuple[3],time_tuple[4],time_tuple[5])

        level_msg = level_up(money)
        send = f'\n{level_msg}\n' + f"{random.choice(like_message)}" + MessageSegment.face(id_=66) + f"\n\n上次签到日期: {data_time}日\n{sys_time}"
        return send
    except Exception:
        send = "脑积水的记忆里没有你这号人哦~请先\"签到\"~~!"
        return send





async def func(client,url):
    resp = await client.get(url,headers={'Referer':'http://www.weibo.com/',})
    if resp.status_code == 200:
        return resp.content
    else:
        return None
    


like_message = [
    "最喜欢你了，需要暖床吗？",
    "当然是你啦",
    "咱也是，非常喜欢你~",
    "那么大！（张开手画圆），丫！手不够长。QAQ 咱真的最喜欢你了~",
    "不可以哦，只可以喜欢咱一个人",
    "突然说这种事...",
    "喜欢⁄(⁄⁄•⁄ω⁄•⁄⁄)⁄咱最喜欢你了",
    "咱也喜欢你哦",
    "好啦好啦，咱知道了",
    "有人喜欢咱，咱觉得很幸福",
    "诶嘿嘿，好高兴",
    "咱也一直喜欢你很久了呢..",
    "嗯...大概有这——么——喜欢~（比划）",
    "喜欢啊！！！",
    "这……这是秘密哦"]