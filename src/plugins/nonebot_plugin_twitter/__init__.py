import contextlib
import os
from nonebot import require,get_driver,get_bot,on_command
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Message,MessageEvent,Bot,GroupMessageEvent,MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.log import logger
import nonebot
from nonebot.adapters.onebot.v11.adapter import Adapter
from nonebot.exception import MatcherException
from nonebot.plugin import PluginMetadata
from pathlib import Path
import json
import random
from httpx import AsyncClient,Client
import asyncio
import tweepy
from .config import Config,__version__

#
config_dev = Config.parse_obj(get_driver().config)

__plugin_meta__ = PluginMetadata(
    name="twitter 推特订阅",
    description="订阅 twitter 推文",
    usage="""
|     指令    |权限|需要@|   范围   | 说明 |
|   关注推主   |无 | 否  | 群聊/私聊 | 关注，指令格式：“关注推主 <推主id> [r18]” r18为可选参数，不开启和默认为不推送r18推文|
|   取关推主   |无 | 否  | 群聊/私聊 | 取关切割 |
|   推主列表   |无 | 否  | 群聊/私聊 | 展示列表 |
| 推特推送关闭 |群管| 否 | 群聊/私聊 | 关闭推送 |
| 推特推送开启 |群管| 否 | 群聊/私聊 | 开启推送 |
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
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'}
if not config_dev.bearer_token:
    logger.warning("bearer_token 未配置")
    config_dev.plugin_enabled = False
        
if config_dev.plugin_enabled:
    # Path
    dirpath = Path() / "data" / "twitter"
    dirpath.mkdir(parents=True, exist_ok=True)
    dirpath = Path() / "data" / "twitter" / "cache"
    dirpath.mkdir(parents=True, exist_ok=True)
    dirpath = Path() / "data" / "twitter" / "group_list.json"
    dirpath.touch()
    if not dirpath.stat().st_size:
        dirpath.write_text("{}")
    pripath = Path() / "data" / "twitter" / "pri_list.json"
    pripath.touch()
    if not pripath.stat().st_size:
        pripath.write_text("{}")
    
    # Twitter token
    client = tweepy.Client(
        bearer_token=config_dev.bearer_token
    )     
    if config_dev.twitter_proxy:
        # twitter_proxy
        client.session.proxies = {
            "http":config_dev.twitter_proxy,
            "https":config_dev.twitter_proxy
        }
        logger.info(f"已读取 twitter proxy {client.session.proxies}")
    
    # Debug
    if config_dev.twitter_debug:
        try:
            logger.debug("连通性测试")
            if config_dev.twitter_proxy:
                logger.debug("twitter proxy 测试")
                with Client(proxies=f"http://{config_dev.twitter_proxy}") as client_test:
                    res = client_test.get("https://twitter.com/",headers=header)
                    if res.status_code == 200 or res.status_code == 302:
                        logger.debug(f"连通正常：{res.status_code}")
                    else:
                        logger.debug(f"连通异常：{res.status_code}")
            else:
                logger.debug("twitter 直连 测试")
                with Client() as client_test:
                    res = client_test.get("https://twitter.com/",headers=header)
                    if res.status_code == 200 or res.status_code == 302:
                        logger.debug(f"连通正常：{res.status_code}")
                    else:
                        logger.debug(f"连通异常：{res.status_code}")
        except Exception as e:
            logger.debug(f"连通测试异常：{e}")
                    
        try:
            logger.debug("获取推文测试")
            tweet_test = client.get_tweet(id=1665797367747026948,
                            media_fields="duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width,alt_text,variants".split(
                                ","),
                            expansions=[
                                'entities.mentions.username',
                                'attachments.media_keys',
                            ],
                    
                    tweet_fields=["possibly_sensitive"])
            if tweet_test.data:
                logger.debug("获取推文测试成功")
        except Exception as e:
            logger.debug(f"获取推文异常：{e}")
    
    @scheduler.scheduled_job("interval",minutes=3,id="twitter",misfire_grace_time=180)
    async def now_twitter():
        group_task_list = []
        group_list = json.loads(dirpath.read_text("utf8"))
        for group_num in group_list:
            if group_num and group_list[group_num]["status"] == "on":
                group_task_list.extend(
                    get_status("group",group_list, group_num, user_id, group_list[group_num][user_id][1])
                    for user_id in group_list[group_num]
                    if user_id != "status"
                )
        asyncio.gather(*group_task_list)
        
        pri_task_list = []
        pri_list = json.loads(pripath.read_text("utf8"))
        for qq_num in pri_list:
            if qq_num and pri_list[qq_num]["status"] == "on":
                pri_task_list.extend(
                    get_status("pri",pri_list, qq_num, user_id, pri_list[qq_num][user_id][1])
                    for user_id in pri_list[qq_num]
                    if user_id != "status"
                )
        asyncio.gather(*pri_task_list)

async def get_status(type_list: str,l_list: list, l_num: str, user_id: str,since_id: int):
    
    # 获取推文
    try:
        ne = client.get_users_tweets(
        id=user_id,
        max_results = 5,
        since_id = since_id
        )
        if ne.data:
            res = await get_tweet_for_id(ne.data[-1].id,l_list[l_num][user_id][2],l_list[l_num][user_id][0])
            
            bots = nonebot.get_adapter(Adapter).bots
            for bot in bots:
                try:
                    if type_list == "group":
                        await bots[bot].send_group_forward_msg(group_id=int(l_num), messages=res["task"])
                    else:
                        await bots[bot].send_private_forward_msg(user_id=int(l_num), messages=res["task"])
                except Exception:
                    pass
            l_list[l_num][str(user_id)][1] = ne.data[-1].id
            if type_list == "group":
                dirpath.write_text(json.dumps(l_list))
            else:
                pripath.write_text(json.dumps(l_list))
            # 清除垃圾
            await asyncio.sleep(80)
            for path in res["path"]:
                os.unlink(path) 
                os.unlink(path+".jpg")
    except Exception as e:
        pass
    
async def get_tweet_for_id(id: int,r18: bool,name: str):
    '''
    id: 推文id
    r18：是否发送r18
    name：推主name'''    
    tweet = client.get_tweet(id=id,
                            media_fields="duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width,alt_text,variants".split(
                                ","),
                            expansions=[
                                'entities.mentions.username',
                                'attachments.media_keys',
                            ],
                    tweet_fields=["possibly_sensitive"])
    if tweet.data.possibly_sensitive and not r18:
        logger.info(f"{name} 的推文 {str(id)} 为r18，根据配置跳过")
        raise ValueError("该条为r18，跳过")
    username = await get_user_name(name)
    tweet_json = tweet.includes
    task = []
    # 逐个判断是照片还是视频
    task_res = []
    task_res.append(MessageSegment.node_custom(
        user_id=2854196310,
        nickname=username,
        content=Message(tweet.data.text)
    ))
    if tweet_json:
        for tweet_single in tweet_json['media']:
            # 图片
            if tweet_single['type'] == "photo":
                task.append(get_pic(tweet_single.url))
            # 视频
            elif tweet_single['type'] == "video":
                task.append(get_video(tweet_single['variants'][0]['url']))
    try:
        path_res = await asyncio.gather(*task)
    except Exception as e:
        logger.debug(f"下载媒体出现异常：{e}")
        path_res = []
    task_res += [msg_type(2854196310, path,name=name) for path in path_res]
    return {"task":task_res,"path":path_res}
        
        
def msg_type(user_id:int, task: str,name: str):
    
    if task.endswith("jpg") or task.endswith("png"):
        return MessageSegment.node_custom(user_id=user_id, nickname=name,
                                   content=Message(MessageSegment.image(f"file://{task}")))
    elif task.endswith("mp4"):
        return MessageSegment.node_custom(user_id=user_id, nickname=name,
                                          content=Message(MessageSegment.video(f"file:///{task}")))        
        
async def get_pic(url: str) -> str:
    path = Path() / "data" / "twitter" / "cache" /  f"{str(random.randint(1, 1000))}.jpg"
    path = f"{os.getcwd()}/{str(path)}"
    if config_dev.twitter_proxy:
        async with AsyncClient(proxies=f"http://{config_dev.twitter_proxy}") as client:
            res = await client.get(url)
            if res.status_code != 200:
                raise ValueError("图片下载失败")
            with open(path,'wb') as file:
                file.write(res.read())
    else:
        async with AsyncClient() as client:
            res = await client.get(url)
            if res.status_code != 200:
                raise ValueError("图片下载失败")
            with open(path,'wb') as file:
                file.write(res.read())
            
    return path

async def get_video(url: str) -> str:
    path = Path() / "data" / "twitter" / "cache" /  f"{str(random.randint(1, 1000))}.mp4"
    path = f"{os.getcwd()}/{str(path)}"
    if config_dev.twitter_proxy:
        async with AsyncClient(proxies=f"http://{config_dev.twitter_proxy}") as client:
            async with client.stream('GET',url,headers=header) as res:
                if res.status_code != 200:
                    raise ValueError("视频下载失败")
                with open(path,'wb') as file:
                    async for chunk in res.aiter_bytes():
                        file.write(chunk)
    else:
        async with AsyncClient() as client:
            async with client.stream('GET',url,headers=header) as res:
                if res.status_code != 200:
                    raise ValueError("视频下载失败")
                with open(path,'wb') as file:
                    async for chunk in res.aiter_bytes():
                        file.write(chunk)
    return path
        
async def get_id(name: str) -> str:
    '''return user_id from name'''
    try:
        return str(client.get_user(username=name).data.id)
    except Exception as e:
        return "未找到"    
    
async def get_user_name(name) -> str:
    '''return user_name from name'''
    try:
        return client.get_user(username=name).data.name
    except Exception as e:
        return "未找到name" 
    
save = on_command("关注推主",block=True,priority=config_dev.command_priority)
@save.handle()
async def save_handle(bot:Bot,event: MessageEvent,matcher: Matcher,arg: Message = CommandArg()):
    data = []
    if " " in arg.extract_plain_text():
        data = arg.extract_plain_text().split(" ")
    else:
        data.append(arg.extract_plain_text())
    user_id = await get_id(data[0])
    
    if user_id == "未找到":
        await matcher.finish(f"未找到 {arg}")
        
    res = client.get_users_tweets(
        id=user_id,
        max_results = 5
    )
    since_id = res.data[0].id if res.data else 0
    
    if isinstance(event,GroupMessageEvent):
        group_list = json.loads(dirpath.read_text("utf8"))
        if str(event.group_id) not in group_list:
            group_list[str(event.group_id)] = {"status":"on"}
        if len(data) > 1:
            group_list[str(event.group_id)][user_id] = [data[0],since_id,True]
        else:
            group_list[str(event.group_id)][user_id] = [data[0],since_id,False]
        dirpath.write_text(json.dumps(group_list))
    else:
        pri_list = json.loads(pripath.read_text("utf8"))
        if str(event.user_id) not in pri_list:
            pri_list[str(event.user_id)] = {"status":"on"}
        pri_list[str(event.user_id)][user_id] = [data[0],since_id,True]
        pripath.write_text(json.dumps(pri_list))
    username = await get_user_name(data[0])
    await matcher.finish(f"id:{data[0]}\nname:{username}\n订阅成功")
        

delete = on_command("取关推主",block=True,priority=config_dev.command_priority)
@delete.handle()
async def delete_handle(bot:Bot,event: MessageEvent,matcher: Matcher,arg: Message = CommandArg()):
    user_id = await get_id(arg.extract_plain_text())
    if user_id == "未找到":
        await matcher.finish(f"未找到 {arg}")

    if isinstance(event,GroupMessageEvent):
        group_list = json.loads(dirpath.read_text("utf8"))
        if str(event.group_id) not in group_list:
            group_list[str(event.group_id)] = {"status":"on"}

        try:
            if arg.extract_plain_text() == group_list[str(event.group_id)][user_id][0]:
                group_list[str(event.group_id)].pop(user_id) 
            else:
                raise ValueError("尚未关注 {arg.extract_plain_text()}")
        except Exception as e:
            await matcher.finish(f"{e}")
        dirpath.write_text(json.dumps(group_list))
    else:
        pri_list = json.loads(pripath.read_text("utf8"))
        if str(event.user_id) not in pri_list:
            pri_list[str(event.user_id)] = {"status":"on"}

        try:
            if arg.extract_plain_text() == pri_list[str(event.user_id)][user_id][0]:
                pri_list[str(event.user_id)].pop(user_id) 
            else:
                raise ValueError("尚未关注 {arg.extract_plain_text()}")
        except Exception as e:
            await matcher.finish(f"{e}")
        pripath.write_text(json.dumps(pri_list))

    await matcher.finish(f"取关 {arg.extract_plain_text()} 成功")
    
follow_list = on_command("推主列表",block=True,priority=config_dev.command_priority)
@follow_list.handle()
async def follow_list_handle(bot:Bot,event: MessageEvent,matcher: Matcher):
    if isinstance(event,GroupMessageEvent):
        data = json.loads(dirpath.read_text("utf8"))[str(event.group_id)]
    else:
        data = json.loads(pripath.read_text("utf8"))[str(event.user_id)]
    del data["status"]
    name_list = [data[x][0] for x in data]
    username_list = []
    for x in name_list:
        username_list.append(await get_user_name(x))
    
    res = [
        MessageSegment.node_custom(
            user_id=2854196310, nickname=username, content=Message(name)
        )
        for name,username in zip(name_list,username_list)
    ]
    bots = nonebot.get_adapter(Adapter).bots
    for bot in bots:
        with contextlib.suppress(Exception):
            if event.message_type == "group":
                await bots[bot].send_group_forward_msg(group_id=int(event.group_id), messages=res)
            else:
                await bots[bot].send_private_forward_msg(user_id=int(event.user_id), messages=res)
    await matcher.finish()


async def is_rule(event:MessageEvent) -> bool:
    if isinstance(event,GroupMessageEvent):
        if event.sender.role in ["owner","admin"]:
            return True
        return False
    else:
        return True
    
twitter_status = on_command("推特推送",block=True,rule=is_rule,priority=config_dev.command_priority)
@twitter_status.handle()
async def twitter_status_handle(bot:Bot,event: MessageEvent,matcher: Matcher,arg: Message = CommandArg()):
    if isinstance(event,GroupMessageEvent):
        group_list = json.loads(dirpath.read_text("utf8"))
        if str(event.group_id) not in group_list:
            group_list[str(event.group_id)] = {"status":"on"}
        if arg.extract_plain_text() == "开启":
            group_list[str(event.group_id)]["status"] = "on"
            dirpath.write_text(json.dumps(group_list))
            await matcher.finish("推送已开启")
        elif arg.extract_plain_text() == "关闭":
            group_list[str(event.group_id)]["status"] = "off"
            dirpath.write_text(json.dumps(group_list))
            await matcher.finish("推送已关闭")
    else:
        pri_list = json.loads(pripath.read_text("utf8"))
        if str(event.user_id) not in pri_list:
            pri_list[str(event.user_id)] = {"status":"on"}
        if arg.extract_plain_text() == "开启":
            pri_list[str(event.user_id)]["status"] = "on"
            pripath.write_text(json.dumps(pri_list))
            await matcher.finish("推送已开启")
        elif arg.extract_plain_text() == "关闭":
            pri_list[str(event.user_id)]["status"] = "off"
            pripath.write_text(json.dumps(pri_list))
            await matcher.finish("推送已关闭")
