from nonebot import on_command
from nonebot.log import logger
from nonebot.params import CommandArg, ArgPlainText
from .config_covid_19 import group_covid, group_image_covid, colour, size
from PIL import Image, ImageFont, ImageDraw
import  datetime, random, httpx, os, aiofiles
from nonebot.adapters.onebot.v11 import GroupMessageEvent,MessageSegment,Message

searchcovid = on_command('查询疫情', priority=30)
covid_news = on_command('疫情资讯', priority=30)
covid_19_mulu = on_command("疫情菜单", priority=30)
ranking_list_jwsr = on_command("境外输入排行榜", priority=30)
details_covid = on_command("疫情现状", priority=30)
cha_covid = on_command("查风险", priority=30)

async def max(p):
    a = []
    for i in range(len(p)):
        a.append(len(p[i]))
    a.sort()
    b = int(len(a) - 1)
    return a[b]

async def CreateImg(text, colour, size):
    text = str(text) + str("\n\n——————Created By Bingyue——————").replace('\n', "\n")
    liens = text.split('\n')
    im = Image.new("RGB", ((size * await max(liens)), len(liens) * (size + 3)), (255, 255, 255))
    fontPath = os.path.join(os.path.dirname(__file__), "123.ttf")
    font = ImageFont.truetype(fontPath, int(size))
    ImageDraw.Draw(im).text((0, 0), text, font=font, fill=colour)
    image_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if os.path.exists("covid_by_19") == False:
        os.mkdir("covid_by_19")
        im.save('./covid_by_19/' + str(image_time) + '.png')
        return str(image_time)
    else:
        im.save("./covid_by_19/" + str(image_time) + ".png")
        return str(image_time)

@covid_19_mulu.handle()
async def _(event: GroupMessageEvent):
    if int(event.group_id) in group_covid:
        l = f"——————疫情小助手——————\n/查询疫情[地区]\n/疫情资讯\n/境外输入排行榜\n/疫情现状\n/查风险[地区] 如 /查风险广东省,广州市,全部\n/covid_19开启\n/covid_19关闭\n/疫情文转图开\n/疫情文转图关\n【{await covid_txt()}】"
        if int(event.group_id) in group_image_covid:
            b = await CreateImg(text=l, colour=colour, size=size)
            a = os.path.join('./', os.getcwd(), 'covid_by_19', b + ".png")
            await covid_19_mulu.finish(MessageSegment.image(file=str("file:///") + a))
        else:
            await covid_19_mulu.finish(l)

@cha_covid.handle()
async def cha(event: GroupMessageEvent, foo: Message = CommandArg()):
    if int(event.group_id) in group_covid:
        try:
            a = str(foo).split(",")
            b = await httpx.AsyncClient().get(
                f"https://interface.sina.cn/news/ncp/data.d.json?mod=risk_level&areaname={a[0]}|{a[1]}|%E5%85%A8%E9%83%A8",
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"})
            b = b.json()
            c = [f"————{a[0]}{a[1]}的风险地区————\n"]
            if b["data"]["middleNum"] != 0:
                for i in range(len(b["data"]["middle"])):
                    c.append(str("🍁") + str(i + 1) + str(
                        f',地址:{b["data"]["middle"][i]["area_name"]},具体位置:{b["data"]["middle"][i]["communitys"]}') + "\n")

            if b["data"]["highNum"] != 0:
                c.append("\n以下是高风险地区\n")
                for i in range(len(b["data"]["high"])):
                    c.append(str("🍁") + str(i + 1) + str(
                        f',地址:{b["data"]["high"][i]["area_name"]},具体位置:{b["data"]["high"][i]["communitys"]}') + "\n")
        except(httpx.ConnectError, httpx.NetworkError, httpx.ConnectTimeout):
            logger.error("covid_19:网络错误")
            await cha_covid.finish()
        except(IndexError):
            logger.error("covid_19:查询格式错误")
            await cha_covid.finish("查询失败，命令格式错误\n示例:/查风险广东省,广州市")
        except(KeyError):
            d = f"————{a[0]}{a[1]}的风险地区————\n🍁该地区低风险（也有可能是查询错误）"
            logger.success(f"covid_19:获取{a[0]}{a[1]}地区成功")
            if int(event.group_id) in group_image_covid:
                b = await CreateImg(text=d, colour=colour, size=size)
                a = os.path.join('./', os.getcwd(), 'covid_by_19', b + ".png")
                await cha_covid.finish(MessageSegment.image(file=str("file:///") + a))
            else:
                await cha_covid.finish(d)
        else:
            logger.success(f"covid_19:获取{a[0]}{a[1]}地区成功")
            if int(event.group_id) in group_image_covid:
                await cha_covid.finish(await json_lshi(c))
            else:
                await cha_covid.finish(c)

async def json_lshi(c):
    for i in c:
        with open("./covid_by_19/3.txt", "a", encoding="utf_8") as f:
            f.write(i)
            f.close()

    with open("./covid_by_19/3.txt", "r", encoding="utf_8") as g:
        l = g.read()
        b = await CreateImg(text=l, colour=colour, size=size)
        a = os.path.join('./', os.getcwd(), 'covid_by_19', b + ".png")
        g.close()
        os.remove("./covid_by_19/3.txt")
        return MessageSegment.image(file=str("file:///") + a)

@details_covid.handle()
async def details(event: GroupMessageEvent):
    if int(event.group_id) in group_covid:
        try:
            a = await httpx.AsyncClient().get(url="https://interface.sina.cn/news/wap/fymap2020_data.d.json", headers={
                "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"})
            a = a.json()
            gntotal = a["data"]["gntotal"]
            deathtotal = a["data"]["deathtotal"]
            jwsrNum = a["data"]["jwsrNum"]
            econNum = a["data"]["econNum"]
            time_covid = a["data"]["mtime"]
            curetotal = a["data"]["curetotal"]
        except(httpx.ConnectError, httpx.HTTPError, httpx.NetworkError):
            logger.error("covid_19:网络请求错误")
            await details_covid.finish()
        except(KeyError):
            logger.error("covid_19:获取数据错误 请检查json")
            await details_covid.finish()
        else:
            logger.success("covid_19:获取疫情详情成功")
            if int(event.group_id) in group_image_covid:
                l = f"——本国疫情详情——\n🍁时间:{time_covid}\n🍁累计确诊:{gntotal}\n🍁累计死亡:{deathtotal}\n🍁境外输入:{jwsrNum}\n🍁现存确诊:{econNum}\n🍁治愈累计:{curetotal}\n【{await covid_txt()}】"
                b = await CreateImg(text=l, colour=colour, size=size)
                a = os.path.join('./', os.getcwd(), 'covid_by_19', b + ".png")
                await details_covid.finish(MessageSegment.image(file=str("file:///") + a))
            else:
                await details_covid.finish(
                    f"——本国疫情详情——\n🍁时间:{time_covid}\n🍁累计确诊:{gntotal}\n🍁累计死亡:{deathtotal}\n🍁境外输入:{jwsrNum}\n🍁现存确诊:{econNum}\n🍁治愈累计:{curetotal}\n【{await covid_txt()}】")

async def covid_txt():
    try:
        async with  aiofiles.open(str(os.path.dirname(__file__)) + '/covid_19.txt', 'r', encoding='utf-8') as f:
            o = await f.readlines()
            p = random.randint(0, len(o))
    except (FileNotFoundError):
        pass
    else:
        return o[p].strip("\n")

@ranking_list_jwsr.handle()
async def phb(event: GroupMessageEvent):
    if int(event.group_id) in group_covid:
        try:
            a = await httpx.AsyncClient().get(url="https://interface.sina.cn/news/wap/fymap2020_data.d.json", headers={
                "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"})
            b = a.json()
            c = ["—境外输入排行榜—"]
            for i in range(len(b["data"]["jwsrTop"])):
                c.append("\n" + str(f"🍁{i + 1}") + str(b["data"]["jwsrTop"][i]["name"]) + str("  ") + str(
                    "输入人数:" + b["data"]['jwsrTop'][i]["jwsrNum"]))

            c.append(f"\n【{await covid_txt()}】")
        except(httpx.ConnectError, httpx.HTTPError, httpx.NetworkError):
            logger.error("covid_19:网络错误")
            await ranking_list_jwsr.finish()
        except(KeyError):
            logger.error("covid_19:数据解析失败")
            await ranking_list_jwsr.finish()
        else:
            logger.success("covid_19:获取排行榜成功")
            if int(event.group_id) in group_image_covid:
                await ranking_list_jwsr.finish(await json_lshi(c=c))
            else:
                await ranking_list_jwsr.finish(c)

@searchcovid.handle()
async def searchcovid_handle(event: GroupMessageEvent, foo: Message = CommandArg()):
    if int(event.group_id) in group_covid:
        if int(event.group_id) in group_image_covid:
            b = await CreateImg(text=await httpx_covid_city(msg=foo), colour=colour, size=size)
            a = os.path.join('./', os.getcwd(), 'covid_by_19', b + ".png")
            await searchcovid.finish(MessageSegment.image(file=str("file:///") + a))
        else:
            await searchcovid.finish(await httpx_covid_city(msg=foo))

@covid_news.handle()
async def chachacha(event: GroupMessageEvent):
    if int(event.group_id) in group_covid:
        if int(event.group_id) not in group_image_covid:
            await covid_news.send(await httpx_covid_news(msg=None))
        else:
            await covid_news.send(await httpx_covid_news(msg=True))

@covid_news.got("number")
async def news_data(event: GroupMessageEvent, a: str = ArgPlainText("number")):
    if int(event.group_id) not in group_image_covid:
        await covid_news.finish(await covid_news_n(number=int(a)))
    else:
        b = await CreateImg(text=await covid_news_n(number=int(a)), colour=colour, size=size)
        p = os.path.join('./', os.getcwd(), 'covid_by_19', b + ".png")
        await covid_news.finish(MessageSegment.image(file=str("file:///") + p))

async def httpx_covid_news(msg):
    try:
        header = {
            "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"}
        r = await httpx.AsyncClient().get(
            url='https://interface.sina.cn/app.news/24hours_news.d.json?conf=page&page=1&pageType=kangYiNewsFlash',
            headers=header)
        r = r.json()
    except(httpx.ConnectError, httpx.HTTPError, httpx.NetworkError):
        return logger.error(f'covid_19:资讯获取失败 网络错误')
    else:
        o = []
        for i in range(len(r["data"]["components"][1]["data"])):
            a = i + 1
            o.append(str(a) + "," + str(r["data"]["components"][1]["data"][i]["item"]["info"]["showTimeText"]) + str(
                '  ') + str(r["data"]["components"][1]["data"][i]["item"]["info"]["title"]) + "\n")

    o.append(f"一共查到了{len(o)}条新闻\n想查看请发送序号\n【{await covid_txt()}】")
    logger.success("covid_19:获取新闻成功")
    if msg == None:
        return o
    else:
        return await json_lshi(c=o)

async def covid_news_n(number):
    try:
        header = {
            "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"}
        r = await httpx.AsyncClient().get(
            url='https://interface.sina.cn/app.news/24hours_news.d.json?conf=page&page=1&pageType=kangYiNewsFlash',
            headers=header)
        r = r.json()
        oo = MessageSegment.image(r["data"]["components"][1]["data"][number - 1]["item"]["info"]["mediaInfo"]["avatar"])
        pp = MessageSegment.text(r["data"]["components"][1]["data"][number - 1]["item"]["base"]["base"]["url"])
        ll = MessageSegment.text(r["data"]["components"][1]["data"][number - 1]["item"]["info"]["title"])
    except(KeyError, httpx.NetworkError, httpx.HTTPError):
        return logger.error("covid_19:获取失败")
    else:
        logger.success("covid_19:获取成功")
        return oo + "\n" + ll + "\n" + pp + f"\n【{await covid_txt()}】"

async def httpx_covid_city(msg):
    try:
        header = {
            "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"}
        r = await httpx.AsyncClient().get(url="https://interface.sina.cn/news/wap/fymap2020_data.d.json",
                                          headers=header)
        r = r.json()
        x = r["data"]["list"]
    except(KeyError, httpx.ConnectError, httpx.HTTPError, httpx.NetworkError):
        return logger.error(f'查询{msg}地区出现错误 网络错误')
    else:
        for i in range(len(x)):
            if x[i]["name"] == str(msg):
                logger.success(f"covid_19:{msg}疫情数据成功")
                return f'—{msg}的疫情数据—\n🍁时间:{r["data"]["times"]}\n🍁新增确诊:{x[i]["conadd"]}\n🍁累计确诊:{x[i]["value"]}\n🍁现存确诊:{x[i]["econNum"]}\n🍁死亡人数:{x[i]["deathNum"]}\n🍁治愈人数:{x[i]["cureNum"]}\n🍁境外输入:{x[i]["jwsrNum"]}\n【{await covid_txt()}】'
            else:
                for o in range(len(r["data"]["list"][i]["city"]) - 1):
                    if r["data"]["list"][i]["city"][o]["name"] == str(msg):
                        logger.success(f"covid_19:{msg}疫情数据成功")
                        return f'—{msg}的疫情数据—\n🍁时间:{r["data"]["times"]}\n🍁新增确诊:{x[i]["city"][o]["conadd"]}\n🍁累计确诊:{x[i]["city"][o]["conNum"]}\n🍁现存确诊:{x[i]["city"][o]["econNum"]}\n🍁死亡人数:{x[i]["city"][o]["deathNum"]}\n🍁治愈人数:{x[i]["city"][o]["cureNum"]}\n【{await covid_txt()}】'
        for i in range(len(r["data"]["worldlist"]) - 1):
            if r["data"]["worldlist"][i]["name"] == str(msg):
                logger.success(f"covid_19:{msg}疫情数据成功")
                return f'—{msg}的疫情数据—\n🍁时间:{r["data"]["times"]}\n🍁新增确诊:{r["data"]["worldlist"][i]["conadd"]}\n🍁累计确诊:{r["data"]["worldlist"][i]["value"]}\n🍁现存确诊:{r["data"]["worldlist"][i]["econNum"]}\n🍁死亡人数:{r["data"]["worldlist"][i]["deathNum"]}\n🍁治愈人数:{r["data"]["worldlist"][i]["cureNum"]}\n【{await covid_txt()}】'
        return logger.error(f'查询{msg}地区出现错误 数据解析错误')
