from datetime import datetime
import time
import math
from os import path,makedirs
import os
from PIL import Image, ImageDraw, ImageFont
import nonebot
from nonebot import require
require("nonebot_plugin_apscheduler")
timing = require("nonebot_plugin_apscheduler").scheduler
from nonebot_plugin_apscheduler import scheduler
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event,Message,MessageSegment
from nonebot.params import CommandArg
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
note_font_color=[65,105,225]
note_bg_color=[225,225,0]


# 获取env配置
try:
    nonebot.logger.debug(nonebot.get_driver().config.note_font_color)
    nonebot.logger.debug(nonebot.get_driver().config.note_bg_color)
    note_font_color = nonebot.get_driver().config.note_font_color if nonebot.get_driver().config.note_font_color!= "" else [65,105,225]
    note_bg_color = nonebot.get_driver().config.note_bg_color if nonebot.get_driver().config.note_bg_color != "" else [225,225,0]
except:
    nonebot.logger.debug("note插件部分配置缺失，采用默认配置。")

try:
    note_type=nonebot.get_driver().config.note_type
except:
    note_type='image'

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
interval_note=on_command(cmd="interval_note",aliases={"间隔记事","间隔记事本"},priority=99,block=True)
cron_note=on_command(cmd="cron_note",aliases={"定时记事","定时记事本"},priority=99,block=True)
date_note=on_command(cmd="date_note",aliases={"单次记事","单次记事本"},priority=99,block=True)

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


#创建note
@note.handle()
async def _note(event:Event,args:Message = CommandArg()):
    if str(args)=='':
        await note.finish("请通过指令note_help查询正确输入格式")
    id=event.get_user_id()
    ban=await read_ban()
    if id in ban.get("users"):
        await note.finish("抱歉，您在记事黑名单内，不能进行记事")
    for word in ban.get("words"):
        if word in str(args):
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"试图记事"+str(args)))
            await note.finish("您此次记事触犯了禁用词，记事失败")
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    if str(args) in config.get(id):
        await note.finish("已存在相同内容的记事，请重新输入")
    else:
        config.get(id).append(str(args))
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+str(args)))
        await note.finish("成功记事，您可以通过note_list指令查看记事列表")


#创建interval_note
@interval_note.handle()
async def _interval(event:Event,args:Message = CommandArg(),other_id:int=0):
    if other_id:
        id=str(other_id)
    else:
        id=event.get_user_id()
    arg=args.extract_plain_text().split()
    ban=await read_ban()
    if id in ban.get("users"):
        await note.finish("抱歉，您在记事黑名单内，不能进行记事")
    for word in ban.get("words"):
        if word in arg[0]:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"试图记事"+arg[0]))
            await note.finish("您此次记事触犯了禁用词，记事失败")
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    if arg[0] in config.get(id):
        await interval_note.finish("已存在相同内容的记事，请重新输入")
    if len(arg)==4:
        try:
            int(arg[1])
            int(arg[2])
            int(arg[3])
        except:
            await interval_note.finish("请通过指令note_help查询正确输入格式")
        job_id=id+'-'+arg[0]
        scheduler.add_job(func=note_job,trigger="interval",hours=int(arg[1]),minutes=int(arg[2]),seconds=int(arg[3]),args=[arg[0],id],id=job_id)
        config.get(id).append(arg[0])
        job_dict=await read_unfinished_job()
        parameter_list=['interval',id,int(arg[1]),int(arg[2]),int(arg[3]),arg[0]]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+arg[0]))
        if other_id:
            info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
            name=info.get('nickname')
            await interval_note.send("成功记事，接下来将每隔{}小时{}分钟{}秒提醒{}({})一次：{}".format(arg[1],arg[2],arg[3],name,id,arg[0]))
        else:
            await interval_note.send("成功记事，接下来将每隔%s小时%s分钟%s秒提醒您一次：%s"%(arg[1],arg[2],arg[3],arg[0]))
    else:
        await interval_note.finish("请通过指令note_help查询正确输入格式")


#创建cron_note
@cron_note.handle()
async def _cron(event:Event,args:Message = CommandArg(),other_id:int = 0):
    if other_id:
        id=str(other_id)
    else:
        id=event.get_user_id()
    arg=args.extract_plain_text().split()
    ban=await read_ban()
    if id in ban.get("users"):
        await note.finish("抱歉，您在记事黑名单内，不能进行记事")
    for word in ban.get("words"):
        if word in arg[0]:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"试图记事"+arg[0]))
            await note.finish("您此次记事触犯了禁用词，记事失败")
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    job_id=id+'-'+arg[0]
    if arg[0] in config.get(id):
        await cron_note.finish("已存在同内容的记事，请重新输入")
    if len(arg)==2:
        try:
            int(arg[1])
        except:
            await cron_note.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=note_job,trigger="cron",second=arg[1],args=[arg[0],id],id=job_id)
        config.get(id).append(arg[0])
        job_dict=await read_unfinished_job()
        parameter_list=['cron',id,arg[1],arg[0]]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+arg[0]))
        if other_id:
            info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
            name=info.get('nickname')
            await cron_note.send("成功记事，接下来将在每分的{}秒提醒{}({})：{}".format(arg[1],name,id,arg[0]))
        else:
            await cron_note.send("成功记事，接下来将在每分的%s秒提醒您：%s"%(arg[1],arg[0]))
    if len(arg)==3:
        try:
            int(arg[1])
            int(arg[2])
        except:
            await cron_note.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=note_job,trigger="cron",minute=arg[1],second=arg[2],args=[arg[0],id],id=job_id)
        config.get(id).append(arg[0])
        job_dict=await read_unfinished_job()
        parameter_list=['cron',id,arg[1],arg[2],arg[0]]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+arg[0]))
        if other_id:
            info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
            name=info.get('nickname')
            await cron_note.send("成功记事，接下来将每时的{}分{}秒提醒{}({})：{}".format(arg[1],arg[2],name,id,arg[0]))
        else:
            await cron_note.send("成功记事，接下来将在每时的%s分%s秒提醒您：%s"%(arg[1],arg[2],arg[0]))
    if len(arg)==4:
        try:
            int(arg[1])
            int(arg[2])
            int(arg[3])
        except:
            await cron_note.finish("请通过指令note_help查询正确输入格式")
        scheduler.add_job(func=note_job,trigger="cron",hour=arg[1],minute=arg[2],second=arg[3],args=[arg[0],id],id=job_id)
        config.get(id).append(arg[0])
        job_dict=await read_unfinished_job()
        parameter_list=['cron',id,arg[1],arg[2],arg[3],arg[0]]
        temp_job={job_id:parameter_list}
        job_dict.update(temp_job)
        await load_unfinished_job(job_dict)
        await load_config(config)
        if id in spy:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+arg[0]))
        if other_id:
            info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
            name=info.get('nickname')
            await cron_note.send("成功记事，接下来将每天的{}时{}分{}秒提醒{}({})：{}".format(arg[1],arg[2],arg[3],name,id,arg[0]))
        else:
            await cron_note.send("成功记事，接下来将在每天的%s时%s分%s秒提醒您：%s"%(arg[1],arg[2],arg[3],arg[0]))
    if len(arg)==5:
        try:
            int(arg[2])
            int(arg[3])
            int(arg[4])
        except:
            await cron_note.finish("请通过指令note_help查询正确输入格式")
        try:
            int(arg[1])
            scheduler.add_job(func=note_job,trigger="cron",day=arg[1],hour=arg[2],minute=arg[3],second=arg[4],args=[arg[0],id],id=job_id)
            config.get(id).append(arg[0])
            job_dict=await read_unfinished_job()
            parameter_list=['cron',id,arg[1],arg[2],arg[3],arg[4],arg[0]]
            temp_job={job_id:parameter_list}
            job_dict.update(temp_job)
            await load_unfinished_job(job_dict)
            await load_config(config)
            if id in spy:
                for user in superusers:
                    await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+arg[0]))
            if other_id:
                info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
                name=info.get('nickname')
                await cron_note.send("成功记事，接下来将每月的{}日{}时{}分{}秒提醒{}({})：{}".format(arg[1],arg[2],arg[3],arg[4],name,id,arg[0]))
            else:
                await cron_note.send("成功记事，接下来将在每月的%s日%s时%s分%s秒提醒您：%s"%(arg[1],arg[2],arg[3],arg[4],arg[0]))
        except:
            if arg[1] in ["mon","tue","wed","thu","fri","sat","sun"]:
                scheduler.add_job(func=note_job,trigger="cron",day_of_week=arg[1],hour=arg[2],minute=arg[3],second=arg[4],args=[arg[0],id],id=job_id)
                config.get(id).append(arg[0])
                job_dict=await read_unfinished_job()
                parameter_list=['cron',id,arg[1],arg[2],arg[3],arg[4],arg[0]]
                temp_job={job_id:parameter_list}
                job_dict.update(temp_job)
                await load_unfinished_job(job_dict)
                await load_config(config)
                if id in spy:
                    for user in superusers:
                        await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+arg[0]))
                if other_id:
                    info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
                    name=info.get('nickname')
                    await cron_note.send("成功记事，接下来将每周的{}日{}时{}分{}秒提醒{}({})：{}".format(arg[1],arg[2],arg[3],arg[4],name,id,arg[0]))
                else:
                    await cron_note.send("成功记事，接下来将在每周的%s日%s时%s分%s秒提醒您：%s"%(arg[1],arg[2],arg[3],arg[4],arg[0]))
            else:
                await cron_note.finish("请通过指令note_help查询正确输入格式")
    if len(arg)<2 or len(arg)>5:
        await cron_note.finish("请通过指令note_help查询正确输入格式")


#创建date_note
@date_note.handle()
async def _date(event:Event,args:Message = CommandArg(),other_id:int =0):
    if other_id:
        id=str(other_id)
    else:
        id=event.get_user_id()
    arg=args.extract_plain_text().split()
    ban=await read_ban()
    if id in ban.get("users"):
        await note.finish("抱歉，您在记事黑名单内，不能进行记事")
    for word in ban.get("words"):
        if word in arg[0]:
            for user in superusers:
                await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"试图记事"+arg[0]))
            await note.finish("您此次记事触犯了禁用词，记事失败")
    config=await read_config()
    if not config.get(id):
        temp_dict={id:[]}
        config.update(temp_dict)
    job_id=id+'-'+arg[0]
    if arg[0] in config.get(id):
        await date_note.finish("已存在相同内容的记事，请重新输入")
    year=None
    month=None
    day=None
    hour=None
    minute=None
    second=None
    n=len(arg)
    if n==5:
        try:
            hour=int(arg[2])
            minute=int(arg[3])
            second=int(arg[4])
        except:
            await date_note.finish("请通过指令note_help查询正确输入格式")
        if arg[1]=='今天':
            year=datetime.now().year
            month=datetime.now().month
            day=datetime.now().day
            n+=2
        if arg[1]=='明天':
            year=datetime.now().year
            month=datetime.now().month
            day=datetime.now().day+1
            n+=2
        if arg[1]=='后天':
            year=datetime.now().year
            month=datetime.now().month
            day=datetime.now().day+2
            n+=2
        if arg[1]=='大后天':
            year=datetime.now().year
            month=datetime.now().month
            day=datetime.now().day+3
            n+=2
    if n==7:
        if year==None:
            year=arg[1]
        if month==None:
            month=arg[2]
        if day==None:
            day=arg[3]
        if hour==None:
            hour=arg[4]
        if minute==None:
            minute=arg[5]
        if second==None:
            second=arg[6]
        try:
            year=int(year)
            month=int(month)
            day=int(day)
            hour=int(hour)
            minute=int(minute)
            second=int(second)
        except:
            await date_note.finish("请通过指令note_help查询正确输入格式")
        if datetime.now()>datetime(year,month,day,hour,minute,second):
            await date_note.finish("定时时间存在于过去，请重新输入")
        else:
            scheduler.add_job(func=note_job,trigger="date",run_date=datetime(year,month,day,hour,minute,second),args=[arg[0],id],id=job_id)
            scheduler.add_job(func=list_delete,trigger="date",run_date=datetime(year,month,day,hour,minute,second),args=[arg[0],id])
            config.get(id).append(arg[0])
            job_dict=await read_unfinished_job()
            parameter_list=['date',id,year,month,day,hour,minute,second,arg[0]]
            temp_job={job_id:parameter_list}
            job_dict.update(temp_job)
            await load_unfinished_job(job_dict)
            await load_config(config)
            if id in spy:
                for user in superusers:
                    await nonebot.get_bot().send_private_msg(user_id=user,message=Message(id+"进行了记事："+arg[0]))
            if other_id:
                info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
                name=info.get('nickname')
                await date_note.send("成功记事，将在{}年{}月{}日{}时{}分{}秒提醒{}({})：{}".format(year,month,day,hour,minute,second,name,id,arg[0]))
            else:
                await date_note.send("成功记事，将在{}年{}月{}日{}时{}分{}秒提醒您：{}".format(year,month,day,hour,minute,second,arg[0]))
    else:
        await date_note.finish("请通过指令note_help查询正确输入格式")

    
async def isfriend(id:int):
    friend_infos=await nonebot.get_bot().call_api('get_friend_list')
    for friend_info in friend_infos:
        if friend_info.get('user_id')==id:
            return True
    return False

@interval_note_other.handle()
async def _(event:Event,args:Message=CommandArg()):
    arg_list=args.extract_plain_text().split()
    try:
        other_id=int(arg_list[0])
    except:
        await interval_note_other.finish("请通过指令note_help查询正确输入格式")
    if not await isfriend(other_id):
        await interval_note_other.finish('请先将{}添加为bot的好友！'.format(other_id))
    _args=''
    for arg in arg_list[1:]:
        _args+=arg+' '
    await _interval(event=event,args=Message(_args),other_id=other_id)


@cron_note_other.handle()
async def _(event:Event,args:Message=CommandArg()):
    arg_list=args.extract_plain_text().split()
    try:
        other_id=int(arg_list[0])
    except:
        await cron_note_other.finish("请通过指令note_help查询正确输入格式")
    if not await isfriend(other_id):
        await cron_note_other.finish('请先将{}添加为bot的好友！'.format(other_id))
    _args=''
    for arg in arg_list[1:]:
        _args+=arg+' '
    await _cron(event=event,args=Message(_args),other_id=other_id)


@date_note_other.handle()
async def _(event:Event,args:Message=CommandArg()):
    arg_list=args.extract_plain_text().split()
    try:
        other_id=int(arg_list[0])
    except:
        await date_note_other.finish("请通过指令note_help查询正确输入格式")
    if not await isfriend(other_id):
        await date_note_other.finish('请先将{}添加为bot的好友！'.format(other_id))
    _args=''
    for arg in arg_list[1:]:
        _args+=arg+' '
    await _date(event=event,args=Message(_args),other_id=other_id)



#重启note任务
@timing.scheduled_job("interval",seconds = 5,id='restart')
async def _restart():
    try:
        for superuser in superusers:
            await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message('记事项目重启中……'))
    except:
        return
    timing.remove_job(job_id='restart')
    with open(unfinished_job_name,'r',encoding='utf-8') as f:
        unfinished_job=load(f.read(),Loader=Loader)
        job_id_list=unfinished_job.keys()
        for job_id in job_id_list:
            if scheduler.get_job(job_id=job_id):
                continue
            parameter=unfinished_job.get(job_id)
            user_id=parameter[1]
            info=await nonebot.get_bot().call_api("get_stranger_info",user_id=user_id)
            name=info.get('nickname')
            if parameter[0]=='interval':
                scheduler.add_job(func=note_job,trigger='interval',hours=parameter[2],minutes=parameter[3],seconds=parameter[4],args=[parameter[5],user_id],id=job_id)
                for superuser in superusers:    
                    await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将每隔{}小时{}分钟{}秒提醒{}({})一次：{}".format(parameter[2],parameter[3],parameter[4],name,user_id,parameter[5])))
            if parameter[0]=='cron':
                if len(parameter)==4:
                    scheduler.add_job(func=note_job,trigger='cron',second=parameter[2],args=[parameter[3],user_id],id=job_id)
                    for superuser in superusers:    
                        await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每分的{}秒提醒{}({})：{}".format(parameter[2],name,user_id,parameter[3])))
                if len(parameter)==5:
                    scheduler.add_job(func=note_job,trigger='cron',minute=parameter[2],second=parameter[3],args=[parameter[4],user_id],id=job_id)
                    for superuser in superusers:    
                        await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每时的{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],name,user_id,parameter[4])))
                if len(parameter)==6:
                    scheduler.add_job(func=note_job,trigger='cron',hour=parameter[2],minute=parameter[3],second=parameter[4],args=[parameter[5],user_id],id=job_id)
                    for superuser in superusers:    
                        await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每天的{}时{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],parameter[4],name,user_id,parameter[5])))
                if len(parameter)==7:
                    try:
                        int(parameter[2])
                        scheduler.add_job(func=note_job,trigger='cron',day=parameter[2],hour=parameter[3],minute=parameter[4],second=parameter[5],args=[parameter[6],user_id],id=job_id)
                        for superuser in superusers:    
                            await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每月的{}日的{}时{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],parameter[4],parameter[5],name,user_id,parameter[6])))
                    except:
                        scheduler.add_job(func=note_job,trigger='cron',day_of_week=parameter[2],hour=parameter[3],minute=parameter[4],second=parameter[5],args=[parameter[6],user_id],id=job_id)
                        for superuser in superusers:    
                            await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，接下来将在每月的{}日的{}时{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],parameter[4],parameter[5],name,user_id,parameter[6])))
            if parameter[0]=='date':
                if datetime.now()>datetime(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7]):
                    await list_delete(parameter[8],user_id)
                    await nonebot.get_bot().send_private_msg(user_id=user_id,message=Message("本应在{}年{}月{}日{}时{}分{}秒提醒您：{}，现在已过期，您可以重新进行记事".format(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7],parameter[8])))
                else:
                    scheduler.add_job(func=note_job,trigger='date',run_date=datetime(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7]),args=[parameter[8],user_id],id=job_id)
                    scheduler.add_job(func=list_delete,trigger='date',run_date=datetime(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7]),args=[parameter[8],user_id])
                    for superuser in superusers:    
                        await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("重启成功，将在{}年{}月{}日{}时{}分{}秒提醒{}({})：{}".format(parameter[2],parameter[3],parameter[4],parameter[5],parameter[6],parameter[7],name,user_id,parameter[8])))
        f.close()
    for superuser in superusers:
        await nonebot.get_bot().send_private_msg(user_id=superuser,message=Message("已成功重启所有的记事项目"))


#删除note
@note_delete.handle()
async def _(event:Event,args:Message = CommandArg()):
    config=await read_config()
    id=event.get_user_id()
    if config.get(id):
        if str(args) in config.get(id):
            config.get(id).remove(str(args))
            job_id=id+'-'+str(args)
            unfinished_job=await read_unfinished_job()
            if job_id in unfinished_job.keys():
                unfinished_job.pop(job_id)
                scheduler.remove_job(job_id=job_id)
                await load_unfinished_job(unfinished_job)
            await load_config(config)      
            await note_delete.finish("已成功删除记事内容："+str(args))
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
    notes=name+"（"+id+"）"+"的记事列表："
    if config.get(id):
        for note in config.get(id):
            notes+="\n"+"*"+note
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
async def _(args:Message = CommandArg()):
    id=str(args)
    config=await read_config()
    notes=""
    texts=""
    if id=="all" or id=="所有":
        if len(config.keys())==0:
            await note_check.finish("还没有任何人进行过记事！")
        for ids in config.keys():
            notes=""
            for note in config.get(ids):
                notes=notes+"\n"+"*"+note
            info=await nonebot.get_bot().call_api("get_stranger_info",user_id=ids)
            names=info.get('nickname')
            texts+=names+"（"+ids+"）"+"的记事列表："+notes+'\n'
    else:
        if config.get(id):
            for note in config.get(id):
                notes=notes+"\n"+"*"+note
            info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
            name=info.get('nickname')
            texts+=name+"（"+id+"）"+"的记事列表："+notes
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
async def _(args:Message = CommandArg()):
    config=await read_config()
    arg=args.extract_plain_text().split()
    id=arg[0]
    if config.get(id):
        info=await nonebot.get_bot().call_api("get_stranger_info",user_id=id)
        name=info.get('nickname')
        if arg[1] in config.get(id):
            config.get(id).remove(arg[1])
            job_id=id+'-'+arg[1]
            unfinished_job=await read_unfinished_job()
            if job_id in unfinished_job.keys():
                unfinished_job.pop(job_id)
                scheduler.remove_job(job_id=job_id)
                await load_unfinished_job(unfinished_job)
            await load_config(config)
            await nonebot.get_bot().send_private_msg(user_id=id,message=Message('您的记事项目“'+arg[1]+'”已被superuser移除'))
            await note_delete.finish("已成功移除{}（{}）的记事内容：{}".format(name,id,arg[1]))
        else:
            await note_delete.finish("没有找到{}（{}）的该记事内容".format(name,id))
    else:
        await note_delete.finish(id+"还没有进行过记事")


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
输入命令'cron_note/定时记事/定时记事本 [记事内容] （日）/（mon/tue/wed/thu/fri/sat/sun） （[时]） （[分]） [秒]'，我将在每月的[日][时][分][秒]/每周的[星期x][时][分][秒]/每天的[时][分][秒]/每时的[分][秒]/每分的[秒]提醒您一次\n
输入命令'date_note/单次记事/单次记事本 [记事内容] [年] [月] [日]（或今天/明天/后天/大后天） [时] [分] [秒]'，我将在这个时刻提醒您\n
输入命令'note_list/记事列表/记事本列表'来查看记事列表\n
输入命令'note_delete/记事删除/记事本删除 [记事内容]'来删除一个记事项目\n\n\n
以下命令需要SUPERUSERS才能使用：\n
输入命令'note_check/记事查看/记事本查看 [QQ账号]/all'来查看某人/所有的记事项目\n
输入命令'note_remove/记事移除/记事本移除 [QQ账号] [记事内容]'来移除某人的某项记事内容\n
输入命令'note_spy/记事监控/记事本监控 [QQ账号]'来监控某人的记事记录\n
输入命令'note_spy_remove/记事监控移除/记事本监控移除 [QQ账号]'来移除对某人的监控\n
输入命令'note_ban/记事禁止/记事本禁止 1/2（word/user） [内容]'来设置禁用词/黑名单\n
输入命令'note_ban_list/记事禁止列表/记事本禁止列表'来查看禁用词和黑名单\n
输入命令'note_ban_remove/记事禁止移除/记事本禁止移除 1/2（word/user） [内容]'来移除禁用词/黑名单\n
输入命令'interval_note_other/间隔记事他人/间隔记事本他人 [QQ账号] [记事内容] [时] [分] [秒]'来给某人添加interval_note\n
输入命令'cron_note_other/定时记事他人/定时记事本他人 [QQ账号] [记事内容] （日）/（mon/tue/wed/thu/fri/sat/sun） （[时]） （[分]） [秒]'来给某人添加cron_note\n
输入命令'date_note_other/单次记事他人/单次记事本他人 [QQ账号] [记事内容] [年] [月] [日]（或今天/明天/后天/大后天） [时] [分] [秒]'来给某人添加date_note\n\n\n
"""
    user_msg="""
这是一个有提醒功能的记事本~\n
输入命令'note/记事/记事本 [记事内容]'进行记事\n
输入命令'interval_note/间隔记事/间隔记事本 [记事内容] [时] [分] [秒]'，我将每隔[时][分][秒]提醒您一次\n
输入命令'cron_note/定时记事/定时记事本 [记事内容] （日）/（mon/tue/wed/thu/fri/sat/sun） （[时]） （[分]） [秒]'，我将在每月的[日][时][分][秒]/每周的[星期x][时][分][秒]/每天的[时][分][秒]/每时的[分][秒]/每分的[秒]提醒您一次\n
输入命令'date_note/单次记事/单次记事本 [记事内容] [年] [月] [日]（或今天/明天/后天/大后天） [时] [分] [秒]'，我将在这个时刻提醒您\n
输入命令'note_list/记事列表/记事本列表'来查看记事列表\n
输入命令'note_delete/记事删除/记事本删除 [记事内容]'来删除一个记事项目\n\n\n
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
    print(msg)  #调试
    await nonebot.get_bot().send_private_msg(user_id=id,message=Message(msg))


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

# made by 路人丁
