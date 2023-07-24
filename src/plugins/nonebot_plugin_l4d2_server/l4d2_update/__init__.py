from typing import Any, Tuple

from nonebot import get_bot, get_driver, on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import RegexGroup
from nonebot.permission import SUPERUSER

from ..l4d2_utils.rule import FullCommand
from ..l4d2_utils.utils import register_menu
from .draw_update_log import draw_update_log_img
from .restart import restart_genshinuid, restart_message

l4d_restart = on_command("l4重启", rule=FullCommand())
get_update_log = on_command("l4更新记录", rule=FullCommand())
l4d_update = on_regex(
    r"^(l4)(强行)?(强制)?(更新)$",
    block=True,
)


driver = get_driver()


@driver.on_bot_connect
async def _():
    logger.info("检查遗留信息...")
    bot = get_bot()
    update_log = await restart_message()
    if update_log == {}:
        return
    if update_log["send_type"] == "group":
        await bot.call_api(
            api="send_group_msg",
            group_id=update_log["send_to"],
            message=update_log["msg"],
        )
    else:
        await bot.call_api(
            api="send_private_msg",
            user_id=update_log["send_to"],
            message=update_log["msg"],
        )
    logger.info("遗留信息检查完毕!")


@get_update_log.handle()
@register_menu(
    "更新记录",
    "更新记录",
    "查看插件最近的更新记录",
    detail_des=(
        "介绍：\n" "查看插件最近的有效Git更新记录\n" " \n" "指令：\n" "- <ft color=(238,120,0)>更新记录</ft>"
    ),
)
async def send_updatelog_msg(
    matcher: Matcher,
):
    im = await draw_update_log_img(is_update=False)
    logger.info("正在执行[更新记录]...")
    if isinstance(im, str):
        await matcher.finish(im)
    elif isinstance(im, bytes):
        await matcher.finish(MessageSegment.image(im))
    else:
        await matcher.finish("发生了未知错误,请联系管理员检查后台输出!")


@l4d_restart.handle()
@register_menu(
    "重启Bot",
    "l4重启",
    "重启Bot框架",
    trigger_method="超级用户指令",
    detail_des=("介绍：\n" "重启Bot框架\n" " \n" "指令：\n" "- <ft color=(238,120,0)>l4重启</ft>"),
)
async def send_restart_msg(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
):
    if not await SUPERUSER(bot, event):
        return
    logger.warning("开始执行[重启]")
    qid = event.user_id
    if len(event.get_session_id().split("_")) == 3:
        send_id = event.get_session_id().split("_")[1]
        send_type = "group"
    else:
        send_id = qid
        send_type = "private"
    await matcher.send("正在执行[l4重启]...")
    await restart_genshinuid(send_type, str(send_id))


@l4d_update.handle()
@register_menu(
    "更新插件",
    "l4更新",
    "手动更新插件",
    detail_des=(
        "介绍：\n"
        "手动更新插件（执行 git pull）\n"
        "每加上一个可选参数，执行等级加1\n"
        "当执行等级≥1时会还原上次更改，等级≥2时会清空暂存\n"
        " \n"
        "指令：\n"
        "- <ft color=(238,120,0)>l4d</ft>"
        "<ft color=(125,125,125)>(强行)(强制)</ft>"
        "<ft color=(238,120,0)>更新</ft>"
    ),
)
async def send_update_msg(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    args: Tuple[Any, ...] = RegexGroup(),
):
    if not await SUPERUSER(bot, event):
        return

    logger.info("[l4更新] 正在执行 ...")
    level = 2
    if args[1] is None:
        level -= 1
    if args[2] is None:
        level -= 1
    logger.info(f"[l4更新] 更新等级为{level}")
    await matcher.send(f"开始执行[l4更新], 执行等级为{level}")
    im = await draw_update_log_img(level)
    if isinstance(im, str):
        await matcher.finish(im)
    elif isinstance(im, bytes):
        await matcher.finish(MessageSegment.image(im))
    else:
        await matcher.finish("发生了未知错误,请联系管理员检查后台输出!")
