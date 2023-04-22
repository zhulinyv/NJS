import nonebot
from typing import List
from nonebot.rule import Rule
from nonebot.plugin import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment, GroupMessageEvent
import aiohttp, re, os, random, cv2, asyncio, base64

global_config = nonebot.get_driver().config
config = global_config.dict()

imgRoot = config.get('imgroot') if config.get('imgroot') else f"{os.environ['HOME']}/"
proxy_aiohttp = config.get('aiohttp') if config.get('aiohttp') else ""
pixiv_cookies = config.get('pixiv_cookies') if config.get('pixiv_cookies') else ""
ffmpeg = config.get('ffmpeg') if config.get('ffmpeg') else "/usr/bin/ffmpeg"
headersCook = {
    'referer': 'https://www.pixiv.net',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}
if pixiv_cookies:
    headersCook['cookie'] = pixiv_cookies

PIXIV_R18 = config.get('pixiv_r18', 'True')
if PIXIV_R18 and (PIXIV_R18 == 'True' or PIXIV_R18 == 'False'):
    PIXIV_R18 = eval(PIXIV_R18)
elif PIXIV_R18:
    try:
        PIXIV_R18 = eval(PIXIV_R18)
        if not isinstance(PIXIV_R18, list):
            print("配置错误！！pixiv_r18应该是列表")
        else:
            for x in PIXIV_R18:
                if not (isinstance(x, int) or (isinstance(x, str) and str(x).isdigit())):
                    print("配置错误！！pixiv_r18中应该是int类型或者str的数值类型")
        PIXIV_R18 = [int(_) for _ in PIXIV_R18]
    except:
        print("配置错误！！")

BAN_PIXIV_R18 = eval(config.get('ban_pixiv_r18', '[]'))
BAN_PIXIV_R18 = [int(_) for _ in BAN_PIXIV_R18]

pathHome = f"{imgRoot}QQbotFiles/pixiv"
if not os.path.exists(pathHome):
    os.makedirs(pathHome)

pathZipHome = f"{imgRoot}QQbotFiles/pixivZip"
if not os.path.exists(pathZipHome):
    os.makedirs(pathZipHome)


def isPixivURL() -> Rule:
    async def isPixivURL_(bot: "Bot", event: "Event") -> bool:
        if event.get_type() != "message":
            return False
        msg = str(event.get_message())
        if re.findall("https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)", msg):
            return True
        return False

    return Rule(isPixivURL_)


pixivURL = on_message(rule=isPixivURL())


async def validate_r18(bot: Bot, event: Event, PID: str) -> bool:
    if not await pan_R18(PID):
        return True
    if isinstance(PIXIV_R18, bool):
        if not PIXIV_R18:
            await bot.send(event=event, message="不支持R18，请修改配置后操作！")
            return False
        else:
            if isinstance(event, GroupMessageEvent):
                flag = any(True if str(_) == str(event.group_id) else False for _ in BAN_PIXIV_R18)
                if flag:
                    await bot.send(event=event, message="不支持R18，请修改配置后操作！")
                    return False
                return True
    elif isinstance(PIXIV_R18, list):
        if isinstance(event, GroupMessageEvent):
            flag = any(True if str(_) == str(event.group_id) else False for _ in PIXIV_R18)
            if not flag:
                await bot.send(event=event, message="不支持R18，请修改配置后操作！")
            return flag

    return True


@pixivURL.handle()
async def pixiv_URL(bot: Bot, event: Event):
    PID = re.findall("https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)", str(event.get_message()))
    if PID:
        PID = [x for x in PID[0] if x][0]
        if not validate_r18(bot, event, PID):
            return
        xx = (await check_GIF(PID))
        if xx != "NO":
            await GIF_send(xx, PID, event, bot)
        else:
            await send(PID, event, bot)


pixiv = on_regex(pattern="^pixiv\ ")


@pixiv.handle()
async def pixiv_rev(bot: Bot, event: Event):
    PID = str(event.get_plaintext()).strip()[6:].strip()
    if not await validate_r18(bot, event, PID):
        return
    xx = (await check_GIF(PID))
    if xx != "NO":
        print("是动图")
        await GIF_send(xx, PID, event, bot)
    else:
        print("不是动图")
        await send(PID, event, bot)


async def fetch(session, url, name):
    print("发送请求：", url)
    async with session.get(url=url, headers=headersCook, proxy=proxy_aiohttp) as response:
        code = response.status
        if code == 200:
            content = await response.content.read()
            with open(f"{imgRoot}QQbotFiles/pixiv/" + name, mode='wb') as f:
                f.write(content)
            return True
        return False


async def main(PID):
    url = f"https://www.pixiv.net/ajax/illust/{PID}"
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        content = await resp.json()
        # print(content)
        if content.get('error'):
            return
        url = content.get('body').get('urls').get('original')

        if not url:
            print("官方api没找到尝试用第三方api")
            resp2 = await session.get(url=f"https://api.obfs.dev/api/pixiv/illust?id={PID}", headers=headersCook, proxy=proxy_aiohttp)
            cc = await resp2.json()
            if cc.get('error'):
                return
            url = cc.get('illust').get('meta_single_page')
            if url:
                url = url.get('original_image_url')
            else:
                url = cc.get('illust').get('meta_pages')[0].get('image_urls').get('original')
        else:
            print("使用官方api")


        name = url[url.rfind("/") + 1:]
        # 后缀
        suffix = name.split(".")[1]
        names = []
        num = 0
        if os.path.exists(f"{imgRoot}QQbotFiles/pixiv/" + name):
            while os.path.exists(f"{imgRoot}QQbotFiles/pixiv/" + name) and num <= 6:
                names.append(name)
                num += 1
                name = re.sub("_p(\d+)\.(png|jpg|jepg)", f"_p{num}.{suffix}", name)
        else:
            while await fetch(session=session, url=url, name=name) and num <= 6:
                names.append(name)
                num += 1
                url = re.sub("_p(\d+)\.(png|jpg|jepg)", f"_p{num}.{suffix}", url)
                name = url[url.rfind("/") + 1:]
        return names


async def get_Img_ByDay(url):
    async with aiohttp.ClientSession() as session:
        if url == 'day':
            url = 'https://www.pixiv.net/ranking.php'
        else:
            url = f'https://www.pixiv.net/ranking.php?mode={url}'
        response = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        text = (await response.content.read()).decode()
        img_list = set(re.findall('\<a href\=\"\/artworks\/(.*?)\"', text))
        return list(img_list)


pixivRank = on_regex(pattern="^pixivRank\ ")


@pixivRank.handle()
async def pixiv_rev(bot: Bot, event: Event):
    info = str(event.get_plaintext()).strip()[10:].strip()
    dic = {
        "1": "day",
        "7": "weekly",
        "30": "monthly"
    }
    if info in dic.keys():
        img_list = random.choices(await get_Img_ByDay(dic[info]), k=5)
        names = []
        for img in img_list:
            names.append(await main(img))
        if not names:
            await bot.send(event=event, message="发生了异常情况")
        else:
            msg = None
            for name in names:
                if name:
                    for t in name:
                        path = f"{imgRoot}QQbotFiles/pixiv/{t}"
                        size = os.path.getsize(path)
                        if size // 1024 // 1024 >= 10:
                            await ya_suo(path)
                        msg += MessageSegment.image(await base64_path(path))
            try:
                if isinstance(event, GroupMessageEvent):
                    await send_forward_msg_group(bot, event, 'qqbot', msg)
                else:
                    if msg:
                        await bot.send(event=event, message=msg)
            except:
                await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查")
    else:
        await bot.send(event=event, message=Message("参数错误\n样例: 'pixivRank 1' , 1:day,7:weekly,30:monthly"))


async def base64_path(path: str):
    ff = "空"
    with open(path, "rb") as f:
        ff = base64.b64encode(f.read()).decode()
    return f"base64://{ff}"


async def send(PID: str, event: Event, bot: Bot):
    names = await main(PID)
    if not names:
        await bot.send(event=event, message="没有这个PID的图片")
    else:
        msg = None
        for name in names:
            path = f"{imgRoot}QQbotFiles/pixiv/{name}"
            size = os.path.getsize(path)
            if size // 1024 // 1024 >= 10:
                await ya_suo(path)
            msg += MessageSegment.image(await base64_path(path))
        try:
            if isinstance(event, GroupMessageEvent):
                await send_forward_msg_group(bot, event, 'qqbot', msg)
            else:
                await bot.send(event=event, message=msg)

        except:
            try:
                for name in names:
                    path = f"{imgRoot}QQbotFiles/pixiv/{name}"
                    os.system(f"echo '1' >> {path}")
                msg = None
                for name in names:
                    path = f"{imgRoot}QQbotFiles/pixiv/{name}"
                    size = os.path.getsize(path)
                    if size // 1024 // 1024 >= 10:
                        await ya_suo(path)
                    msg += MessageSegment.image(await base64_path(path))
                if isinstance(event, GroupMessageEvent):
                    await send_forward_msg_group(bot, event, 'qqbot', msg)
                else:
                    await bot.send(event=event, message=msg)
            except:
                await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查!!!")


# 压缩图片大小
async def ya_suo(path):
    while os.path.getsize(path) // 1024 // 1024 >= 10:
        image = cv2.imread(path)
        shape = image.shape
        res = cv2.resize(image, (shape[1] // 2, shape[0] // 2), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f"{path}", res)


# 非动图返回 "NO", 动图返回下载地址
async def check_GIF(PID: str) -> str:
    url = f'https://www.pixiv.net/ajax/illust/{PID}/ugoira_meta'
    async with aiohttp.ClientSession() as session:
        if pixiv_cookies:
            headersCook['cookie'] = pixiv_cookies
        resp = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        content = await resp.json()
        if content['error']:
            return "NO"
        return content['body']['originalSrc']


async def GIF_send(url: str, PID: str, event: Event, bot: Bot):
    path_pre = f"{imgRoot}QQbotFiles/pixivZip/{PID}"
    if os.path.exists(f"{path_pre}/{PID}.gif"):
        size = os.path.getsize(f"{path_pre}/{PID}.gif")
        while size // 1024 // 1024 >= 15:
            msg = await run(f"file {path_pre}/{PID}.gif")
            chang = int(msg.split(" ")[-3]) // 2
            kuan = int(msg.split(" ")[-1]) // 2
            await run(f"{ffmpeg} -i {path_pre}/{PID}.gif -s {chang}x{kuan} {path_pre}/{PID}_temp.gif")
            await run(f"rm -rf {path_pre}/{PID}.gif")
            await run(f"mv {path_pre}/{PID}_temp.gif {path_pre}/{PID}.gif")
            size = os.path.getsize(f"{path_pre}/{PID}.gif")
        try:
            await bot.send(event=event, message=MessageSegment.image(await base64_path(f"{path_pre}/{PID}.gif")))
        except:
            await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查")
        return
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        code = response.status
        if code == 200:
            content = await response.content.read()
            if not os.path.exists(f"{path_pre}.zip"):
                with open(f"{path_pre}.zip", mode='wb') as f:
                    f.write(content)
                if not os.path.exists(f"{path_pre}"):
                    os.mkdir(f"{path_pre}")
            await run(f"unzip -n {path_pre}.zip -d {path_pre}")
            image_list = sorted(os.listdir(f"{path_pre}"))
            await run(f"rm -rf {path_pre}.zip")
            await run(f"{ffmpeg} -r {len(image_list)} -i {path_pre}/%06d.jpg {path_pre}/{PID}.gif -n")
            # 压缩
            size = os.path.getsize(f"{path_pre}/{PID}.gif")
            while size // 1024 // 1024 >= 15:
                msg = await run(f"file {path_pre}/{PID}.gif")
                chang = int(msg.split(" ")[-3]) // 2
                kuan = int(msg.split(" ")[-1]) // 2
                await run(f"{ffmpeg} -i {path_pre}/{PID}.gif -s {chang}x{kuan} {path_pre}/{PID}_temp.gif")
                await run(f"rm -rf {path_pre}/{PID}.gif")
                await run(f"mv {path_pre}/{PID}_temp.gif {path_pre}/{PID}.gif")
                size = os.path.getsize(f"{path_pre}/{PID}.gif")
            try:
                await bot.send(event=event, message=MessageSegment.image(await base64_path(f"{path_pre}/{PID}.gif")))
            except:
                await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查")


async def run(cmd: str):
    print(cmd)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    return (stdout + stderr).decode()


# 合并消息
async def send_forward_msg_group(
        bot: Bot,
        event: GroupMessageEvent,
        name: str,
        msgs: List[str],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": bot.self_id, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )


async def pan_R18(PID) -> bool:
    url = f"https://www.pixiv.net/ajax/illust/{PID}"
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        content = await resp.json()
        if content.get('error'):
            return False
        tag = content['body']['tags']['tags'][0]['tag']
        if tag == 'R-18':
            print("是R-18")
            return True
        else:
            print("不是R-18")
            return False
