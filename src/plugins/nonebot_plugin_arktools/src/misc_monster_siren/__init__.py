"""即点歌"""
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg, Arg
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message

from .data_source import search_cloud, search_tencent


siren = on_command("塞壬点歌")


@siren.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    args = args.extract_plain_text().strip()
    if args:
        matcher.set_arg("keywords", args)


@siren.got(key="keywords", prompt="请发送要点的歌名:")
async def _(keywords: str = Arg()):
    await siren.send("搜索中...")
    await siren.finish(
        await search_cloud(keywords)
    )


__plugin_meta__ = PluginMetadata(
    name="塞壬点歌",
    description="即网易云点歌",
    usage=(
        "命令:"
        "\n    塞壬点歌 [歌曲名] => 点歌，以卡片形式发到群内"
    ),
    extra={
        "name": "monster_siren",
        "author": "NumberSir<number_sir@126.com>",
        "version": "0.1.0"
    }
)
