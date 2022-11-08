import asyncio
from nonebot.exception import IgnoredException
from nonebot.plugin.on import on_keyword, on_message, on_notice, on_command
from nonebot.rule import to_me
from nonebot.message import event_preprocessor
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    Event,
    NotifyEvent,
    MessageEvent,
    PokeNotifyEvent,
    MessageSegment
)
from .utils import *
from loguru import logger

cdTime = 21600   # 这个是有人骂bot的时候ban的CD, 单位秒,可以自己改

# 响应器1, 有人骂了我家bot就不理他六小时, superuser除外(信息存在bot目录"data/sb_CDusercd.json"里面,可以删掉他提前解除)
# 判断方法:艾特了bot句子中包含以下关键词就触发, 可能会误触? 不管了, 响应器优先级1
attack = on_keyword(["傻逼", "sb", "SB", "你妈", "nm", "色批", "泥马", "病", "尼玛", "傻鸟", "傻狗", "狗", "儿子", "爹", "爸爸", "猪", "沙雕", "卧槽", "妈的", "傻卵", "二逼", "二臂", "爷爷", "有病", "MD", "宕机", ], rule=to_me(), block=True, priority=1)
# 响应器2, 优先级99,条件:艾特bot就触发
ai = on_message(rule=to_me(), priority=99)
# 响应器3, 用来移除bot不理人的操作, 传入的参数是QQ号
remove_CD = on_command("remove_sb", permission=SUPERUSER, block=True)

@attack.handle()
async def handle_receive(event: MessageEvent):
    img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "1.jpg"
    qid = event.get_user_id()
    data = read_json()
    mid = event.message_id
    # 写入json,记录时间和id
    write_json(qid, event.time, mid, data)
    await attack.send(message=f"{random.choice(attack_sendmessage)}"+MessageSegment.image(img), at_sender=True)
# 提前处理消息,用于阻断

@event_preprocessor
async def event_preblock_sb(event: Event, bot: Bot):
    # 当event类型为MessageEvent(消息事件)或NotifyEvent(提醒事件)
    if isinstance(event,MessageEvent) or isinstance(event,NotifyEvent):
        # 如果不是超级用户, 执行以下操作
        if not event.get_user_id() in bot.config.superusers:
            qid = event.get_user_id()
            data = read_json()
            try:
                cd = event.time - data[qid][0]
            except Exception:
                cd = cdTime + 1
            if cd > cdTime:
                return
            blockreason = "这货骂了我家bot"
            if blockreason:
                logger.info(f'当前事件已阻断，原因：{blockreason}')
                raise IgnoredException(blockreason)
    # 其它事件就不参与处理
    else:
        pass


# 这个值为False时, 使用的是小爱同学, True时使用的是青云客api
api_flag = True
# 优先级1, 向下阻断, 需要艾特bot, 智能回复api切换指令, 目前有俩api, 分别是qinyunke_api和小爱同学, 默认qinyun
api_switch = on_command("智障回复api切换", aliases={"ai切换", "api_switch","智能回复api切换"}, permission=SUPERUSER, rule=to_me(), block=True)
# 优先级99, 条件: 艾特bot就触发
ai = on_message(rule=to_me(), priority=99, block=False)
# 优先级1, 不会向下阻断, 条件: 戳一戳bot触发
poke_ = on_notice(rule=to_me(), block=False)


@api_switch.handle()
async def _():
    global api_flag
    api_flag = not api_flag
    await api_switch.send(message=f"切换成功, 当前智能回复api为{'青云客' if api_flag else '小爱同学'}")


@ai.handle()
async def _(event: MessageEvent):
    # 获取消息文本
    msg = str(event.get_message())
    # 去掉带中括号的内容(去除cq码)
    msg = re.sub(r"\[.*?\]", "", msg)
    # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
    if (not msg) or msg.isspace() or msg in [
        "你好啊",
        "你好",
        "在吗",
        "在不在",
        "您好",
        "您好啊",
        "你好",
        "在",
    ]:
        await ai.finish(Message(random.choice(hello__reply)))
    # 获取用户nickname
    if isinstance(event, GroupMessageEvent):
        nickname = event.sender.card or event.sender.nickname
    else:
        nickname = event.sender.nickname
    # 从字典里获取结果
    result = await get_chat_result(msg,  nickname)
    # 如果词库没有结果，则调用api获取智能回复
    if result == None:
        if api_flag:
            qinyun_url = f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}"
            message = await qinyun_reply(qinyun_url)
            logger.info("来自青云客的智能回复: " + message)
        else:
            xiaoai_url = f"https://jintia.jintias.cn/api/xatx.php?msg={msg}"
            message = await xiaoice_reply(xiaoai_url)
            logger.info("来自小爱同学的智能回复: " + message)
        await ai.finish(message=message)
    await ai.finish(Message(result))


@poke_.handle()
async def _poke_event(bot: Bot,event: PokeNotifyEvent)-> bool:
    if event.is_tome:
        if random.random() < 0.2:
            # pic = await get_setu()
            # message="别戳了别戳了,这张setu给你了,让我安静一会儿,30秒后我要撤回\n"+Message(pic[1])+Message(pic[0])
            message="别戳了别戳了,这张图给你了,让我安静一会儿,30秒后我要撤回\n" + MessageSegment.image(file='https://iw233.cn/api.php?sort=iw233')
            setu_msg_id = await poke_.send(message)
            setu_msg_id = setu_msg_id['message_id']
            await asyncio.sleep(30)
            await bot.delete_msg(message_id=setu_msg_id)
            return
            # 50%概率回复莲宝的藏话
        elif random.random() < 0.5:
            # 发送语音需要配置ffmpeg, 这里try一下, 不行就随机回复poke__reply的内容
            try:
                await poke_.send(MessageSegment.record(Path(aac_file_path)/random.choice(aac_file_list)))
            except:
                await poke_.send(message=f"{random.choice(poke__reply)}")
#               await poke_.send(message=f"{random.choice(poke__reply)}")
        else:
            await poke_.send(message=f"{random.choice(poke__reply)}")


'''@poke_.handle()
async def _poke_event(bot: Bot,event: PokeNotifyEvent)-> bool:
    with open('./data/sb_CDusercd.json','r',encoding='utf8')as fp:
        json_data = json.load(fp)
    qid = str(event.get_user_id())
    if qid in json_data:
        return
    else:
        if event.is_tome:
            if random.random() < 0.2:
                # pic = await get_setu()
                # message="别戳了别戳了,这张setu给你了,让我安静一会儿,30秒后我要撤回\n"+Message(pic[1])+Message(pic[0])
                message="别戳了别戳了,这张图给你了,让我安静一会儿,30秒后我要撤回\n" + MessageSegment.image(file='https://dev.iw233.cn/api.php?sort=random')
                setu_msg_id = await poke_.send(message)
                setu_msg_id = setu_msg_id['message_id']
                await asyncio.sleep(30)
                await bot.delete_msg(message_id=setu_msg_id)
                return
                # 50%概率回复莲宝的藏话
            elif random.random() < 0.5:
                # 发送语音需要配置ffmpeg, 这里try一下, 不行就随机回复poke__reply的内容
                try:
                    await poke_.send(MessageSegment.record(Path(aac_file_path)/random.choice(aac_file_list)))
                except:
                    await poke_.send(message=f"{random.choice(poke__reply)}")
#               await poke_.send(message=f"{random.choice(poke__reply)}")
            else:
                await poke_.send(message=f"{random.choice(poke__reply)}")'''

'''
# 获取涩图(P站)
async def get_setu() -> list:
    async with AsyncClient() as client:
        req_url = "https://api.lolicon.app/setu/v2"
        params = {
            "r18": 0,
            "size": "regular",
            "proxy": "i.pixiv.re",
        }
        res = await client.get(req_url, params=params, timeout=120)
        logger.info(res.json())
        setu_title = res.json()["data"][0]["title"]
        setu_url = res.json()["data"][0]["urls"]["regular"]
        content = await down_pic(setu_url)
        setu_pid = res.json()["data"][0]["pid"]
        setu_author = res.json()["data"][0]["author"]
        base64 = convert_b64(content)
        if type(base64) == str:
            pic = "[CQ:image,file=base64://" + base64 + "]"
            data = (
                "标题:"
                + setu_title
                + "\npid:"
                + str(setu_pid)
                + "\n画师:"
                + setu_author
            )
        return [pic, data, setu_url]

async def down_pic(url):
    async with AsyncClient() as client:
        headers = {
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        }
        re = await client.get(url=url, headers=headers, timeout=120)
        if re.status_code == 200:
            logger.success("成功获取图片")
            return re.content
        else:
            logger.error(f"获取图片失败: {re.status_code}")
            return re.status_code

def convert_b64(content) -> str:
    ba = str(base64.b64encode(content))
    pic = findall(r"\'([^\"]*)\'", ba)[0].replace("'", "")
    return pic
'''

@remove_CD.handle()
async def _(msg: Message = CommandArg()):
    # 获取消息文本
    qid = msg.extract_plain_text()
    boolean = False
    # 我他妈也想直接try一下完事, 不知道为什么那样的话try和except全执行了, 焯
    try:
        remove_json(qid)
        boolean = True
    except:
        pass
    if boolean:
        await remove_CD.finish(f"ID:{qid}CD已清除, 下次别骂{NICKNAME}了")
    else:
        await remove_CD.finish(f"{NICKNAME}记忆里没有这号人欸")
