import asyncio
import datetime
import math
import random
from argparse import Namespace
from dataclasses import dataclass
from io import BytesIO
from typing import Dict, List, Optional

from nonebot import on_command, on_shell_command
from nonebot.adapters.onebot.v11 import (
    ActionFailed,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.exception import FinishedException, ParserExit
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.rule import ArgumentParser
from nonebot_plugin_apscheduler import scheduler
from pil_utils import BuildImage

from .config import config
from .data_bawiki import (
    MangaDict,
    db_get,
    db_get_emoji,
    db_get_event_alias,
    db_get_extra_l2d_list,
    db_get_gacha_data,
    db_get_manga,
    db_get_raid_alias,
    db_get_stu_alias,
    db_get_terrain_alias,
    db_global_future,
    db_wiki_craft,
    db_wiki_event,
    db_wiki_furniture,
    db_wiki_raid,
    db_wiki_stu,
    db_wiki_time_atk,
    recover_stu_alia,
    schale_to_gamekee,
)
from .data_gamekee import (
    GameKeeVoice,
    game_kee_calender,
    game_kee_get_page,
    game_kee_get_stu_cid_li,
    game_kee_get_voice,
    game_kee_grab_l2d,
    game_kee_page_url,
)
from .data_schaledb import (
    draw_fav_li,
    find_current_event,
    schale_calender,
    schale_get_common,
    schale_get_stu_dict,
    schale_get_stu_info,
)
from .gacha import gacha
from .util import async_req, clear_req_cache, recover_alia, splice_msg


@dataclass()
class GachaPool:
    name: str
    pool: List[int]
    index: Optional[int] = None


gacha_pool_index: Dict[str, GachaPool] = {}


@scheduler.scheduled_job("interval", hours=3)
async def _():
    clear_req_cache()


h_clear_cache = on_command("ba清空缓存", aliases={"ba清除缓存"}, permission=SUPERUSER)


@h_clear_cache.handle()
async def _(matcher: Matcher):
    clear_req_cache()
    await matcher.finish("缓存已清空～")


handler_calender = on_command("ba日程表")


@handler_calender.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg: str = cmd_arg.extract_plain_text()

    await matcher.send("正在绘制图片，请稍等")
    try:
        if "schale" in (arg := arg.lower()):
            arg = arg.replace("schale", "").strip()
            servers = []

            if (not arg) or ("日" in arg) or ("j" in arg):
                servers.append(0)
            if (not arg) or ("国" in arg) or ("g" in arg):
                servers.append(1)

            await asyncio.gather(
                *[
                    matcher.send(x)
                    for x in (
                        await asyncio.gather(*[schale_calender(x) for x in servers])
                    )
                ]
            )
            await matcher.finish()
        else:
            await matcher.finish(await game_kee_calender())
    except (FinishedException, ActionFailed):  # type: ignore
        raise
    except:
        logger.exception("绘制日程表图片出错")
        return await matcher.finish("绘制日程表图片出错，请检查后台输出")


async def send_wiki_page(sid, matcher: Matcher):
    url = game_kee_page_url(sid)
    await matcher.send(f"请稍等，正在截取Wiki页面……\n{url}")

    try:
        img = await game_kee_get_page(url)
    except:
        logger.exception(f"截取wiki页面出错 {url}")
        return await matcher.finish("截取页面出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(img))


stu_schale = on_command("ba学生图鉴")


@stu_schale.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    try:
        ret = await schale_get_stu_dict()
    except:
        logger.exception("获取学生列表出错")
        return await matcher.finish("获取学生列表表出错，请检查后台输出")

    if not ret:
        return await matcher.finish("没有获取到学生列表数据")

    if not (data := ret.get(await recover_stu_alia(arg))):
        return await matcher.finish("未找到该学生")

    stu_name = data["PathName"]
    await matcher.send(f"请稍等，正在截取SchaleDB页面～\n{config.ba_schale_url}?chara={stu_name}")

    try:
        img = MessageSegment.image(await schale_get_stu_info(stu_name))
    except:
        logger.exception(f"截取schale db页面出错 chara={stu_name}")
        return await matcher.finish("截取页面出错，请检查后台输出")

    await matcher.finish(img)


stu_rank = on_command("ba学生评价", aliases={"ba角评"})


@stu_rank.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    if arg == "总览" or arg == "全部" or arg.lower() == "all":
        arg = "all"
    else:
        arg = await recover_stu_alia(arg)

    try:
        im = await db_wiki_stu(arg)
    except:
        logger.exception("获取角评出错")
        return await matcher.finish("获取角评出错，请检查后台输出")

    await matcher.finish(im)


stu_wiki = on_command("ba学生wiki", aliases={"ba学生Wiki", "ba学生WIKI"})


@stu_wiki.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    try:
        ret = await game_kee_get_stu_cid_li()
    except:
        logger.exception("获取学生列表出错")
        return await matcher.finish("获取学生列表出错，请检查后台输出")

    if not ret:
        return await matcher.finish("没有获取到学生列表数据")

    if not (sid := ret.get(await recover_stu_alia(arg, True))):
        return await matcher.finish("未找到该学生")

    await send_wiki_page(sid, matcher)


fav = on_command("ba好感度", aliases={"ba羁绊", "bal2d", "baL2D", "balive2d", "baLive2D"})


@fav.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    async def get_l2d(stu_name):
        if r := (await db_get_extra_l2d_list()).get(stu_name):
            return f"{config.ba_bawiki_db_url}{r}"

        return await game_kee_grab_l2d((await game_kee_get_stu_cid_li()).get(stu_name))

    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称或所需的羁绊等级")

    # 好感度等级
    if arg.isdigit():
        arg = int(arg)
        if arg > 9:
            return await matcher.finish("学生解锁L2D最高只需要羁绊等级9")
        if arg < 1:
            return await matcher.finish("学生解锁L2D最低只需要羁绊等级1")

        try:
            p = await draw_fav_li(arg)
        except:
            logger.exception("绘制图片出错")
            return await matcher.finish("绘制图片出错，请检查后台输出")

        return await matcher.finish(p)

    # 学生名称
    arg = await recover_stu_alia(arg)

    try:
        ret = await schale_get_stu_dict()
    except:
        logger.exception("获取学生列表出错")
        return await matcher.finish("获取学生列表表出错，请检查后台输出")

    if stu := ret.get(arg):
        if not (lvl := stu["MemoryLobby"]):
            return await matcher.finish("该学生没有L2D")

        im = MessageSegment.text(f'{stu["Name"]} 在羁绊等级 {lvl[0]} 时即可解锁L2D\nL2D预览：')
        if p := await get_l2d(await schale_to_gamekee(arg)):
            im += [MessageSegment.image(await async_req(x, raw=True)) for x in p]
        else:
            im += (
                "没找到该学生的L2D看板\n"
                "可能原因：\n"
                "- GameKee页面爬取不到角色L2D图片\n"
                "- GameKee和插件没有收录该学生的L2D\n"
            )
        return await matcher.finish(im)

    return await matcher.finish("未找到学生")


raid_wiki_parser = ArgumentParser("ba总力战")
raid_wiki_parser.add_argument(
    "name", nargs="?", default=None, help="总力战Boss名称，不指定默认取当前服务器总力战Boss"
)
raid_wiki_parser.add_argument(
    "-s",
    "--server",
    nargs="*",
    help="服务器名称，`j`或`日`代表日服，`g`或`国`代表国际服，可指定多个，默认全选",
    default=["j", "g"],
)
raid_wiki_parser.add_argument("-t", "--terrain", help="指定总力战环境，不指定默认全选，不带Boss名称该参数无效")
raid_wiki_parser.add_argument(
    "-w", "--wiki", action="store_true", help="发送该总力战Boss的技能机制而不是配队推荐"
)

raid_wiki = on_shell_command("ba总力战", parser=raid_wiki_parser)


@raid_wiki.handle()
async def _(matcher: Matcher, foo: ParserExit = ShellCommandArgs()):
    im = ""
    if foo.status != 0:
        im = "参数错误\n"
    await matcher.finish(f"{im}{foo.message}")


@raid_wiki.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    if not args.server:
        await matcher.finish("请指定server参数")

    server = set()
    for s in args.server:
        if ("日" in s) or ("j" in s):
            server.add(0)
        elif ("国" in s) or ("g" in s):
            server.add(1)
    server = list(server)
    server.sort()

    tasks = []
    if not args.name:
        try:
            common = await schale_get_common()
            for s in server:
                raid = common["regions"][s]["current_raid"]
                if (r := find_current_event(raid)) and (raid := r[0]["raid"]) < 1000:
                    tasks.append(
                        db_wiki_raid(raid, [s], args.wiki, r[0].get("terrain"))
                    )
        except:
            logger.exception("获取当前总力战失败")
            return await matcher.finish("获取当前总力战失败")

        if not tasks:
            return await matcher.finish("目前服务器没有正在进行的总力战，请手动指定")
    else:
        tasks.append(
            db_wiki_raid(
                recover_alia(args.name, await db_get_raid_alias()),
                server,
                args.wiki,
                (
                    recover_alia(args.terrain, await db_get_terrain_alias())
                    if args.terrain
                    else None
                ),
            )
        )

    try:
        ret = await asyncio.gather(*tasks)
    except:
        logger.exception("获取总力战wiki失败")
        return await matcher.finish("获取图片失败，请检查后台输出")

    await matcher.finish(splice_msg(ret))


event_wiki = on_command("ba活动")


@event_wiki.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().lower().strip()

    server = []
    if arg.startswith("日") or arg.startswith("j") or (not arg):
        server.append(0)
    if arg.startswith("国") or arg.startswith("g") or (not arg):
        server.append(1)

    events = []
    if server:
        try:
            common = await schale_get_common()
            for s in server:
                ev = common["regions"][s]["current_events"]
                if e := find_current_event(ev):
                    events.append((e[0]["event"]) % 10000)
        except:
            logger.exception("获取当前活动失败")
            return await matcher.finish("获取当前活动失败")

        if not events:
            await matcher.finish("当前服务器没有正在进行的活动")

    else:
        events.append(recover_alia(arg, await db_get_event_alias()))

    try:
        ret = await asyncio.gather(*[db_wiki_event(x) for x in events])
    except:
        logger.exception("获取活动wiki出错")
        return await matcher.finish("获取图片出错，请检查后台输出")

    await matcher.finish(splice_msg(ret))


time_atk_wiki = on_command("ba综合战术考试", aliases={"ba合同火力演习", "ba战术考试", "ba火力演习"})


@time_atk_wiki.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().lower().strip()

    server = []
    if arg.startswith("日") or arg.startswith("j") or (not arg):
        server.append(0)
    if arg.startswith("国") or arg.startswith("g") or (not arg):
        server.append(1)

    events = []
    if server:
        try:
            common = await schale_get_common()
            for s in server:
                raid = common["regions"][s]["current_raid"]
                if (r := find_current_event(raid)) and (raid := r[0]["raid"]) >= 1000:
                    events.append(raid)
        except:
            logger.exception("获取当前综合战术考试失败")
            return await matcher.finish("获取当前综合战术考试失败")

        if not events:
            await matcher.finish("当前服务器没有正在进行的综合战术考试")

    else:
        if (not str(arg).isdigit()) or ((arg := int(arg)) < 1):
            await matcher.finish("综合战术考试ID需为整数，从1开始，代表第1个综合战术考试")
        events.append(arg)

    try:
        ret = await asyncio.gather(*[db_wiki_time_atk(x) for x in events])
    except:
        logger.exception("获取综合战术考试wiki出错")
        return await matcher.finish("获取图片出错，请检查后台输出")

    await matcher.finish(splice_msg(ret))


craft_wiki = on_command("ba制造", aliases={"ba合成", "ba制作"})


@craft_wiki.handle()
async def _(matcher: Matcher):
    try:
        im = await db_wiki_craft()
    except:
        logger.exception("获取合成wiki图片错误")
        return await matcher.finish("获取图片失败，请检查后台输出")

    await matcher.finish(im)


global_future = on_command("ba国际服千里眼", aliases={"ba千里眼", "ba国际服前瞻", "ba前瞻"})


@global_future.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip()
    if "全" in args or "a" in args:
        await matcher.finish(await db_global_future(all_img=True))

    args = args.split()
    num = 1
    date = None
    if (args_len := len(args)) == 1:
        if args[0].isdigit():
            num = args[0]
        else:
            date = args[0]
    elif args_len > 1:
        date = args[0].strip()
        num = args[-1].strip()

    if date:
        parsed_date = None
        for f in ["%Y/%m/%d", "%Y-%m-%d", "%Y年%m月%d日", "%m/%d", "%m-%d", "%m月%d日"]:
            try:
                parsed_date = datetime.datetime.strptime(date.replace(" ", ""), f)
                break
            except ValueError:
                pass
        if not parsed_date:
            await matcher.finish("日期格式不正确！")
        date = parsed_date
        if date.year == 1900:
            now = datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            date = date.replace(year=now.year)
            if date < now:
                date = date.replace(year=now.year + 1)

    if isinstance(num, str):
        if (not num.isdigit()) or (num := int(num)) < 1:
            await matcher.finish("前瞻项目数量格式不正确！")

    await matcher.finish(await db_global_future(date, num))


furniture_wiki = on_command("ba互动家具")


@furniture_wiki.handle()
async def _(matcher: Matcher):
    try:
        im = await db_wiki_furniture()
    except:
        logger.exception("获取互动家具wiki图片错误")
        return await matcher.finish("获取图片失败，请检查后台输出")

    await matcher.finish(im)


voice = on_command("ba语音")


@voice.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    arg = arg.split()
    arg_len = len(arg)
    name = " ".join(arg[:-1]) if arg_len > 1 else arg[0]
    v_type = arg[-1].strip().lower() if arg_len > 1 else None

    try:
        ret = await game_kee_get_stu_cid_li()
    except:
        logger.exception("获取学生列表出错")
        return await matcher.finish("获取学生列表出错，请检查后台输出")

    if not ret:
        return await matcher.finish("没有获取到学生列表数据")

    try:
        org_stu_name = await recover_stu_alia(name, True)
        stu_name = await schale_to_gamekee(org_stu_name)
    except:
        logger.exception("还原学生别名失败")
        return await matcher.finish("还原学生别名失败，请检查后台输出")

    if not (sid := ret.get(stu_name)):
        return await matcher.finish("未找到该学生")

    voices = await game_kee_get_voice(sid)
    if v_type:
        voices = [x for x in voices if v_type in x.title.lower()]
    if not voices:
        await matcher.finish("没找到符合要求的语音捏")

    v: GameKeeVoice = random.choice(voices)
    v_data = await async_req(v.url, raw=True)

    im = [f"学生 {org_stu_name} 语音 {v.title}\n-=-=-=-=-=-=-=-"]
    if v.jp:
        im.append(v.jp)
    if v.cn:
        im.append(v.cn)
    await matcher.send("\n".join(im))
    await matcher.send(MessageSegment.record(v_data))


def get_1st_pool(data: dict) -> Optional[GachaPool]:
    if not data:
        return

    pool_data = data["current_pools"]
    pool = pool_data[0]
    pool_obj = GachaPool(name=pool["name"], pool=pool["pool"], index=0)
    return pool_obj


change_pool = on_command("ba切换卡池")


@change_pool.handle()
async def _(matcher: Matcher, event: MessageEvent, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip().lower()
    qq = event.get_user_id()

    if arg:
        if "常驻" in arg:
            current = GachaPool(name="常驻池", pool=[])
        else:
            pool = []
            try:
                stu_li = await schale_get_stu_dict()
                stu_alias = await db_get_stu_alias()
            except:
                logger.exception("获取学生列表或别名失败")
                return await matcher.finish("获取学生列表或别名失败，请检查后台输出")

            for i in arg.split():
                if not (stu := stu_li.get(recover_alia(i, stu_alias))):
                    await matcher.finish(f"未找到学生 {i}")
                if stu["StarGrade"] == 1:
                    await matcher.finish("不能UP一星角色")
                pool.append(stu)

            current = GachaPool(
                name=f"自定义卡池（{'、'.join([x['Name'] for x in pool])}）",
                pool=[x["Id"] for x in pool],
            )

    else:
        try:
            gacha_data = await db_get_gacha_data()
        except:
            logger.exception("获取抽卡基本数据失败")
            return await matcher.finish("获取抽卡基本数据失败，请检查后台输出")

        pool_data = gacha_data["current_pools"]
        if not pool_data:
            await matcher.finish("当前没有可切换的卡池")

        pool_obj = gacha_pool_index.get(qq) or get_1st_pool(gacha_data)
        if not pool_obj:
            await matcher.finish("当前没有UP池可供切换")

        if (index := pool_obj.index) is not None:
            index += 1
            if len(pool_data) <= index:
                index = 0
        else:
            index = 0

        pool = pool_data[index]
        current = GachaPool(name=pool["name"], pool=pool["pool"], index=index)

    gacha_pool_index[qq] = current
    await matcher.finish(f"已切换到卡池 {current.name}")


gacha_once = on_command("ba抽卡")


@gacha_once.handle()
async def _(matcher: Matcher, event: MessageEvent, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip().lower()

    gacha_times = 10
    if arg:
        if (not arg.isdigit()) or (not (1 <= (gacha_times := int(arg)) <= 90)):
            await matcher.finish("请输入有效的抽卡次数，在1~90之间")

    try:
        gacha_data = await db_get_gacha_data()
    except:
        logger.exception("获取抽卡基本数据失败")
        return await matcher.finish("获取抽卡基本数据失败，请检查后台输出")

    pool_obj = gacha_pool_index.get(qq := event.get_user_id()) or get_1st_pool(
        gacha_data
    )
    if not pool_obj:
        await matcher.finish("目前没有UP池，请使用[ba切换卡池]指令来切换到常驻池或组建一个自定义UP池")

    try:
        img = []
        for _ in range(math.ceil(gacha_times / 10)):
            img.append(
                await gacha(
                    qq,
                    10 if gacha_times >= 10 else gacha_times,
                    gacha_data,
                    pool_obj.pool,
                )
            )
            gacha_times -= 10
    except:
        logger.exception("抽卡错误")
        return await matcher.finish("抽卡出错了，请检查后台输出")

    await matcher.finish(MessageSegment.at(qq) + f"当前抽取卡池：{pool_obj.name}" + img)


random_emoji = on_command("ba表情")


@random_emoji.handle()
async def _(matcher: Matcher):
    try:
        emojis = await db_get_emoji()
        emo = await db_get(random.choice(emojis), True)
    except:
        logger.exception("获取表情失败")
        return await matcher.finish("获取表情失败，请检查后台输出")
    await matcher.finish(MessageSegment.image(emo))


random_manga = on_command("ba漫画")


@random_manga.handle()
async def _(matcher: Matcher):
    async def get_pic(url):
        p = await async_req(url, raw=True)
        if url.endswith(".webp"):
            p = BuildImage.open(BytesIO(p)).save_png()
        return p

    try:
        manga: MangaDict = random.choice(await db_get_manga())
        pics = await asyncio.gather(*[get_pic(x) for x in manga["pics"]])
    except:
        logger.exception("获取漫画失败")
        return await matcher.finish("获取漫画失败，请检查后台输出")

    await matcher.finish(
        Message()
        + f'{manga["title"]}\n-=-=-=-=-=-=-=-\n{manga["detail"]}'
        + [MessageSegment.image(x) for x in pics]
    )
