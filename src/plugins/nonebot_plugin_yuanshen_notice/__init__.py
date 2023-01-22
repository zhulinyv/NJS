from nonebot import on_regex, on_keyword
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message
import requests
import json

"""
本插件功能为返回原神官网前20条公告
提供用户公告链接，方便查看
本插件调用api为萌新源api(https://api.juncikeji.xyz/)
命令：
  - 原神公告 返回20条最新公告标题
  - #原神公告+序号 返回公告背景以及公告链接
writen by 萌新源 at 2023/1/12
"""

ysgg = on_regex(pattern=r'^原神公告$')
ggset = on_keyword({'查看公告'})


@ysgg.handle()
async def yy(bot: Bot, event: GroupMessageEvent, state: T_State):
    """本函数用作返回前20条公告，并且发送给用户"""
    url = "https://api.juncikeji.xyz/api/yuanshen.php"  # 定义接口链接
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.59"
    }
    resp = requests.get(url=url, headers=header, timeout=10)  # 返回数据
    data_d = json.loads(resp.text)  # 转换字典
    str = '——📢—原神公告—📢——\n'  # 定义字符串，用于后续储存公告标题
    for i in range(0, 20):
        str += f"{i}:{data_d[i]['title']}\n"

    str += '———————————\n请发送 "查看公告+公告序号" 查看详情'
    await ysgg.send(Message(str))


@ggset.handle()
async def cc(bot: Bot, event: GroupMessageEvent, state: T_State):
    """本函数用作发送详情公告"""
    url = "https://api.juncikeji.xyz/api/yuanshen.php"  # 定义接口链接
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.59"
    }
    resp = requests.get(url=url, headers=header, timeout=10)  # 返回数据
    data_d = json.loads(resp.text)  # 转换字典
    ans = str(event.get_message()).strip()
    ans = ans.strip('查看公告')  # 获取公告序号
    try:
        ans = int(ans)
        try:
            img = data_d[ans]['img'] #背景图片链接
            url = data_d[ans]['url'] #公告链接
            msg = f"[CQ:image,file={img}]\n公告链接：{url}"
            await ggset.send(Message(msg))
        except IndexError:
            await ggset.send(Message('请确保输入的序号在有效范围内！'))
    except ValueError:
        await ggset.send(Message('请确保输入的序号为数字！'))
