from datetime import datetime
import datetime as dt
import math
from os import path,makedirs
import os
from PIL import Image, ImageDraw, ImageFont
import nonebot
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event,Message,MessageSegment
from nonebot.params import CommandArg,ArgPlainText
from nonebot.matcher import Matcher
from yaml import dump,load,Loader
from nonebot.permission import SUPERUSER


#初始化
config_name="data/notebook/config.yaml"
unfinished_job_name="data/notebook/unfinished_job.yaml"
ban_name="data/notebook/ban.yaml"
schedule_name="data/notebook/schedule.yaml"
default_config={}
default_unfinished_job={}
default_ban_word={"words":[],"users":[]}

# 笔记的字体颜色和背景颜色
note_font_color=[0,0,0]
note_bg_color=[255,255,255]


# 获取env配置
try:
    nonebot.logger.debug(nonebot.get_driver().config.note_font_color)
    nonebot.logger.debug(nonebot.get_driver().config.note_bg_color)
    note_font_color = nonebot.get_driver().config.note_font_color if nonebot.get_driver().config.note_font_color!= "" else [0,0,0]
    note_bg_color = nonebot.get_driver().config.note_bg_color if nonebot.get_driver().config.note_bg_color != "" else [255,255,255]
except:
    nonebot.logger.debug("note插件部分配置缺失，采用默认配置。")

try:
    note_type=nonebot.get_driver().config.note_type
except:
    note_type='text'

try:
    note_restart_notice=nonebot.get_driver().config.note_restart_notice
except:
    note_restart_notice=False



if path.exists("data/notebook")==False:
    makedirs("data/notebook")

if path.exists("{}/data".format(os.path.dirname(os.path.abspath(__file__))))==False:
    makedirs("{}/data".format(os.path.dirname(os.path.abspath(__file__))))

if path.exists(config_name)==False:
    with open(config_name,'w',encoding='utf-8') as f:
        f.write(dump(default_config,allow_unicode=True))
        f.close()

if path.exists(unfinished_job_name)==False:
    with open(unfinished_job_name,'w',encoding='utf-8') as f:
        f.write(dump(default_unfinished_job,allow_unicode=True))
        f.close()

if path.exists(ban_name)==False:
    with open(ban_name,'w',encoding='utf-8') as f:
        f.write(dump(default_ban_word,allow_unicode=True))
        f.close()


#读取superusers
driver=nonebot.get_driver()
superusers=driver.config.superusers

spy=[]

#note种类
note=on_command(cmd="note",aliases={"记事","记事本"},priority=99,block=True)
interval_note=on_command(cmd="interval_note",aliases={"间隔记事","间隔记事本",'innote'},priority=99,block=True)
cron_note=on_command(cmd="cron_note",aliases={"定时记事","定时记事本",'crnote'},priority=99,block=True)
date_note=on_command(cmd="date_note",aliases={"单次记事","单次记事本",'danote'},priority=99,block=True)

#note其他功能
note_help=on_command(cmd="note_help",aliases={"记事帮助","记事本帮助"},priority=1,block=True)
note_delete=on_command(cmd="note_delete",aliases={"记事删除","记事本删除"},priority=2,block=True)
note_list=on_command(cmd="note_list",aliases={"记事列表","记事本列表"},priority=3,block=True)

#note的superuser功能
note_check=on_command(cmd="note_check",aliases={"记事查看","记事本查看"},priority=1,block=True,permission=SUPERUSER)
note_remove=on_command(cmd="note_remove",aliases={"记事移除","记事本移除"},priority=1,block=True,permission=SUPERUSER)
note_spy=on_command(cmd="note_spy",aliases={"记事本监控","记事本监控"},priority=5,block=True,permission=SUPERUSER)
note_spy_remove=on_command(cmd="note_spy_remove",aliases={"记事监控移除","记事本监控移除"},priority=1,block=True,permission=SUPERUSER)
note_ban=on_command(cmd="note_ban",aliases={"记事禁止","记事本禁止"},priority=5,block=True,permission=SUPERUSER)
note_ban_list=on_command(cmd="note_ban_list",aliases={"记事禁止列表","记事本禁止列表"},priority=1,block=True,permission=SUPERUSER)
note_ban_remove=on_command(cmd="note_ban_remove",aliases={"记事禁止移除","记事本禁止移除"},priority=1,block=True,permission=SUPERUSER)

interval_note_other=on_command(cmd="interval_note_other",aliases={"间隔记事他人","间隔记事本他人"},priority=99,block=True,permission=SUPERUSER)
cron_note_other=on_command(cmd="cron_note_other",aliases={"定时记事他人","定时记事本他人"},priority=99,block=True,permission=SUPERUSER)
date_note_other=on_command(cmd="date_note_other",aliases={"单次记事他人","单次记事本他人"},priority=99,block=True,permission=SUPERUSER)

interval_note_group=on_command(cmd="interval_note_group",aliases={"群间隔记事","群间隔记事本"},priority=99,block=True,permission=SUPERUSER)
cron_note_group=on_command(cmd="cron_note_group",aliases={"群定时记事","群定时记事本"},priority=99,block=True,permission=SUPERUSER)
date_note_group=on_command(cmd="date_note_group",aliases={"群单次记事","群单次记事本"},priority=99,block=True,permission=SUPERUSER)



#创建note
@note.handle()
async def _(matcher:Matcher,event:Event,args:Message = CommandArg()):
    if args:
        matcher.set_arg('content',args)

@note.got('content',prompt='请输入您想记事的内容：')
async def _note(event:Event,content:str=ArgPlainText('content')):
    id=event.get_user_id()
    ban=await read_ban()
    if id in ban.get("users"):
        await note.finish("抱歉，您在记事黑名单内，不能进行记事")
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"试图记事"+content))
            await note.finish("您此次记事触犯了禁用词，记事失败")
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    if content in config.get(id):
        await note.finish("已存在相同内容的记事，请重新输入")
    else:
        config.get(id).append(content)
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+content))
        await note.finish("成功记事，您可以通过note_list指令查看记事列表")



#创建interval_note
@interval_note.handle()
async def _(matcher:Matcher,args:Message = CommandArg()):
    arglist=args.extract_plain_text().split()
    if len(arglist)==4:
        matcher.set_arg('content',Message(arglist[0]))
        matcher.set_arg('time',Message(arglist[1]+' '+arglist[2]+' '+arglist[3]))
    elif len(arglist)==1:
        matcher.set_arg('content',Message(arglist[0]))
    elif len(arglist)!=0:
        await interval_note.finish("请通过指令note_help查询正确输入格式")

@interval_note.got('content',prompt='请输入您想记事的内容：')
async def _(matcher:Matcher,content:str=ArgPlainText('content')):
    pass

@interval_note.got('time',prompt='请输入间隔记事的时间：')
async def _(matcher:Matcher,event:Event,time:str=ArgPlainText('time')):
    try:
        time_list=time.split()
        hour=int(time_list[0])
        minute=int(time_list[1])
        second=int(time_list[2])
    except:
        await interval_note.finish("请通过指令note_help查询正确输入格式")

    content=matcher.get_arg('content').extract_plain_text()
    id=event.get_user_id()
    
    ban=await read_ban()
    if id in ban.get("users"):
            await interval_note.finish("抱歉，您在记事黑名单内，不能进行记事")
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"试图记事"+content))
            await interval_note.finish("您此次记事触犯了禁用词，记事失败")
    
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    if content in config.get(id):
        await interval_note.finish("已存在相同内容的记事，请重新输入")
    
    job_id=id+'-'+content
    scheduler.add_job(func=note_job,trigger="interval",hours=hour,minutes=minute,seconds=second,args=[content,id],id=job_id)
    config.get(id).append(content)
    job_dict=await read_unfinished_job()
    parameter_list=['interval',id,hour,minute,second,content]
    temp_job={job_id:parameter_list}
    job_dict.update(temp_job)
    await load_unfinished_job(job_dict)
    await load_config(config)
    if id in spy:
        for user in superusers:
            await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+content))
    await interval_note.finish("成功记事，接下来将每隔{}小时{}分钟{}秒提醒您一次：{}".format(hour,minute,second,content))



#创建cron_note
@cron_note.handle()
async def _(matcher:Matcher,args:Message = CommandArg()):
    arglist=args.extract_plain_text().split()
    if 1<len(arglist)<7:
        matcher.set_arg('content',Message(arglist[0]))
        try:
            time=Message('')
            time+=Message(arglist[1])
            time+=Message(' '+arglist[2])
            time+=Message(' '+arglist[3])
            time+=Message(' '+arglist[4])
        except:
            pass
        matcher.set_arg('time',time)
    elif len(arglist)==1:
        matcher.set_arg('content',Message(arglist[0]))
    elif len(arglist)>6:
        await cron_note.finish("请通过指令note_help查询正确输入格式")

@cron_note.got('content',prompt='请输入您想记事的内容：')
async def _(matcher:Matcher,content:str=ArgPlainText('content')):
    pass

@cron_note.got('time',prompt='请输入定时记事的时间：')
async def _(matcher:Matcher,event:Event,time:str=ArgPlainText('time')):
    time_list=time.split()
    content=matcher.get_arg('content').extract_plain_text()
    id=event.get_user_id()
    ban=await read_ban()
    if id in ban.get("users"):
        await cron_note.finish("抱歉，您在记事黑名单内，不能进行记事")
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"试图记事"+content))
            await cron_note.finish("您此次记事触犯了禁用词，记事失败")
    
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    if content in config.get(id):
        await cron_note.finish("已存在相同内容的记事，请重新输入")

    job_id=id+'-'+content
    if len(time_list)==1:
        try:
            second=int(time_list[0])
        except:
            await cron_note.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=note_job,trigger="cron",second=second,args=[content,id],id=job_id)
        config.get(id).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['cron',id,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+content))
        await cron_note.send("成功记事，接下来将在每分的{}秒提醒您：{}".format(second,content))
    if len(time_list)==2:
        try:
            minute=int(time_list[0])
            second=int(time_list[1])
        except:
            await cron_note.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=note_job,trigger="cron",minute=minute,second=second,args=[content,id],id=job_id)
        config.get(id).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['cron',id,minute,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+content))
        await cron_note.send("成功记事，接下来将在每时的{}分{}秒提醒您：{}".format(minute,second,content))
    if len(time_list)==3:
        try:
            hour=int(time_list[0])
            minute=int(time_list[1])
            second=int(time_list[2])
        except:
            await cron_note.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=note_job,trigger="cron",hour=hour,minute=minute,second=second,args=[content,id],id=job_id)
        config.get(id).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['cron',id,hour,minute,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+content))
        await cron_note.send("成功记事，接下来将在每天的{}时{}分{}秒提醒您：{}".format(hour,minute,second,content))
    if len(time_list)==4:
        try:
            hour=int(time_list[1])
            minute=int(time_list[2])
            second=int(time_list[3])
        except:
            await cron_note.finish("请通过指令note_help查询正确输入格式")
        try:
            day=int(time_list[0])
            scheduler.add_job(func=note_job,trigger="cron",day=day,hour=hour,minute=minute,second=second,args=[content,id],id=job_id)
            config.get(id).append(content)
            job_dict=await read_unfinished_job()
            parameter_list=['cron',id,day,hour,minute,second,content]
            temp_job={job_id:parameter_list}
            job_dict.update(temp_job)
            await load_unfinished_job(job_dict)
            await load_config(config)
            if id in spy:
                for user in superusers:
                    await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+content))
            await cron_note.send("成功记事，接下来将每月的{}日{}时{}分{}秒提醒您：{}".format(day,hour,minute,second,content))
        except:
            dow=time_list[0]
            if dow in ["mon","tue","wed","thu","fri","sat","sun"]:
                scheduler.add_job(func=note_job,trigger="cron",day_of_week=dow,hour=hour,minute=minute,second=second,args=[content,id],id=job_id)
                config.get(id).append(content)
                job_dict=await read_unfinished_job()
                parameter_list=['cron',id,dow,hour,minute,second,content]
                temp_job={job_id:parameter_list}
                job_dict.update(temp_job)
                await load_unfinished_job(job_dict)
                await load_config(config)
                await cron_note.send("成功记事，接下来将每周的{}日{}时{}分{}秒提醒您：{}".format(dow,hour,minute,second,content))
            else:
                await cron_note.finish("请通过指令note_help查询正确输入格式")



#创建date_note
@date_note.handle()
async def _(matcher:Matcher,args:Message = CommandArg()):
    arglist=args.extract_plain_text().split()
    if len(arglist)==7:
        matcher.set_arg('content',Message(arglist[0]))
        matcher.set_arg('time',Message(arglist[1]+' '+arglist[2]+' '+arglist[3]+' '+arglist[4]+' '+arglist[5]+' '+arglist[6]))
    elif len(arglist)==5:
        matcher.set_arg('content',Message(arglist[0]))
        matcher.set_arg('time',Message(arglist[1]+' '+arglist[2]+' '+arglist[3]+' '+arglist[4]))
    elif len(arglist)==1:
        matcher.set_arg('content',Message(arglist[0]))
    elif len(arglist)!=0:
        await date_note.finish("请通过指令note_help查询正确输入格式")

@date_note.got('content',prompt='请输入您想记事的内容：')
async def _(matcher:Matcher,content:str=ArgPlainText('content')):
    pass

@date_note.got('time',prompt='请输入单次记事的时间：')
async def _(matcher:Matcher,event:Event,time:str=ArgPlainText('time')):
    time_list=time.split()
    if len(time_list)==4 and time_list[0] in ['今天','明天','后天','大后天']:
        date=dt.datetime.now()+dt.timedelta(['今天','明天','后天','大后天'].index(time_list[0]))
        time_list.append(time_list[2])
        time_list.append(time_list[3])
        time_list[3]=time_list[1]
        time_list[0]=str(date.year)
        time_list[1]=str(date.month)
        time_list[2]=str(date.day)
    content=matcher.get_arg('content').extract_plain_text()
    id=event.get_user_id()
    ban=await read_ban()
    if id in ban.get("users"):
            await date_note.finish("抱歉，您在记事黑名单内，不能进行记事")
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"试图记事"+content))
            await date_note.finish("您此次记事触犯了禁用词，记事失败")
    
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    if content in config.get(id):
        await date_note.finish("已存在相同内容的记事，请重新输入")
    
    try:
        year=int(time_list[0])
        month=int(time_list[1])
        day=int(time_list[2])
        hour=int(time_list[3])
        minute=int(time_list[4])
        second=int(time_list[5])
    except:
        await date_note.finish("请通过指令note_help查询正确输入格式")

    if datetime.now()>datetime(year,month,day,hour,minute,second):
        await date_note.finish("定时时间存在于过去，请重新输入")
    else:
        job_id=id+'-'+content
        scheduler.add_job(func=note_job,trigger="date",run_date=datetime(year,month,day,hour,minute,second),args=[content,id],id=job_id)
        scheduler.add_job(func=list_delete,trigger="date",run_date=datetime(year,month,day,hour,minute,second),args=[content,id])
        config.get(id).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['date',id,year,month,day,hour,minute,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+content))
        await date_note.send("成功记事，将在{}年{}月{}日{}时{}分{}秒提醒您：{}".format(year,month,day,hour,minute,second,content))



async def ingroup(id:int):
    group_infos=await nonebot.get_bot().call_api('get_group_list')
    for group_info in group_infos:
        if group_info.get('group_id')==id:
            return True
    return False
    
async def isfriend(id:int):
    friend_infos=await nonebot.get_bot().call_api('get_friend_list')
    for friend_info in friend_infos:
        if friend_info.get('user_id')==id:
            return True
    return False



@interval_note_other.handle()
async def _(matcher:Matcher,event:Event,args:Message=CommandArg()):
    arglist=args.extract_plain_text().split()
    if len(arglist)==5:
        matcher.set_arg('qq_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        matcher.set_arg('time',Message(arglist[2]+' '+arglist[3]+' '+arglist[4]))
    elif len(arglist)==2:
        matcher.set_arg('qq_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
    elif len(arglist)==1:
        matcher.set_arg('qq_id',Message(arglist[0]))
    elif len(arglist)!=0:
        await interval_note.finish("请通过指令note_help查询正确输入格式")

@interval_note_other.got('qq_id',prompt='请输入您想提醒的qq：')
async def _(matcher:Matcher,qq_id:str=ArgPlainText('qq_id')):
    if not await isfriend(int(qq_id)):
        await interval_note_other.finish('请先将{}添加为bot的好友！'.format(qq_id))

@interval_note_other.got('content',prompt='请输入您想记事的内容：')
async def _(matcher:Matcher,content:str=ArgPlainText('content')):
    pass

@interval_note_other.got('time',prompt='请输入间隔记事的时间：')
async def _(matcher:Matcher,event:Event,time:str=ArgPlainText('time')):
    try:
        time_list=time.split()
        hour=int(time_list[0])
        minute=int(time_list[1])
        second=int(time_list[2])
    except:
        await interval_note_other.finish("请通过指令note_help查询正确输入格式")

    content=matcher.get_arg('content').extract_plain_text()
    id=str(matcher.get_arg('qq_id'))
    
    ban=await read_ban()
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(event.get_user_id()+"试图记事"+content))
            await interval_note_other.finish("您此次记事触犯了禁用词，记事失败")
    
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    if content in config.get(id):
        await interval_note_other.finish("已存在相同内容的记事，请重新输入")
    
    job_id=id+'-'+content
    scheduler.add_job(func=note_job,trigger="interval",hours=hour,minutes=minute,seconds=second,args=[content,id],id=job_id)
    config.get(id).append(content)
    job_dict=await read_unfinished_job()
    parameter_list=['interval',id,hour,minute,second,content]
    temp_job={job_id:parameter_list}
    job_dict.update(temp_job)
    await load_unfinished_job(job_dict)
    await load_config(config)
    info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
    name=info.get('nickname')
    await interval_note_other.finish("成功记事，接下来将每隔{}小时{}分钟{}秒提醒{}({})一次：{}".format(hour,minute,second,name,id,content))



@cron_note_other.handle()
async def _(matcher:Matcher,event:Event,args:Message=CommandArg()):
    arglist=args.extract_plain_text().split()
    if 2<len(arglist)<8:
        matcher.set_arg('qq_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        try:
            time=Message('')
            time+=Message(' '+arglist[2])
            time+=Message(' '+arglist[3])
            time+=Message(' '+arglist[4])
            time+=Message(' '+arglist[5])
        except:
            pass
        matcher.set_arg('time',time)
    elif len(arglist)==2:
        matcher.set_arg('qq_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
    elif len(arglist)==1:
        matcher.set_arg('qq_id',Message(arglist[0]))
    elif len(arglist)>7:
        await cron_note.finish("请通过指令note_help查询正确输入格式")

@cron_note_other.got('qq_id',prompt='请输入您想提醒的qq：')
async def _(matcher:Matcher,qq_id:str=ArgPlainText('qq_id')):
    if not await isfriend(int(qq_id)):
        await cron_note_other.finish('请先将{}添加为bot的好友！'.format(qq_id))

@cron_note_other.got('content',prompt='请输入您想记事的内容：')
async def _(matcher:Matcher,content:str=ArgPlainText('content')):
    pass

@cron_note_other.got('time',prompt='请输入定时记事的时间：')
async def _(matcher:Matcher,event:Event,time:str=ArgPlainText('time')):
    time_list=time.split()
    content=matcher.get_arg('content').extract_plain_text()
    id=str(matcher.get_arg('qq_id'))
    ban=await read_ban()
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(event.get_user_id()+"试图记事"+content))
            await cron_note_other.finish("您此次记事触犯了禁用词，记事失败")
    
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    if content in config.get(id):
        await cron_note_other.finish("已存在相同内容的记事，请重新输入")

    job_id=id+'-'+content   
    if len(time_list)==1:
        try:
            second=int(time_list[0])
        except:
            await cron_note_other.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=note_job,trigger="cron",second=second,args=[content,id],id=job_id)
        config.get(id).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['cron',id,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
        name=info.get('nickname')
        await cron_note_other.finish("成功记事，接下来将在每分的{}秒提醒{}({})：{}".format(second,name,id,content))
    if len(time_list)==2:
        try:
            minute=int(time_list[0])
            second=int(time_list[1])
        except:
            await cron_note_other.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=note_job,trigger="cron",minute=minute,second=second,args=[content,id],id=job_id)
        config.get(id).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['cron',id,minute,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
        name=info.get('nickname')
        await cron_note_other.finish("成功记事，接下来将每时的{}分{}秒提醒{}({})：{}".format(minute,second,name,id,content))
    if len(time_list)==3:
        try:
            hour=int(time_list[0])
            minute=int(time_list[1])
            second=int(time_list[2])
        except:
            await cron_note_other.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=note_job,trigger="cron",hour=hour,minute=minute,second=second,args=[content,id],id=job_id)
        config.get(id).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['cron',id,hour,minute,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
        name=info.get('nickname')
        await cron_note_other.finish("成功记事，接下来将每天的{}时{}分{}秒提醒{}({})：{}".format(hour,minute,second,name,id,content))
    if len(time_list)==4:
        try:
            hour=int(time_list[1])
            minute=int(time_list[2])
            second=int(time_list[3])
        except:
            await cron_note_other.finish("请通过指令note_help查询正确输入格式")
        try:
            day=int(time_list[0])
            scheduler.add_job(func=note_job,trigger="cron",day=day,hour=hour,minute=minute,second=second,args=[content,id],id=job_id)
            config.get(id).append(content)
            job_dict=await read_unfinished_job()
            parameter_list=['cron',id,day,hour,minute,second,content]
            temp_job={job_id:parameter_list}
            job_dict.update(temp_job)
            await load_unfinished_job(job_dict)
            await load_config(config)
            info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
            name=info.get('nickname')
            await cron_note_other.finish("成功记事，接下来将每月的{}日{}时{}分{}秒提醒{}({})：{}".format(day,hour,minute,second,name,id,content))
        except:
            dow=time_list[0]
            if dow in ["mon","tue","wed","thu","fri","sat","sun"]:
                scheduler.add_job(func=note_job,trigger="cron",day_of_week=dow,hour=hour,minute=minute,second=second,args=[content,id],id=job_id)
                config.get(id).append(content)
                job_dict=await read_unfinished_job()
                parameter_list=['cron',id,dow,hour,minute,second,content]
                temp_job={job_id:parameter_list}
                job_dict.update(temp_job)
                await load_unfinished_job(job_dict)
                await load_config(config)
                info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
                name=info.get('nickname')
                await cron_note_other.finish("成功记事，接下来将每周的{}日{}时{}分{}秒提醒{}({})：{}".format(dow,hour,minute,second,name,id,content))
            else:
                await cron_note_other.finish("请通过指令note_help查询正确输入格式")



@date_note_other.handle()
async def _(matcher:Matcher,event:Event,args:Message=CommandArg()):
    arglist=args.extract_plain_text().split()
    if len(arglist)==8:
        matcher.set_arg('qq_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        matcher.set_arg('time',Message(arglist[2]+' '+arglist[3]+' '+arglist[4]+' '+arglist[5]+' '+arglist[6]+' '+arglist[7]))
    elif len(arglist)==6:
        matcher.set_arg('qq_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        matcher.set_arg('time',Message(arglist[2]+' '+arglist[3]+' '+arglist[4]+' '+arglist[5]))
    elif len(arglist)==2:
        matcher.set_arg('qq_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
    elif len(arglist)==1:
        matcher.set_arg('qq_id',Message(arglist[0]))
    elif len(arglist)!=0:
        await date_note_other.finish("请通过指令note_help查询正确输入格式")

@date_note_other.got('qq_id',prompt='请输入您想提醒的qq：')
async def _(matcher:Matcher,qq_id:str=ArgPlainText('qq_id')):
    if not await isfriend(int(qq_id)):
        await date_note_other.finish('请先将{}添加为bot的好友！'.format(qq_id))

@date_note_other.got('content',prompt='请输入您想记事的内容：')
async def _(matcher:Matcher,content:str=ArgPlainText('content')):
    pass

@date_note_other.got('time',prompt='请输入单次记事的时间：')
async def _(matcher:Matcher,event:Event,time:str=ArgPlainText('time')):
    time_list=time.split()
    if len(time_list)==4 and time_list[0] in ['今天','明天','后天','大后天']:
        date=dt.datetime.now()+dt.timedelta(['今天','明天','后天','大后天'].index(time_list[0]))
        time_list.append(time_list[2])
        time_list.append(time_list[3])
        time_list[3]=time_list[1]
        time_list[0]=str(date.year)
        time_list[1]=str(date.month)
        time_list[2]=str(date.day)
    content=matcher.get_arg('content').extract_plain_text()
    id=str(matcher.get_arg('qq_id'))
    ban=await read_ban()
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(event.get_user_id()+"试图记事"+content))
            await date_note_other.finish("您此次记事触犯了禁用词，记事失败")
    
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    if content in config.get(id):
        await date_note_other.finish("已存在相同内容的记事，请重新输入")
    
    try:
        year=int(time_list[0])
        month=int(time_list[1])
        day=int(time_list[2])
        hour=int(time_list[3])
        minute=int(time_list[4])
        second=int(time_list[5])
    except:
        await date_note_other.finish("请通过指令note_help查询正确输入格式")

    if datetime.now()>datetime(year,month,day,hour,minute,second):
        await date_note_other.finish("定时时间存在于过去，请重新输入")
    else:
        job_id=id+'-'+content
        scheduler.add_job(func=note_job,trigger="date",run_date=datetime(year,month,day,hour,minute,second),args=[content,id],id=job_id)
        scheduler.add_job(func=list_delete,trigger="date",run_date=datetime(year,month,day,hour,minute,second),args=[content,id])
        config.get(id).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['date',id,year,month,day,hour,minute,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
        name=info.get('nickname')
        await date_note_other.finish("成功记事，将在{}年{}月{}日{}时{}分{}秒提醒{}({})：{}".format(year,month,day,hour,minute,second,name,id,content))



@interval_note_group.handle()
async def _(matcher:Matcher,event:Event,args:Message=CommandArg()):
    arglist=args.extract_plain_text().split()
    if len(arglist)==5:
        matcher.set_arg('group_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        matcher.set_arg('time',Message(arglist[2]+' '+arglist[3]+' '+arglist[4]))
    elif len(arglist)==2:
        matcher.set_arg('group_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
    elif len(arglist)==1:
        matcher.set_arg('group_id',Message(arglist[0]))
    elif len(arglist)!=0:
        await interval_note.finish("请通过指令note_help查询正确输入格式")

@interval_note_group.got('group_id',prompt='请输入您想提醒的qq群：')
async def _(matcher:Matcher,group_id:str=ArgPlainText('group_id')):
    if not await ingroup(int(group_id)):
        await interval_note_group.finish("请先将bot加入群{}！".format(group_id))

@interval_note_group.got('content',prompt='请输入您想记事的内容：')
async def _(matcher:Matcher,content:str=ArgPlainText('content')):
    pass

@interval_note_group.got('time',prompt='请输入间隔记事的时间：')
async def _(matcher:Matcher,event:Event,time:str=ArgPlainText('time')):
    try:
        time_list=time.split()
        hour=int(time_list[0])
        minute=int(time_list[1])
        second=int(time_list[2])
    except:
        await interval_note_group.finish("请通过指令note_help查询正确输入格式")

    content=matcher.get_arg('content').extract_plain_text()
    id=str(matcher.get_arg('group_id'))
    if id[0]=='0':
        id=id.replace('0','',1)
    nid='0'+id
    
    ban=await read_ban()
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(event.get_user_id()+"试图记事"+content))
            await interval_note_group.finish("您此次记事触犯了禁用词，记事失败")
    
    config=await read_config()
    if not config.get(nid):
        temp_dict={nid:[]}
        config.update(temp_dict)
    if content in config.get(nid):
        await interval_note_group.finish("已存在相同内容的记事，请重新输入")
    
    job_id=nid+'-'+content
    scheduler.add_job(func=group_note_job,trigger="interval",hours=hour,minutes=minute,seconds=second,args=[content,id],id=job_id)
    config.get(nid).append(content)
    job_dict=await read_unfinished_job()
    parameter_list=['interval',nid,hour,minute,second,content]
    temp_job={job_id:parameter_list}
    job_dict.update(temp_job)
    await load_unfinished_job(job_dict)
    await load_config(config)
    info=await nonebot.get_bot().call_api("get_group_info",group_id=id)
    name=info.get('group_name')
    await interval_note_group.finish("成功记事，接下来将每隔{}小时{}分钟{}秒在群:{}({})提醒一次：{}".format(hour,minute,second,name,id,content))



@cron_note_group.handle()
async def _(matcher:Matcher,event:Event,args:Message=CommandArg()):
    arglist=args.extract_plain_text().split()
    if 2<len(arglist)<8:
        matcher.set_arg('group_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        try:
            time=Message('')
            time+=Message(' '+arglist[2])
            time+=Message(' '+arglist[3])
            time+=Message(' '+arglist[4])
            time+=Message(' '+arglist[5])
        except:
            pass
        matcher.set_arg('time',time)
    elif len(arglist)==2:
        matcher.set_arg('group_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
    elif len(arglist)==1:
        matcher.set_arg('group_id',Message(arglist[0]))
    elif len(arglist)>7:
        await cron_note.finish("请通过指令note_help查询正确输入格式")

@cron_note_group.got('group_id',prompt='请输入您想提醒的qq群：')
async def _(matcher:Matcher,group_id:str=ArgPlainText('group_id')):
    if not await ingroup(int(group_id)):
        await cron_note_group.finish("请先将bot加入群{}！".format(group_id))

@cron_note_group.got('content',prompt='请输入您想记事的内容：')
async def _(matcher:Matcher,content:str=ArgPlainText('content')):
    pass

@cron_note_group.got('time',prompt='请输入定时记事的时间：')
async def _(matcher:Matcher,event:Event,time:str=ArgPlainText('time')):
    time_list=time.split()
    content=matcher.get_arg('content').extract_plain_text()
    id=str(matcher.get_arg('group_id'))
    if id[0]=='0':
        id=id.replace('0','',1)
    nid='0'+id
    ban=await read_ban()
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(event.get_user_id()+"试图记事"+content))
            await cron_note_group.finish("您此次记事触犯了禁用词，记事失败")
    
    config=await read_config()
    if not config.get(nid):
        temp_dict={nid:[]}
        config.update(temp_dict)
    if content in config.get(nid):
        await cron_note_group.finish("已存在相同内容的记事，请重新输入")

    job_id=nid+'-'+content   
    if len(time_list)==1:
        try:
            second=int(time_list[0])
        except:
            await cron_note_group.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=group_note_job,trigger="cron",second=second,args=[content,id],id=job_id)
        config.get(nid).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['cron',nid,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        info=await nonebot.get_bot().call_api("get_group_info",group_id=id)
        name=info.get('group_name')
        await cron_note_group.finish("成功记事，接下来将在每分的{}秒在群:{}({})里提醒:{}".format(second,name,id,content))
    if len(time_list)==2:
        try:
            minute=int(time_list[0])
            second=int(time_list[1])
        except:
            await cron_note_group.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=group_note_job,trigger="cron",minute=minute,second=second,args=[content,id],id=job_id)
        config.get(nid).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['cron',nid,minute,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        info=await nonebot.get_bot().call_api("get_group_info",group_id=id)
        name=info.get('group_name')
        await cron_note_group.finish("成功记事，接下来将在每时的{}分{}秒在群:{}({})里提醒:{}".format(minute,second,name,id,content))
    if len(time_list)==3:
        try:
            hour=int(time_list[0])
            minute=int(time_list[1])
            second=int(time_list[2])
        except:
            await cron_note_group.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=group_note_job,trigger="cron",hour=hour,minute=minute,second=second,args=[content,id],id=job_id)
        config.get(nid).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['cron',nid,hour,minute,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        info=await nonebot.get_bot().call_api("get_group_info",group_id=id)
        name=info.get('group_name')
        await cron_note_group.finish("成功记事，接下来将在每天的{}时{}分{}秒在群:{}({})里提醒:{}".format(hour,minute,second,name,id,content))
    if len(time_list)==4:
        try:
            hour=int(time_list[1])
            minute=int(time_list[2])
            second=int(time_list[3])
        except:
            await cron_note_group.finish("请通过指令note_help查询正确输入格式")
        try:
            day=int(time_list[0])
            scheduler.add_job(func=group_note_job,trigger="cron",day=day,hour=hour,minute=minute,second=second,args=[content,id],id=job_id)
            config.get(nid).append(content)
            job_dict=await read_unfinished_job()
            parameter_list=['cron',nid,day,hour,minute,second,content]
            temp_job={job_id:parameter_list}
            job_dict.update(temp_job)
            await load_unfinished_job(job_dict)
            await load_config(config)
            info=await nonebot.get_bot().call_api("get_group_info",group_id=id)
            name=info.get('group_name')
            await cron_note_group.finish("成功记事，接下来将在每月的{}天{}时{}分{}秒在群:{}({})里提醒:{}".format(day,hour,minute,second,name,id,content))
        except:
            dow=time_list[0]
            if dow in ["mon","tue","wed","thu","fri","sat","sun"]:
                scheduler.add_job(func=group_note_job,trigger="cron",day_of_week=dow,hour=hour,minute=minute,second=second,args=[content,id],id=job_id)
                config.get(nid).append(content)
                job_dict=await read_unfinished_job()
                parameter_list=['cron',nid,dow,hour,minute,second,content]
                temp_job={job_id:parameter_list}
                job_dict.update(temp_job)
                await load_unfinished_job(job_dict)
                await load_config(config)
                info=await nonebot.get_bot().call_api("get_group_info",group_id=id)
                name=info.get('group_name')
                await cron_note_group.finish("成功记事，接下来将在每周的{}日{}时{}分{}秒在群:{}({})里提醒:{}".format(dow,hour,minute,second,name,id,content))
            else:
                await cron_note_group.finish("请通过指令note_help查询正确输入格式")



@date_note_group.handle()
async def _(matcher:Matcher,event:Event,args:Message=CommandArg()):
    arglist=args.extract_plain_text().split()
    if len(arglist)==8:
        matcher.set_arg('group_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        matcher.set_arg('time',Message(arglist[2]+' '+arglist[3]+' '+arglist[4]+' '+arglist[5]+' '+arglist[6]+' '+arglist[7]))
    elif len(arglist)==6:
        matcher.set_arg('group_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        matcher.set_arg('time',Message(arglist[2]+' '+arglist[3]+' '+arglist[4]+' '+arglist[5]))
    elif len(arglist)==2:
        matcher.set_arg('group_id',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
    elif len(arglist)==1:
        matcher.set_arg('group_id',Message(arglist[0]))
    elif len(arglist)!=0:
        await date_note_group.finish("请通过指令note_help查询正确输入格式")

@date_note_group.got('group_id',prompt='请输入您想提醒的qq：')
async def _(matcher:Matcher,group_id:str=ArgPlainText('group_id')):
    if not await ingroup(int(group_id)):
        await date_note_group.finish("请先将bot加入群{}！".format(group_id))

@date_note_group.got('content',prompt='请输入您想记事的内容：')
async def _(matcher:Matcher,content:str=ArgPlainText('content')):
    pass

@date_note_group.got('time',prompt='请输入单次记事的时间：')
async def _(matcher:Matcher,event:Event,time:str=ArgPlainText('time')):
    time_list=time.split()
    if len(time_list)==4 and time_list[0] in ['今天','明天','后天','大后天']:
        date=dt.datetime.now()+dt.timedelta(['今天','明天','后天','大后天'].index(time_list[0]))
        time_list.append(time_list[2])
        time_list.append(time_list[3])
        time_list[3]=time_list[1]
        time_list[0]=str(date.year)
        time_list[1]=str(date.month)
        time_list[2]=str(date.day)
    content=matcher.get_arg('content').extract_plain_text()
    id=str(matcher.get_arg('group_id'))
    if id[0]=='0':
        id=id.replace('0','',1)
    nid='0'+id
    ban=await read_ban()
    for word in ban.get("words"):
        if word in content:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(event.get_user_id()+"试图记事"+content))
            await date_note_group.finish("您此次记事触犯了禁用词，记事失败")
    
    config=await read_config()
    if not config.get(nid):
        temp_dict={nid:[]}
        config.update(temp_dict)
    if content in config.get(nid):
        await date_note_group.finish("已存在相同内容的记事，请重新输入")
    
    try:
        year=int(time_list[0])
        month=int(time_list[1])
        day=int(time_list[2])
        hour=int(time_list[3])
        minute=int(time_list[4])
        second=int(time_list[5])
    except:
        await date_note_group.finish("请通过指令note_help查询正确输入格式")

    if datetime.now()>datetime(year,month,day,hour,minute,second):
        await date_note_group.finish("定时时间存在于过去，请重新输入")
    else:
        job_id=nid+'-'+content
        scheduler.add_job(func=group_note_job,trigger="date",run_date=datetime(year,month,day,hour,minute,second),args=[content,id],id=job_id)
        scheduler.add_job(func=list_delete,trigger="date",run_date=datetime(year,month,day,hour,minute,second),args=[content,nid])
        config.get(nid).append(content)
        job_dict=await read_unfinished_job()
        parameter_list=['date',nid,year,month,day,hour,minute,second,content]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        info=await nonebot.get_bot().call_api("get_group_info",group_id=id)
        name=info.get('group_name')
        await date_note_group.send("成功记事，将在{}年{}月{}日{}时{}分{}秒在群：{}({})里提醒：{}".format(year,month,day,hour,minute,second,name,id,content))



#重启note任务
@scheduler.scheduled_job("interval",seconds = 5,id='restart')
async def _restart():
    try:
        if note_restart_notice:
            for superuser in superusers:
                await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message('记事项目重启中……'))
    except:
        return
    scheduler.remove_job(job_id='restart')
    with open(unfinished_job_name,'r',encoding='utf-8') as f:
        unfinished_job=load(f.read(),Loader=Loader)
        job_id_list=unfinished_job.keys()
        for job_id in job_id_list:
            if scheduler.get_job(job_id=job_id):
                continue
            parameter=unfinished_job.get(job_id)

            if parameter[1][0]=='0':
                group_id=parameter[1].replace('0','',1)
                if note_restart_notice:
                    info=await nonebot.get_bot().call_api("get_group_info",group_id=group_id)
                    name=info.get('group_name')
                if parameter[0]=='interval':
                    scheduler.add_job(func=group_note_job,trigger='interval',hours=parameter[2],minutes=parameter[3],seconds=parameter[4],args=[parameter[5],group_id],id=job_id)
                    if note_restart_notice:
                        for superuser in superusers:
                            await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将每隔{}小时{}分钟{}秒提醒群：{}({})一次：{}".format(parameter[2],parameter[3],parameter[4],name,group_id,parameter[5])))
                if parameter[0]=='cron':
                    if len(parameter)==4:
                        scheduler.add_job(func=group_note_job,trigger='cron',second=parameter[2],args=[parameter[3],group_id],id=job_id)
                        if note_restart_notice:
                            for superuser in superusers:    
                                await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每分的{}秒提醒群：{}({})：{}".format(parameter[2],name,group_id,parameter[3])))
                    if len(parameter)==5:
                        scheduler.add_job(func=group_note_job,trigger='cron',minute=parameter[2],second=parameter[3],args=[parameter[4],group_id],id=job_id)
                        if note_restart_notice:    
                            for superuser in superusers:    
                                await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每时的{}分{}秒提醒群：{}({})：{}".format(parameter[2],parameter[3],name,group_id,parameter[4])))
                    if len(parameter)==6:
                        scheduler.add_job(func=group_note_job,trigger='cron',hour=parameter[2],minute=parameter[3],second=parameter[4],args=[parameter[5],group_id],id=job_id)
                        if note_restart_notice:
                            for superuser in superusers:    
                                await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每天的{}时{}分{}秒提醒群：{}({})：{}".format(parameter[2],parameter[3],parameter[4],name,group_id,parameter[5])))
                    if len(parameter)==7:
                        try:
                            int(parameter[2])
                            scheduler.add_job(func=group_note_job,trigger='cron',day=parameter[2],hour=parameter[3],minute=parameter[4],second=parameter[5],args=[parameter[6],group_id],id=job_id)
                            if note_restart_notice:
                                for superuser in superusers:    
                                    await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每月的{}日的{}时{}分{}秒提醒群：{}({})：{}".format(parameter[2],parameter[3],parameter[4],parameter[5],name,group_id,parameter[6])))
                        except:
                            scheduler.add_job(func=group_note_job,trigger='cron',day_of_week=parameter[2],hour=parameter[3],minute=parameter[4],second=parameter[5],args=[parameter[6],group_id],id=job_id)
                            if note_restart_notice:    
                                for superuser in superusers:    
                                    await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每月的{}日的{}时{}分{}秒提醒群：{}({})：{}".format(parameter[2],parameter[3],parameter[4],parameter[5],name,group_id,parameter[6])))
                if parameter[0]=='date':
                    if datetime.now()>datetime(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7]):
                        await list_delete(parameter[8],'0'+group_id)
                        await nonebot.get_bot().send_group_msg(group_id=group_id,message=Message("本应在{}年{}月{}日{}时{}分{}秒提醒：{}，现在已过期，可以重新进行记事".format(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7],parameter[8])))
                    else:
                        scheduler.add_job(func=group_note_job,trigger='date',run_date=datetime(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7]),args=[parameter[8],group_id],id=job_id)
                        scheduler.add_job(func=list_delete,trigger='date',run_date=datetime(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7]),args=[parameter[8],'0'+group_id])
                        if note_restart_notice:
                            for superuser in superusers:    
                                await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，将在{}年{}月{}日{}时{}分{}秒提醒群：{}({})：{}".format(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7],name,group_id,parameter[8])))



            else:
                user_id=parameter[1]
                if note_restart_notice:
                    info=await nonebot.get_bot().call_api("get_stranger_info",user_id=user_id)
                    name=info.get('nickname')
                if parameter[0]=='interval':
                    scheduler.add_job(func=note_job,trigger='interval',hours=parameter[2],minutes=parameter[3],seconds=parameter[4],args=[parameter[5],user_id],id=job_id)
                    if note_restart_notice:
                        for superuser in superusers:    
                            await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将每隔{}小时{}分钟{}秒提醒{}({})一次：{}".format(parameter[2],parameter[3],parameter[4],name,user_id,parameter[5])))
                if parameter[0]=='cron':
                    if len(parameter)==4:
                        scheduler.add_job(func=note_job,trigger='cron',second=parameter[2],args=[parameter[3],user_id],id=job_id)
                        if note_restart_notice:
                            for superuser in superusers:    
                                await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每分的{}秒提醒{}({})：{}".format(parameter[2],name,user_id,parameter[3])))
                    if len(parameter)==5:
                        scheduler.add_job(func=note_job,trigger='cron',minute=parameter[2],second=parameter[3],args=[parameter[4],user_id],id=job_id)
                        if note_restart_notice:
                            for superuser in superusers:    
                                await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每时的{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],name,user_id,parameter[4])))
                    if len(parameter)==6:
                        scheduler.add_job(func=note_job,trigger='cron',hour=parameter[2],minute=parameter[3],second=parameter[4],args=[parameter[5],user_id],id=job_id)
                        if note_restart_notice:    
                            for superuser in superusers:    
                                await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每天的{}时{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],parameter[4],name,user_id,parameter[5])))
                    if len(parameter)==7:
                        try:
                            int(parameter[2])
                            scheduler.add_job(func=note_job,trigger='cron',day=parameter[2],hour=parameter[3],minute=parameter[4],second=parameter[5],args=[parameter[6],user_id],id=job_id)
                            if note_restart_notice:
                                for superuser in superusers:    
                                    await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每月的{}日的{}时{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],parameter[4],parameter[5],name,user_id,parameter[6])))
                        except:
                            scheduler.add_job(func=note_job,trigger='cron',day_of_week=parameter[2],hour=parameter[3],minute=parameter[4],second=parameter[5],args=[parameter[6],user_id],id=job_id)
                            if note_restart_notice:
                                for superuser in superusers:    
                                    await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每月的{}日的{}时{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],parameter[4],parameter[5],name,user_id,parameter[6])))
                if parameter[0]=='date':
                    if datetime.now()>datetime(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7]):
                        await list_delete(parameter[8],user_id)
                        await nonebot.get_bot().send_private_msg(user_id=user_id,message=Message("本应在{}年{}月{}日{}时{}分{}秒提醒您：{}，现在已过期，您可以重新进行记事".format(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7],parameter[8])))
                    else:
                        scheduler.add_job(func=note_job,trigger='date',run_date=datetime(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7]),args=[parameter[8],user_id],id=job_id)
                        scheduler.add_job(func=list_delete,trigger='date',run_date=datetime(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7]),args=[parameter[8],user_id])
                        if note_restart_notice:
                            for superuser in superusers:    
                                await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，将在{}年{}月{}日{}时{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7],name,user_id,parameter[8])))
        f.close()
    if note_restart_notice:
        for superuser in superusers:
            await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("已成功重启所有的记事项目"))



#删除note
@note_delete.handle()
async def _(matcher:Matcher,event:Event,args:Message = CommandArg()):
    if args:
        matcher.set_arg('content',args)

@note_delete.got('content',prompt='请输入您想删除的内容：')
async def _(matcher:Matcher,event:Event,content:str=ArgPlainText('content')):
    config=await read_config()
    id=event.get_user_id()
    if config.get(id):
        if content in config.get(id):
            config.get(id).remove(content)
            job_id=id+'-'+content
            unfinished_job=await read_unfinished_job()
            if job_id in unfinished_job.keys():
                unfinished_job.pop(job_id)
                scheduler.remove_job(job_id=job_id)
                await load_unfinished_job(unfinished_job)
            await load_config(config)
            await note_delete.finish("已成功删除记事内容："+content)
        else:
            await note_delete.finish("没有找到该记事内容")
    else:
        await note_delete.finish("您还没有记事过，请先进行一次记事")



#列出note
@note_list.handle()
async def _(event:Event):
    id=event.get_user_id()
    config=await read_config()
    info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
    name=info.get('nickname')
    notes=name+"("+id+")"+"的记事列表："
    if config.get(id):
        for note in config.get(id):
            notes+="\n"+"→"+note
        if note_type=='text':
            await note_check.finish(notes)
        else:
            cur_dir = os.path.dirname(os.path.abspath(__file__)) 
            if path.exists(r"{}/data/list.png".format(cur_dir)):
                os.remove(r"{}/data/list.png".format(cur_dir))
            await CreateMutiLinesPic(notes,30,r"{}\data\list.png".format(cur_dir))
            await note_list.finish(MessageSegment.image(file=r"file:///{}\data\list.png".format(cur_dir)))
    else:
        await note_list.finish("您还没有记事过，请先进行一次记事")



#检查某人或所有note
@note_check.handle()
async def _(matcher:Matcher,args:Message = CommandArg()):
    if args:
        matcher.set_arg('id',args)

@note_check.got('id',prompt='请输入您想检查的qq(qq群在群号前加个0)：')
async def _(matcher:Matcher,event:Event,id:str=ArgPlainText('id')):
    config=await read_config()
    notes=""
    texts=""
    if id=="all" or id=="所有":
        if len(config.keys())==0:
            await note_check.finish("还没有任何人进行过记事！")
        for ids in config.keys():
            notes=""
            for note in config.get(ids):
                notes=notes+"\n"+"→"+note
            if ids[0]=='0':
                group_id=ids.replace('0','',1)
                info=await nonebot.get_bot().call_api("get_group_info",group_id=group_id)
                names=info.get('group_name')
                texts+='群：'+names+"("+group_id+")"+"的记事列表："+notes+'\n'
            else:
                info=await nonebot.get_bot().call_api("get_stranger_info",user_id=ids)
                names=info.get('nickname')
                texts+=names+"("+ids+")"+"的记事列表："+notes+'\n'
    else:
        if config.get(id):
            for note in config.get(id):
                notes=notes+"\n"+"→"+note
            if id[0]=='0':
                group_id=id.replace('0','',1)
                info=await nonebot.get_bot().call_api("get_group_info",group_id=group_id)
                name=info.get('group_name')
                texts+='群：'+name+"("+group_id+")"+"的记事列表："+notes+'\n'
            else:
                info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
                name=info.get('nickname')
                texts+=name+"("+id+")"+"的记事列表："+notes
        else:
            await note_check.finish(id+"还没有进行过记事")

    if note_type=='text':
        await note_check.finish(texts)
    else:
        cur_dir = os.path.dirname(os.path.abspath(__file__)) 
        if path.exists(r"{}/data/check.png".format(cur_dir)):
            os.remove(r"{}/data/check.png".format(cur_dir))
        await CreateMutiLinesPic(texts,30,r"{}/data/check.png".format(cur_dir))
        await note_check.finish(MessageSegment.image(file=r"file:///{}/data/check.png".format(cur_dir)))



#移除某条note
@note_remove.handle()
async def _(matcher:Matcher,args:Message = CommandArg()):
    arglist=args.extract_plain_text().split()
    if len(arglist)==3:
        matcher.set_arg('nid',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        matcher.set_arg('type',Message(arglist[2]))
    if len(arglist)==2:
        matcher.set_arg('nid',Message(arglist[0]))
        matcher.set_arg('content',Message(arglist[1]))
        matcher.set_arg('type',Message('visibly'))
    if len(arglist)==1:
        matcher.set_arg('nid',Message(arglist[0]))

@note_remove.got('nid',prompt='请输入您想移除记事内容的qq(qq群在群号前加个0)：')
async def _(matcher:Matcher,event:Event,nid:str=ArgPlainText('nid')):
    if nid[0]=='0':
        matcher.set_arg('type',Message('否'))

@note_remove.got('content',prompt='请输入您想移除的记事内容：')
async def _(matcher:Matcher,event:Event,content:str=ArgPlainText('content')):
    pass

@note_remove.got('type',prompt='是否提醒被移除内容的人？(是/否)')
async def _(matcher:Matcher,event:Event,type:str=ArgPlainText('type')):
    nid=str(matcher.get_arg('nid'))
    content=matcher.get_arg('content').extract_plain_text()
    config=await read_config()
    if config.get(nid):
        
        if content in config.get(nid):
            config.get(nid).remove(content)
            job_id=nid+'-'+content
            unfinished_job=await read_unfinished_job()
            if job_id in unfinished_job.keys():
                unfinished_job.pop(job_id)
                scheduler.remove_job(job_id=job_id)
                await load_unfinished_job(unfinished_job)
            await load_config(config)
            if nid[0]!='0' and (type=='v' or type=='visibly' or type=='是'):
                await nonebot.get_bot().send_private_msg(user_id=nid,message=Message('您的记事项目“'+content+'”已被superuser移除'))
            if nid[0]=='0':
                info=await nonebot.get_bot().call_api("get_group_info",group_id=nid.replace('0','',1))
                name=info.get('group_name')
                await note_delete.finish("已成功移除群：{}({})的记事内容：{}".format(name,nid.replace('0','',1),content))
            else:
                info=await nonebot.get_bot().call_api("get_stranger_info",user_id=nid)
                name=info.get('nickname')
                await note_delete.finish("已成功移除{}({})的记事内容：{}".format(name,nid,content))
        else:
            if nid[0]=='0':
                info=await nonebot.get_bot().call_api("get_group_info",group_id=nid.replace('0','',1))
                name=info.get('group_name')
                await note_delete.finish("没有找到群：{}({})的该记事内容".format(name,nid.replace('0','',1)))
            else:
                info=await nonebot.get_bot().call_api("get_stranger_info",user_id=nid)
                name=info.get('nickname')
                await note_delete.finish("没有找到{}({})的该记事内容".format(name,nid))
    else:
        await note_delete.finish(nid+"还没有进行过记事")



#监视某人的note
@note_spy.handle()
async def _(args:Message=CommandArg()):
    if str(args).isdigit():
        if str(args) not in spy:
            spy.append(str(args))
            await note_spy.finish(str(args)+"已加入监控对象列表")
        else:
            await note_spy.finish(str(args)+"已经在监控对象里了")
    else:
        await note_spy.finish("请通过指令note_help查询正确输入格式")



#移除对某人的监视
@note_spy_remove.handle()
async def _(args:Message=CommandArg()):
    try:
        int(str(args))
    except:
        await note_spy_remove.finish("请输入正确的QQ号！")
    if str(args) in spy:
        spy.remove(str(args))
        await note_spy_remove.finish(str(args)+"已移除监控对象列表")
    else:
        await note_spy_remove.finish(str(args)+"不在监控对象里")



#添加禁用词或黑名单
@note_ban.handle()
async def _(args:Message=CommandArg()):
    arg=args.extract_plain_text().split()
    if len(arg)==2:
        if arg[0]==str(1) or arg[0]=='word':
            ban=await read_ban()
            if arg[1] in ban.get("words"):
                await note_ban.finish("已存在此禁用词")
            else:
                ban.get("words").append(arg[1])
                await load_ban(ban)
                await note_ban.finish("成功添加禁用词："+arg[1])
        if arg[0]==str(2) or arg[0]=='user':
            try:
                int(arg[1])
            except:
                await note_ban.finish("请通过指令note_help查询正确输入格式")
            ban=await read_ban()
            if arg[1] in ban.get("users"):
                await note_ban.finish("此人已在黑名单里")
            else:
                ban.get("users").append(arg[1])
                await load_ban(ban)
                await note_ban.finish("成功添加黑名单："+arg[1])
    await note_ban.finish("请通过指令note_help查询正确输入格式")



#列出ban
@note_ban_list.handle()
async def _():
    ban=await read_ban()
    temp=""
    temp+="禁用词：\n"
    for word in ban.get("words"):
        temp+=word+"\n"
    temp+="\n黑名单：\n"
    for user in ban.get("users"):
        temp+=user+"\n"
    temp+="\n展示完毕！"
    await note_ban_list.finish(temp)



#取消禁用词或黑名单
@note_ban_remove.handle()
async def _(args:Message=CommandArg()):
    arg=args.extract_plain_text().split()
    if len(arg)==2:
        if arg[0]==str(1) or arg[0]=='word':
            ban=await read_ban()
            if arg[1] in ban.get("words"):
                ban.get("words").remove(arg[1])
                await load_ban(ban)
                await note_ban.finish("已移除禁用词："+arg[1])
            else:
                await note_ban.finish(arg[1]+"不是禁用词")
        if arg[0]==str(2) or arg[0]=='user':
            try:
                int(arg[1])
            except:
                await note_ban_remove.finish("请通过指令note_help查询正确输入格式")
            ban=await read_ban()
            if arg[1] in ban.get("users"):
                ban.get("users").remove(arg[1])
                await load_ban(ban)
                await note_ban.finish("已移除黑名单："+arg[1])
            else:
                await note_ban.finish(arg[1]+"不在黑名单内")
    await note_ban.finish("请通过指令note_help查询正确输入格式")



#note帮助
@note_help.handle()
async def _(event:Event):
    superuser_msg="""
这是一个有提醒功能的记事本~\n
输入命令'note/记事/记事本 [记事内容]'进行记事\n
输入命令'interval_note/间隔记事/间隔记事本 [记事内容] [时] [分] [秒]'，我将每隔[时][分][秒]提醒您一次\n
输入命令'cron_note/定时记事/定时记事本 [记事内容] (日)/(mon/tue/wed/thu/fri/sat/sun) ([时]) ([分]) [秒]'，我将在每月的[日][时][分][秒]/每周的[星期x][时][分][秒]/每天的[时][分][秒]/每时的[分][秒]/每分的[秒]提醒您一次\n
输入命令'date_note/单次记事/单次记事本 [记事内容] [年] [月] [日](或今天/明天/后天/大后天) [时] [分] [秒]'，我将在这个时刻提醒您\n
输入命令'note_list/记事列表/记事本列表'来查看记事列表\n
输入命令'note_delete/记事删除/记事本删除 [记事内容]'来删除一个记事项目\n
\n\n
以下命令需要SUPERUSERS才能使用：\n
输入命令'note_check/记事查看/记事本查看 [QQ账号(QQ群在群号前加个0)]/all'来查看某人/所有的记事项目\n
输入命令'note_remove/记事移除/记事本移除 [QQ账号(QQ群在群号前加个0)] [记事内容]'来移除某人的某项记事内容\n
输入命令'note_spy/记事监控/记事本监控 [QQ账号]'来监控某人的记事记录\n
输入命令'note_spy_remove/记事监控移除/记事本监控移除 [QQ账号]'来移除对某人的监控\n
输入命令'note_ban/记事禁止/记事本禁止 1/2(word/user) [内容]'来设置禁用词/黑名单\n
输入命令'note_ban_list/记事禁止列表/记事本禁止列表'来查看禁用词和黑名单\n
输入命令'note_ban_remove/记事禁止移除/记事本禁止移除 1/2(word/user) [内容]'来移除禁用词/黑名单\n
输入命令'interval_note_other/间隔记事他人/间隔记事本他人 [QQ账号] [记事内容] [时] [分] [秒]'来给某人添加interval_note\n
输入命令'cron_note_other/定时记事他人/定时记事本他人 [QQ账号] [记事内容] (日)/(mon/tue/wed/thu/fri/sat/sun) ([时]) ([分]) [秒]'来给某人添加cron_note\n
输入命令'date_note_other/单次记事他人/单次记事本他人 [QQ账号] [记事内容] [年] [月] [日](或今天/明天/后天/大后天) [时] [分] [秒]'来给某人添加date_note\n
输入命令'interval_note_group/群间隔记事/群间隔记事本 [QQ群号] [记事内容] [时] [分] [秒]'来给某群添加interval_note\n
输入命令'cron_note_group/群定时记事/群定时记事本 [QQ群号] [记事内容] (日)/(mon/tue/wed/thu/fri/sat/sun) ([时]) ([分]) [秒]'来给某群添加cron_note\n
输入命令'date_note_group/群单次记事/群单次记事本 [QQ群号] [记事内容] [年] [月] [日](或今天/明天/后天/大后天) [时] [分] [秒]'来给某群添加date_note\n

*注：如果[记事内容]中需要有空格的话，可以分布使用命令(即直接使用指令不带参数)\n
\n\n
"""
    user_msg="""
这是一个有提醒功能的记事本~\n
输入命令'note/记事/记事本 [记事内容]'进行记事\n
输入命令'interval_note/间隔记事/间隔记事本 [记事内容] [时] [分] [秒]'，我将每隔[时][分][秒]提醒您一次\n
输入命令'cron_note/定时记事/定时记事本 [记事内容] (日)/(mon/tue/wed/thu/fri/sat/sun) ([时]) ([分]) [秒]'，我将在每月的[日][时][分][秒]/每周的[星期x][时][分][秒]/每天的[时][分][秒]/每时的[分][秒]/每分的[秒]提醒您一次\n
输入命令'date_note/单次记事/单次记事本 [记事内容] [年] [月] [日](或今天/明天/后天/大后天) [时] [分] [秒]'，我将在这个时刻提醒您\n
输入命令'note_list/记事列表/记事本列表'来查看记事列表\n
输入命令'note_delete/记事删除/记事本删除 [记事内容]'来删除一个记事项目\n

*注：如果[记事内容]中需要有空格的话，可以一步一步用命令\n
\n\n
"""
    if note_type=='text':
        if event.get_user_id() in superusers:
            await note_help.finish(superuser_msg)
        else:
            await note_help.finish(user_msg)
    else:
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        if event.get_user_id() in superusers:
            if path.exists(r"{}/data/superuser-help.png".format(cur_dir)):
                os.remove(r"{}/data/superuser-help.png".format(cur_dir))
            await CreateMutiLinesPic(superuser_msg,70,r"{}/data/superuser-help.png".format(cur_dir))
            await note_help.finish(MessageSegment.image(file=r"file:///{}/data/superuser-help.png".format(cur_dir)))
        else:
            if path.exists(r"{}/data/user-help.png".format(cur_dir)):
                os.remove(r"{}/data/user-help.png".format(cur_dir))
            await CreateMutiLinesPic(user_msg,70,r"{}/data/user-help.png".format(cur_dir))
            await note_help.finish(MessageSegment.image(file=r"file:///{}/data/user-help.png".format(cur_dir)))



#定时发消息
async def note_job(msg:str,id:str):
    #print(msg)  #调试
    await nonebot.get_bot().send_private_msg(user_id=id,message=Message(msg))

async def group_note_job(msg:str,id:str):
    print(msg)  #调试
    await nonebot.get_bot().send_group_msg(group_id=id,message=Message(msg))



#定时删除date_note
async def list_delete(note_to_remove:str,id:str):
    config=await read_config()
    unfinished_job=await read_unfinished_job()
    config.get(id).remove(note_to_remove)
    unfinished_job.pop(id+'-'+note_to_remove)
    await load_config(config)
    await load_unfinished_job(unfinished_job)


async def read_config():
    with open(config_name,'r',encoding='utf-8')as f:
        temp_config=load(f.read(),Loader=Loader)
        f.close()
    return temp_config


async def load_config(config_to_load):
    with open(config_name,'w',encoding='utf-8') as f:
        f.write(dump(config_to_load,allow_unicode=True))
        f.close()


async def read_unfinished_job():
    with open(unfinished_job_name,'r',encoding='utf-8') as f:
        temp_job=load(f.read(),Loader=Loader)
        f.close()
    return temp_job


async def load_unfinished_job(job_to_load):
    with open(unfinished_job_name,'w',encoding='utf-8') as f:
        f.write(dump(job_to_load,allow_unicode=True))
        f.close()


async def read_ban():
    with open(ban_name,'r',encoding='utf-8') as f:
        temp_word=load(f.read(),Loader=Loader)
        f.close()
    return temp_word


async def load_ban(word_to_load):
    with open(ban_name,'w',encoding='utf-8') as f:
        f.write(dump(word_to_load,allow_unicode=True))
        f.close()


async def CreateMutiLinesPic(text,line_size,pic_path):

    count=0
    for i in text:
        if i=="\n":
            blank_size=line_size-count%line_size
            text=text.replace(i,blank_size*' ',1)
            count+=blank_size
        else:
            count+=1  

    font_conf = {
        'type':'simkai.ttf',
        'size':20,
        'rgb':tuple(note_font_color)
    }
    bg_conf = {
        'rgb':tuple(note_bg_color)
    }
    margin=50

    line_count=math.ceil(len(text)/line_size)

    font = ImageFont.truetype(font_conf['type'],font_conf['size'])

    # calculate the picture size
    fwidth,fheight = font.getsize('中'*line_size)
    owidth,oheight = font.getoffset('中'*line_size)
    pic_size=[margin*2+fwidth+owidth,margin*2+(fheight+oheight)*line_count]

    # create new picture
    pic = Image.new('RGB', pic_size,bg_conf['rgb'])
    draw = ImageDraw.Draw(pic)
    for i in range(line_count):
        # draw lines
        draw.text((margin,margin+(fheight+oheight)*i), text[i*line_size:(i+1)*line_size], font_conf['rgb'], font)
    if pic_path:
        pic.save(pic_path)
