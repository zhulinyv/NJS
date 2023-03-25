"""游戏公告推送"""
from pathlib import Path

from aiofiles import open as aopen
from nonebot import logger, get_bot, on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, Message
from nonebot.exception import ActionFailed
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_htmlrender import html_to_pic

from .data_source import get_news
from ..configs.scheduler_config import SchedulerConfig
from ..core.database import RSSNewsModel

scfg = SchedulerConfig.parse_obj(get_driver().config.dict())

latest_news = on_command("方舟最新公告")
add_group = on_command("添加方舟推送群", aliases={"ADDGROUP"})
del_group = on_command("删除方舟推送群", aliases={"DELGROUP"})
get_group = on_command("查看方舟推送群", aliases={"GETGROUP"})


@latest_news.handle()
async def _():
    news = await RSSNewsModel.all().order_by("time").first()
    await latest_news.send("获取最新公告中 ...")
    if not news:
        try:
            news_list = await get_news()
        except:
            logger.error("获取最新公告出错")
        else:
            news = news_list[0]

    image = await html_to_pic(
        html=news.content
    )
    try:
        await latest_news.finish(
            Message(
                MessageSegment.image(image)
                + "舟舟发布了一条新公告"
                  f"\n发布时间: {news.time.__str__()[:10]}"
                  f"\n{news.link}"
            )
        )
    except ActionFailed as e:
        await latest_news.finish(
            "公告截图失败..."
            f"\n发布时间: {news.time.__str__()[:10]}"
            f"\n{news.link}"
        )


@add_group.handle()
async def _(arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip().split()
    if not args or not all((_.isnumeric() for _ in args)):
        await add_group.finish()

    if not (Path(__file__).parent / "groups.txt").exists():
        async with aopen(Path(__file__).parent / "groups.txt", "w") as fp:
            await fp.write(f"{' '.join(args)}")
        await add_group.finish("添加成功！", at_sender=True)

    async with aopen(Path(__file__).parent / "groups.txt", "r") as fp:
        local_groups = await fp.read()
    async with aopen(Path(__file__).parent / "groups.txt", "w") as fp:
        await fp.write(" ".join(list(set(local_groups.split() + args))))
    await add_group.finish("添加成功！", at_sender=True)


@del_group.handle()
async def _(arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip().split()
    if not args or not all((_.isnumeric() for _ in args)):
        await del_group.finish()

    if not (Path(__file__).parent / "groups.txt").exists():
        async with aopen(Path(__file__).parent / "groups.txt", "w") as fp:
            pass
        await del_group.finish("删除成功！", at_sender=True)

    async with aopen(Path(__file__).parent / "groups.txt", "r") as fp:
        local_groups = await fp.read()
    async with aopen(Path(__file__).parent / "groups.txt", "w") as fp:
        groups = {
            _ for _ in local_groups.split()
            if _ not in args
        }
        await fp.write(f"{' '.join(list(groups))}")
    await del_group.finish("删除成功！", at_sender=True)


@get_group.handle()
async def _():
    if not (Path(__file__).parent / "groups.txt").exists():
        await get_group.finish("小笨蛋，尚未添加任何推送群哦！", at_sender=True)

    async with aopen(Path(__file__).parent / "groups.txt", "r") as fp:
        groups = await fp.read()
    if not groups:
        await get_group.finish("小笨蛋，尚未添加任何推送群哦！", at_sender=True)

    await get_group.finish(
        "当前自动推送最新公告的群聊: "
        f"\n{', '.join(groups.split())}"
    )


@scheduler.scheduled_job(
    "interval",
    minutes=scfg.announce_push_interval,
)
async def _():
    if scfg.announce_push_switch:
        logger.info("checking rss news...")
        try:
            bot: Bot = get_bot()
        except ValueError:
            pass

        try:
            news_list = await get_news()
        except:  # TODO
            logger.error("获取最新公告出错")
        else:
            if news_list:
                if not (Path(__file__).parent / "groups.txt").exists():
                    async with aopen(Path(__file__).parent / "groups.txt", "w") as fp:
                        pass
                async with aopen(Path(__file__).parent / "groups.txt", "r") as fp:
                    groups = (await fp.read()).split()
                if groups:
                    for news in news_list:
                        for group in groups:
                            image = await html_to_pic(
                                html=news.content
                            )
                            try:
                                await bot.send_group_msg(
                                    group_id=int(group),
                                    message=Message(
                                        MessageSegment.image(image)
                                        + "舟舟发布了一条新公告"
                                          f"\n发布时间: {news.time.__str__()[:10]}"
                                          f"\n{news.link}"
                                    )
                                )
                            except ActionFailed as e:
                                await bot.send_group_msg(
                                    group_id=int(group),
                                    message=Message(
                                        "公告截图失败..."
                                        f"\n发布时间: {news.time.__str__()[:10]}"
                                        f"\n{news.link}"
                                    )
                                )


__plugin_meta__ = PluginMetadata(
    name="公告推送",
    description="获取并推送最新的方舟公告/新闻",
    usage=(
        "命令:"
        "\n    方舟最新公告 => 获取最新公告"
        "\n    添加方舟推送群 / ADDGROUP   => 添加自动推送的群号"
        "\n    删除方舟推送群 / DELGROUP   => 删除自动推送的群号"
        "\n    查看方舟推送群 / GETGROUP   => 查看自动推送的群号"
        "\n无命令:"
        "\n    自动推送方舟最新公告的截图、发布时间、链接"
    ),
    extra={
        "name": "announce_push",
        "author": "NumberSir<number_sir@126.com>",
        "version": "0.1.0"
    }
)
