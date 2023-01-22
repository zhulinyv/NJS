from nonebot import on_command
import nonebot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from bs4 import BeautifulSoup
from httpx import AsyncClient
import re
import random
import asyncio

# 一次性最多返回多少条结果, 可在env设置
try:
    max_num = nonebot.get_driver().config.magnet_max_num
except:
    max_num = 3

# cookie & user-agent
try:
    cookie = nonebot.get_driver().config.clm_cookie
    useragent = nonebot.get_driver().config.clm_useragent
except:
    # 这是我自己刚刚获取的cookie和useragent捏
    cookie = "challenge=8b11e0a1c25a29ca8cd6b530e64c5294; ex=1; _ga=GA1.1.1219749203.1655966067; _ga_W7KV15XZN0=GS1.1.1655966067.1.1.1655966427.0"
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44"



# 我也不知道有没有必要加这一行, 我看着从env闯进来的cookie这个数据类型好像不太对劲
# cookie = cookie

# 访问头
headers = {
    "cookie":cookie,
    "user-agent":useragent,
}

# 网站主页
magnet_url = "https://clm9.me"


# 声明一个响应器, 优先级10, 向下阻断
bt = on_command("磁力搜索",aliases={'bt'}, priority=10, block=True)

@bt.handle()
async def _(msg: Message = CommandArg()):
    # 纯文本提取
    keyword = msg.extract_plain_text()
    if keyword == "":
        await bt.finish("虚空搜索?")
    search_url = f"https://clm9.me/search?word={keyword}"
    try:
        # 尝试获取消息
        message = await get_magnet(search_url)
    except:
        # 获取失败的时候返回错误信息
        await bt.finish("搜索失败, 可能网络出现问题, 或者env配置的cookie过期了, 也可能是代码有bug(不可能, 绝对不可能)")
    # 如果搜索到了结果, 则尝试发送, 有些账号好像文本太长cqhttp会显示风控
    if message:
        try:
            await bt.send(message)
        except:
            await bt.finish("消息被风控了, message发送失败")
    else:
        await bt.finish("没有找到结果捏, 或者env配置的cookie过期了")
        


# 获取磁力链接和一堆东西
async def get_magnet(url):
    async with AsyncClient() as client:
        # 发送请求
        res = await client.get(url=url, headers=headers, timeout=30)
        res=res.text
        soup = BeautifulSoup(res, "lxml")
        item_lst = soup.find_all("a", {"class": "SearchListTitle_result_title"})
        async with AsyncClient() as client2:
            tasks = []
            # 获取每一个url, 异步访问
            for item in item_lst:
                url = magnet_url + item.get("href")
                tasks.append(get_info(url,client2))
            data = await asyncio.gather(*tasks)
    # num是每次发送的条数        
    num = max_num
    # 防止数组越界
    if len(data) < max_num:
        num = len(data)
    # 随机选择一些条目 
    message_list = random.sample(data, num)
    message = ""
    # message拼接
    for msg in message_list:
        message = message + msg + "\n"
    # 在控制台输出一下
    print(message)
    return message


async def get_info(url,client):
    res = await client.get(url=url, headers=headers, timeout=30)
    res=res.text
    soup = BeautifulSoup(res, "lxml")
    Information_l_content = soup.find_all("div", {"class": "Information_l_content"})
    # 这个是磁力链接
    magnet = Information_l_content[0].find("a").get("href")
    #  这个是文件大小
    size = list(Information_l_content[1])[4]
    size = re.sub(u"\\<.*?\\>", "", str(size)) 
    # 访问File_list_info, 目的是为了获取文件名
    name = soup.find_all('div',{'class':'File_list_info'})
    name = list(name[0])[0]
    message = f"文件名: {name} \n大小: {size}\n链接: {magnet}\n"
    return message
