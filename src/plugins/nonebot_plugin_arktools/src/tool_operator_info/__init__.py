"""
获取干员信息：
1. 技能 1~7 升级材料 √
2. 精英化材料 √
3. 技能专精材料 √
4. 模组升级材料 √
5. 模组任务
6. 基本信息: HandbookInfo
"""
from nonebot import on_command, logger
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .data_source import BuildOperatorInfo
from ..core.models_v3 import Character
from ..exceptions import *
from ..utils.general import nickname_swap

operator_info = on_command("方舟干员", aliases={"干员"})


@operator_info.handle()
async def _(arg: Message = CommandArg()):
    name = arg.extract_plain_text().strip()
    if not name:
        await operator_info.finish()

    try:
        name = await nickname_swap(name)
        cht = await Character.parse_name(name)
    except NamedCharacterNotExistException as e:
        await operator_info.finish(e.msg, at_sender=True)

    try:
        img_bytes = await BuildOperatorInfo(cht=cht).build_whole_image()
    except FileNotFoundError as e:
        logger.error("干员信息缺失，请使用 “更新方舟素材” 命令更新游戏素材后重试")
        await operator_info.finish(f"缺失干员信息：{name}, 请使用 “更新方舟素材” 命令更新游戏素材后重试")
    await operator_info.finish(MessageSegment.image(img_bytes))


__plugin_meta__ = PluginMetadata(
    name="干员信息",
    description="查看干员精英化、技能升级、技能专精、模组解锁需要的材料",
    usage=(
        "命令:"
        "\n    干员 [干员名称] => 查看对应干员的精英化、技能升级、技能专精、模组解锁需要的材料"
    ),
    extra={
        "name": "operator_info",
        "author": "NumberSir<number_sir@126.com>",
        "version": "0.1.0"
    }
)
