import os
from nonebot import require,on_command
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Message,MessageEvent,Bot,GroupMessageEvent,MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.log import logger
import nonebot
from nonebot.adapters.onebot.v11.adapter import Adapter
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from pathlib import Path
import json
import random
from httpx import AsyncClient,Client
import asyncio
from .config import Config,__version__,website_list,config_dev
from .api import *


__plugin_meta__ = PluginMetadata(
    name="twitter 推特订阅",
    description="订阅 twitter 推文",
    usage="""
|     指令    |权限|需要@|   范围   | 说明 |
|   关注推主   |无 | 否  | 群聊/私聊 | 关注，指令格式：“关注推主 <推主id> [r18]” r18为可选参数，不开启和默认为不推送r18推文|
|   取关推主   |无 | 否  | 群聊/私聊 | 取关切割 |
|   推主列表   |无 | 否  | 群聊/私聊 | 展示列表 |
| 推文推送关闭 |群管| 否 | 群聊/私聊 | 关闭推送 |
| 推文推送开启 |群管| 否 | 群聊/私聊 | 开启推送 |
    """,
    type="application",
    config=Config,
    homepage="https://github.com/nek0us/nonebot-plugin-twitter",
    supported_adapters={"~onebot.v11"},
    extra={
        "author":"nek0us",
        "version":__version__,
        "priority":config_dev.command_priority
    }
)

web_list = []
if config_dev.twitter_website:
    logger.info("使用自定义 website")
    web_list.append(config_dev.twitter_website)
web_list += website_list


with Client(proxies=config_dev.twitter_proxy) as client:
    for url in web_list:
        try:
            res = client.get(url)
            if res.status_code == 200:
                logger.info(f"website: {url} ok!")
                config_dev.twitter_url = url
                break
            else:
                logger.info(f"website: {url} failed!")
        except Exception as e:
            logger.debug(f"website选择异常：{e}")
            continue
        


        
if config_dev.plugin_enabled:
    # Path
    dirpath = Path() / "data" / "twitter"
    dirpath.mkdir(parents=True, exist_ok=True)
    dirpath = Path() / "data" / "twitter" / "cache"
    dirpath.mkdir(parents=True, exist_ok=True)
    dirpath = Path() / "data" / "twitter" / "twitter_list.json"
    dirpath.touch()
    if not dirpath.stat().st_size:
        dirpath.write_text("{}")

    @scheduler.scheduled_job("interval",minutes=3,id="twitter",misfire_grace_time=180)
    async def now_twitter():
        twitter_list = json.loads(dirpath.read_text("utf8"))
        twitter_list_task = [
            get_status(user_name, twitter_list) for user_name in twitter_list
        ]
        asyncio.gather(*twitter_list_task)

        
def msg_type(user_id:int, task: str,name: str):
    return MessageSegment.node_custom(user_id=user_id, nickname=name,
                                          content=Message(MessageSegment.video(f"file:///{task}")))        
        
async def get_pic(url: str,user_name: str) -> MessageSegment:

    async with AsyncClient(proxies=config_dev.twitter_proxy) as client:
        res = await client.get(f"{config_dev.twitter_url}{url}")
        if res.status_code != 200:
            logger.info(f"图片下载失败:{url}")
            return MessageSegment.node_custom(user_id=config_dev.twitter_qq, nickname=user_name,
                                   content=Message(f"图片加载失败 X_X {url}"))
        return MessageSegment.node_custom(user_id=config_dev.twitter_qq, nickname=user_name,
                                   content=Message(MessageSegment.image(file=res.read())))



        
        
        
async def get_status(user_name,twitter_list):
    # 获取推文
    try:
        line_new_tweet_id = await get_user_newtimeline(user_name,twitter_list[user_name]["since_id"])
        if line_new_tweet_id and line_new_tweet_id != "not found":
            # update tweet
            tweet_info = await get_tweet(user_name,line_new_tweet_id)
            if not tweet_info["status"]:
                logger.info(f"{user_name} 的推文 {line_new_tweet_id} 获取失败")
                return 
            else:
                task = []
                task_res = []
                task_res.append(MessageSegment.node_custom(
                    user_id=config_dev.twitter_qq,
                    nickname=twitter_list[user_name]["screen_name"],
                    content=Message(tweet_info["text"])
                ))
                
                if tweet_info["pic_url_list"]:
                    for url in tweet_info["pic_url_list"]:
                        task_res.append(await get_pic(url,user_name))
                        
                # 视频
                if tweet_info["video_url"]:
                    task.append(get_video(tweet_info["video_url"]))
                    
                try:
                    path_res = await asyncio.gather(*task)
                except Exception as e:
                    logger.debug(f"下载媒体出现异常：{e}")
                    path_res = []
                task_res += [msg_type(config_dev.twitter_qq, path,name=user_name) for path in path_res]
                
                # 准备发送
                bots = nonebot.get_adapter(Adapter).bots
                for group_num in twitter_list[user_name]["group"]:
                    # 群聊
                    if twitter_list[user_name]["group"][group_num]["status"]:
                        if twitter_list[user_name]["group"][group_num]["r18"] == False and tweet_info["r18"] == True:
                            logger.info(f"根据r18设置，群 {group_num} 的推文 {user_name}/status/{line_new_tweet_id} 跳过发送")
                            continue
                        for bot in bots:
                            try:
                                await bots[bot].send_group_forward_msg(group_id=int(group_num), messages=task_res)
                                logger.info(f"群 {group_num} 的推文 {user_name}/status/{line_new_tweet_id} 发送成功")
                            except Exception:
                                pass
                    else:
                        logger.info(f"根据通知设置，群 {group_num} 的推文 {user_name}/status/{line_new_tweet_id} 跳过发送")
                        
                for qq in twitter_list[user_name]["private"]:
                    # 私聊
                    if twitter_list[user_name]["private"][qq]["status"]:
                        if twitter_list[user_name]["private"][qq]["r18"] == False and tweet_info["r18"] == True:
                            logger.info(f"根据r18设置，qq {qq} 的推文 {user_name}/status/{line_new_tweet_id} 跳过发送")   
                            continue
                        for bot in bots:
                            try:
                                await bots[bot].send_private_forward_msg(user_id=int(qq), messages=task_res)
                                logger.info(f"qq {qq} 的推文 {user_name}/status/{line_new_tweet_id} 发送成功")
                            except Exception:
                                pass
                    else:
                        logger.info(f"根据通知设置，qq {qq} 的推文 {user_name}/status/{line_new_tweet_id} 跳过发送")                    
                                    
                twitter_list[user_name]["since_id"] = line_new_tweet_id
                
                dirpath.write_text(json.dumps(twitter_list))

                # 清除垃圾
                await asyncio.sleep(80)
                for path in path_res:
                    os.unlink(path) 
                    os.unlink(path+".jpg")
    except Exception as e:
        logger.debug(f"出现异常：{e}")


save = on_command("关注推主",block=True,priority=config_dev.command_priority)
@save.handle()
async def save_handle(bot:Bot,event: MessageEvent,matcher: Matcher,arg: Message = CommandArg()):
    data = []
    if " " in arg.extract_plain_text():
        data = arg.extract_plain_text().split(" ")
    else:
        data.append(arg.extract_plain_text())
        data.append("")
    user_info = await get_user_info(data[0])
    
    if not user_info["status"]:
        await matcher.finish(f"未找到 {data[0]}")

    tweet_id = await get_user_newtimeline(data[0])
    
    twitter_list = json.loads(dirpath.read_text("utf8"))
    if isinstance(event,GroupMessageEvent):
        if data[0] not in twitter_list:
            twitter_list[data[0]] = {
                "group":{
                    str(event.group_id):{
                        "status":True,
                        "r18":True if data[1]=='r18' else False
                    }
                },
                "private":{}
            }
        else:
            twitter_list[data[0]]["group"][str(event.group_id)] = {
                        "status":True,
                        "r18":True if data[1]=='r18' else False
                    }
    else:
        if data[0] not in twitter_list:
            twitter_list[data[0]] = {
                "group":{},
                "private":{
                    str(event.user_id):{
                        "status":True,
                        "r18":True if data[0]=='r18' else False
                    }
                }
            }
        else:
            twitter_list[data[0]]["private"][str(event.user_id)] = {
                        "status":True,
                        "r18":True if data[1]=='r18' else False
                    }
            
    twitter_list[data[0]]["since_id"] = tweet_id
    twitter_list[data[0]]["screen_name"] = user_info["screen_name"]
    dirpath.write_text(json.dumps(twitter_list))
    await matcher.finish(f"id:{data[0]}\nname:{user_info['screen_name']}\n{user_info['bio']}\n订阅成功")
        

delete = on_command("取关推主",block=True,priority=config_dev.command_priority)
@delete.handle()
async def delete_handle(bot:Bot,event: MessageEvent,matcher: Matcher,arg: Message = CommandArg()):
    twitter_list = json.loads(dirpath.read_text("utf8"))
    if arg.extract_plain_text() not in twitter_list:
        await matcher.finish(f"未找到 {arg}")

    if isinstance(event,GroupMessageEvent):
        if str(event.group_id) not in twitter_list[arg.extract_plain_text()]["group"]:
            await matcher.finish(f"本群未订阅 {arg}")
            
        twitter_list[arg.extract_plain_text()]["group"].pop(str(event.group_id))
        
    else:
        if str(event.user_id) not in twitter_list[arg.extract_plain_text()]["private"]:
            await matcher.finish(f"未订阅 {arg}")
            
        twitter_list[arg.extract_plain_text()]["private"].pop(str(event.user_id))
    pop_list = []
    for user_name in twitter_list:
        if twitter_list[user_name]["group"] == {} and twitter_list[user_name]["private"] == {}:
            pop_list.append(user_name)
            
    for user_name in pop_list:
        twitter_list.pop(user_name)

    dirpath.write_text(json.dumps(twitter_list))
    
    await matcher.finish(f"取关 {arg.extract_plain_text()} 成功")
    
follow_list = on_command("推主列表",block=True,priority=config_dev.command_priority)
@follow_list.handle()
async def follow_list_handle(bot:Bot,event: MessageEvent,matcher: Matcher):
    
    twitter_list = json.loads(dirpath.read_text("utf8"))
    msg = []
    
    if isinstance(event,GroupMessageEvent):
        for user_name in twitter_list:
            if str(event.group_id) in twitter_list[user_name]["group"]:
                msg += [
                    MessageSegment.node_custom(
                        user_id=config_dev.twitter_qq, nickname=twitter_list[user_name]["screen_name"], content=Message(
                            f"{user_name}  {'r18' if twitter_list[user_name]['group'][str(event.group_id)]['r18'] else ''}"
                            )
                    )
                ]
        await bot.send_group_forward_msg(group_id=event.group_id, messages=msg)
    else:
        for user_name in twitter_list:
            if str(event.user_id) in twitter_list[user_name]["private"]:
                msg += [
                    MessageSegment.node_custom(
                        user_id=config_dev.twitter_qq, nickname=twitter_list[user_name]["screen_name"], content=Message(
                            f"{user_name}  {'r18' if twitter_list[user_name]['private'][str(event.user_id)]['r18'] else ''}"
                            )
                    )
                ]
        await bot.send_private_forward_msg(user_id=event.user_id, messages=msg)          
    
    await matcher.finish()


async def is_rule(event:MessageEvent) -> bool:
    if isinstance(event,GroupMessageEvent):
        if event.sender.role in ["owner","admin"]:
            return True
        return False
    else:
        return True
    
twitter_status = on_command("推文推送",block=True,rule=is_rule,priority=config_dev.command_priority)
@twitter_status.handle()
async def twitter_status_handle(bot:Bot,event: MessageEvent,matcher: Matcher,arg: Message = CommandArg()):
    twitter_list = json.loads(dirpath.read_text("utf8"))
    try:
        if isinstance(event,GroupMessageEvent):
            for user_name in twitter_list:
                if str(event.group_id) in twitter_list[user_name]["group"]:
                    if arg.extract_plain_text() == "开启":
                        twitter_list[user_name]["group"][str(event.group_id)]["status"] = True
                    elif arg.extract_plain_text() == "关闭":
                        twitter_list[user_name]["group"][str(event.group_id)]["status"] = False
                    else:
                        await matcher.finish("错误指令")
        else:
            for user_name in twitter_list:
                if str(event.user_id) in twitter_list[user_name]["private"]:
                    if arg.extract_plain_text() == "开启":
                        twitter_list[user_name]["private"][str(event.user_id)]["status"] = True
                    elif arg.extract_plain_text() == "关闭":
                        twitter_list[user_name]["private"][str(event.user_id)]["status"] = False
                    else:
                        await matcher.finish("错误指令")
        dirpath.write_text(json.dumps(twitter_list))
        await matcher.finish(f"推送已{arg.extract_plain_text()}")
    except FinishedException:
        pass
    except Exception as e:
        await matcher.finish(f"异常:{e}")

