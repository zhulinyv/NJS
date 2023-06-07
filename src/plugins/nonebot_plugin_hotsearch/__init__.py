import json, re, httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GROUP,
    GroupMessageEvent
)
from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='热搜查询',
    description='获取各个网站的热搜排行',
    usage='可选命令：\n'
          '/微博热搜  /百度热搜\n'
          '/知乎热搜  /贴吧热搜 /b站热搜'
)


def render_forward_msg(msg_list: list, uid: str, name='小白猫~'):
	forward_msg = []
	for msg in msg_list:
		forward_msg.append({
			"type": "node",
			"data": {
				"name": str(name),
				"uin": str(uid),
				"content": msg
			}
		})
	return forward_msg

# 热搜条数dn
cnt = 10

# 触发器
weibo_hotsearch = on_command("微博热搜", permission=GROUP, priority=5, block=True)
baidu_hotsearch = on_command("百度热搜", permission=GROUP, priority=5, block=True)
zhihu_hotsearch = on_command("知乎热搜", permission=GROUP, priority=5, block=True)
tieba_hotsearch = on_command("贴吧热搜", permission=GROUP, priority=5, block=True)
bzhan_hotsearch = on_command("b站热搜", aliases={"B站热搜"}, permission=GROUP, priority=5, block=True)


# 微博热搜
@weibo_hotsearch.handle()
async def weiboresou(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    bot_id = bot.self_id
    await bot.send(event=event, message='获取中……')
    url = 'https://weibo.com/ajax/side/hotSearch'
    srcurl = "https://s.weibo.com/weibo?q="
    res = httpx.get(url)
    r = res.json()["data"]["realtime"][:cnt]
    msg_list = ['微博热搜榜']
    for i,obj in enumerate(r):
        code = str(obj["word"].encode('utf-8'))[2:-1]
        code = code.replace('\\x','%')
        url = srcurl+code
        result = '%d、%s\nhot:%d\n链接:%s'%(i+1,obj["word"],obj["num"],url)
        msg_list.append(result)
    forward_msg = render_forward_msg(msg_list, bot_id)
    try:
        await bot.send_group_forward_msg(group_id=group_id, messages=forward_msg)
    except:
        await bot.send(event=event, message='合并消息获取失败，稍后重新试试吧~')


# 百度热搜
@baidu_hotsearch.handle()
async def baiduresou(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    bot_id = bot.self_id
    await bot.send(event=event, message='获取中……')
    url='https://top.baidu.com/board?tab=realtime'
    res=httpx.get(url)
    r=res.text
    data = re.search('(<!--s-data:)({.+})(-->)', r)
    r=json.loads(data.groups()[1])["data"]["cards"][0]["content"][:cnt]
    msg_list = ['百度热搜榜']
    for i,obj in enumerate(r):
        result = '%d、%s\nhot:%s\n链接:%s'%(i+1,obj["desc"],obj["hotScore"],obj["appUrl"])
        msg_list.append(result)
    forward_msg = render_forward_msg(msg_list, bot_id)
    try:
        await bot.send_group_forward_msg(group_id=group_id, messages=forward_msg)
    except:
        await bot.send(event=event, message='合并消息获取失败，稍后重新试试吧~')

# 知乎热搜
@zhihu_hotsearch.handle()
async def zhihuresou(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    bot_id = bot.self_id
    await bot.send(event=event, message='获取中……')
    url='https://www.zhihu.com/billboard'
    res=httpx.get(url)
    r=res.text
    data = re.search('("hotList":\\[{)(.+?)(}\\])', r)
    data=data.groups()[1]
    msg_list=["知乎热搜榜"]
    for i,obj in enumerate(data.split('},{')[:cnt]):
        dic=json.loads("{"+obj+"}")["target"]
        result = '%d、%s\nhot:%s\n链接:%s'%(i+1,dic["titleArea"]["text"],dic["metricsArea"]["text"],dic["link"]["url"])
        msg_list.append(result)
    forward_msg = render_forward_msg(msg_list, bot_id)
    try:
        await bot.send_group_forward_msg(group_id=group_id, messages=forward_msg)
    except:
        await bot.send(event=event, message='合并消息获取失败，稍后重新试试吧~')


# 贴吧热搜
@tieba_hotsearch.handle()
async def tiebaresou(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    bot_id = bot.self_id
    await bot.send(event=event, message='获取中……')
    url='https://tieba.baidu.com/hottopic/browse/topicList'
    res=httpx.get(url)
    r=res.json()["data"]["bang_topic"]["topic_list"][:cnt]
    msg_list = ['贴吧热议榜']
    for i,obj in enumerate(r):
        result = '%d、%s\nhot:%d\n链接:%s'%(i+1,obj["topic_name"],obj["discuss_num"],obj["topic_url"])
        msg_list.append(result)
    forward_msg = render_forward_msg(msg_list, bot_id)
    try:
        await bot.send_group_forward_msg(group_id=group_id, messages=forward_msg)
    except:
        await bot.send(event=event, message='合并消息获取失败，稍后重新试试吧~')


# b站热搜
@bzhan_hotsearch.handle()
async def bzhanresou(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    bot_id = bot.self_id
    await bot.send(event=event, message='获取中……')
    url='https://app.bilibili.com/x/v2/search/trending/ranking'
    try:
        async with httpx.AsyncClient() as r:
            r: httpx.AsyncClient
            res = await r.get(
                "https://app.bilibili.com/x/v2/search/trending/ranking"
            )
            msg_list = ['b站热搜']
            rs = res.json()["data"]["list"][:cnt]
            for i,obj in enumerate(rs):
                code = str(obj['show_name'].encode('utf-8'))[2:-1]
                code = code.replace('\\x','%')
                result = '%d、%s'%(i+1, obj['show_name'])
                msg_list.append(result)
            forward_msg = render_forward_msg(msg_list, bot_id)
            try:
                await bot.send_group_forward_msg(group_id=group_id, messages=forward_msg)
            except:
                await bot.send(event=event, message='合并消息获取失败，稍后重新试试吧~')
    except Exception as e:
        await bot.send(f"获取B站热搜失败，error:{e}")


