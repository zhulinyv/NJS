import random
from datetime import date
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11 import Message

def luck_simple(num):
    if num < 18:
        return '凶'
    elif num < 53:
        return '末吉'
    elif num < 58:
        return '末小吉'
    elif num < 62:
        return '小吉'
    elif num < 65:
        return '半吉'
    elif num < 71:
        return '吉'
    else:
        return '大吉'
    

jrrp = on_command('jrrp',priority=50,block=True)
@jrrp.handle()
async def jrrp_handle(bot: Bot, event: Event):
    rnd = random.Random()
    rnd.seed(( int(date.today().strftime("%y%m%d"))*45 )*( int(event.get_user_id())*55 ))
    lucknum = rnd.randint(1,100)
    await jrrp.finish(message = Message(f'[CQ:at,qq={event.get_user_id()}]您今日的幸运指数是{lucknum}/100（越高越好），为"{luck_simple(lucknum)}"'))