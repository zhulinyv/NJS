from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, MessageEvent
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from .data_source import tarot_manager

__tarot_version__ = "v0.4.0.post4"
__tarot_usages__ = f'''
塔罗牌 {__tarot_version__}
[占卜] 随机选取牌阵进行占卜
[塔罗牌] 得到单张塔罗牌回应
[开启/启用/关闭/禁用]群聊转发 开启或关闭全局群聊转发'''.strip()

__plugin_meta__ = PluginMetadata(
    name="塔罗牌",
    description="塔罗牌！魔法占卜🔮",
    usage=__tarot_usages__,
    extra={
        "author": "KafCoppelia <k740677208@gmail.com>",
        "version": __tarot_version__
    }
)

divine = on_command(cmd="占卜", priority=7)
tarot = on_command(cmd="塔罗牌", priority=7)
chain_reply_switch = on_regex(
    pattern=r"^(开启|启用|关闭|禁用)群聊转发(模式)?$", permission=SUPERUSER, priority=7, block=True)


@divine.handle()
async def general_divine(bot: Bot, matcher: Matcher, event: MessageEvent):
    arg: str = event.get_plaintext()

    if "帮助" in arg[-2:]:
        await matcher.finish(__tarot_usages__)

    await tarot_manager.divine(bot, matcher, event)


@tarot.handle()
async def _(matcher: Matcher, event: MessageEvent):
    arg: str = event.get_plaintext()

    if "帮助" in arg[-2:]:
        await matcher.finish(__tarot_usages__)

    msg = await tarot_manager.onetime_divine()
    await matcher.finish(msg)


@chain_reply_switch.handle()
async def _(event: GroupMessageEvent):
    arg: str = event.get_plaintext()

    if arg[:2] == "开启" or arg[:2] == "启用":
        tarot_manager.switch_chain_reply(True)
        msg = "占卜群聊转发模式已开启~"
    else:
        tarot_manager.switch_chain_reply(False)
        msg = "占卜群聊转发模式已关闭~"

    await chain_reply_switch.finish(msg)
