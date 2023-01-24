from nonebot import on_command, logger
from nonebot.adapters import Message
from nonebot.params import Matcher, CommandArg, ArgPlainText

from .calc import calc_molar_mass, CalcException


__all__ = []


molar_mass = on_command('摩尔质量', aliases={'相对分子质量', 'mol'})


@molar_mass.handle()
async def handle_receive_molar_mass(matcher: Matcher, arg: Message = CommandArg()):
    if arg.extract_plain_text():
        matcher.set_arg('chemical', arg)


@molar_mass.got('chemical', prompt='你想计算什么物质？')
async def handle_calculate_molar_mass(chemical: str = ArgPlainText()):
    try:
        await molar_mass.finish(calc_molar_mass(chemical))
    except CalcException:
        logger.error(f'failed to calculate {chemical}')
        await molar_mass.reject('计算出错，请检查输入格式。\n'
                                '输入例：NaOH，H2SO4，2HCl，(NH4)2SO4，CuSO4+5H2O')
