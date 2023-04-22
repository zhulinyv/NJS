"""猜干员，改自 wordle"""
from nonebot import on_shell_command, on_command, on_message
from nonebot.plugin import PluginMetadata
from nonebot.params import ShellCommandArgv, CommandArg, EventPlainText
from nonebot.exception import ParserExit
from nonebot.rule import Rule, ArgumentParser, to_me
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment

import asyncio
import shlex
from typing import List, Dict, Optional
from io import BytesIO
from dataclasses import dataclass
from asyncio import TimerHandle


from .data_source import *
from ..core.models_v3 import Character


GAMES: Dict[str, GuessCharacter] = {}  # 记录游戏数据
TIMERS: Dict[str, TimerHandle] = {}  # 计时


@dataclass
class Options:
    hint: bool = False
    stop: bool = False
    cht_name: str = None


parser = ArgumentParser("arkguess", description="猜干员")
parser.add_argument("--hint", action="store_true", help="提示")
parser.add_argument("--stop", action="store_true", help="结束游戏")
parser.add_argument("cht_name", nargs="?", help="干员名")


arkguess = on_shell_command("猜干员", parser=parser)
@arkguess.handle()
async def _(matcher: Matcher, event: GroupMessageEvent, argv: List[str] = ShellCommandArgv()):
    """开始游戏"""
    await handle_arkguess(matcher, event, argv)


async def handle_arkguess(matcher: Matcher, event: GroupMessageEvent, argv: List[str]):
    async def send(message: Optional[str] = None, image: Optional[BytesIO] = None):
        if not (message or image):
            await matcher.finish()
        msg_ = Message()
        if image:
            msg_.append(MessageSegment.image(image))
        if message:
            msg_.append(message)
        await matcher.finish(msg_)

    try:
        args = parser.parse_args(argv)
    except ParserExit as e:
        if e.status == 0:
            await send("小笨蛋，命令输错了哦！")
        await send()

    options = Options(**vars(args))
    cid = f"group_{event.group_id}"
    if not GAMES.get(cid):
        if options.cht_name or options.stop or options.hint:
            await matcher.finish("小笨蛋，没有正在进行的游戏哦！")

        character = await get_random_character()
        game = GuessCharacter(cht=character)
        GAMES[cid] = game
        set_timeout(matcher, cid)

        await send(f"你有{game.times}次机会猜出干员，请发送“#干员名”猜干员，如“#艾雅法拉”", await game.draw())

    # 手动结束游戏
    if options.stop:
        game = GAMES.pop(cid)
        msg = "游戏已结束"
        if game.guessed:
            msg += f"\n{await game.get_result()}"
        await send(msg)

    game = GAMES[cid]
    set_timeout(matcher, cid)

    # 提示
    if options.hint:
        await send(message=await game.get_hint())

    cht = await Character.parse_name(options.cht_name)
    result = await game.guess(cht)
    if result in [GuessResult.WIN, GuessResult.LOSE]:
        GAMES.pop(cid)
        await send(
            (
                "恭喜你猜出了干员！"
                if result == GuessResult.WIN
                else "很遗憾，没有人猜出来呢"
            ) + f"\n{await game.get_result()}",
            await game.draw()
        )

    elif result == GuessResult.DUPLICATE:
        await send("小笨蛋，已经猜过这个干员了哦")
    elif result == GuessResult.ILLEGAL:
        await send(f"你确定 {cht.name} 是咱干员吗？")
    else:
        await send(image=await game.draw())


def set_timeout(matcher: Matcher, cid: str, timeout: float = 300):
    """设置游戏超时，默认5分钟"""
    timer = TIMERS.get(cid)
    if timer:
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game(matcher, cid))
    )
    TIMERS[cid] = timer


async def stop_game(matcher: Matcher, cid: str):
    """超时自动停止"""
    TIMERS.pop(cid)
    if GAMES.get(cid):
        game = GAMES.pop(cid)
        msg = "猜干员超时，游戏结束"
        if game.guessed:
            msg += f"\n{await game.get_result()}"
        await matcher.finish(msg)


def shortcut(cmd: str, argv: List[str] = None, **kwargs):
    if not argv:
        argv = []
    command = on_command(cmd, **kwargs)

    @command.handle()
    async def _(matcher: Matcher, event: GroupMessageEvent, msg: Message = CommandArg()):
        try:
            args = shlex.split(msg.extract_plain_text().strip())
        except Exception as e:
            args = []
        await handle_arkguess(matcher, event, argv + args)


def is_game_running(event: GroupMessageEvent) -> bool:
    """判断游戏运行"""
    return bool(GAMES.get(f"group_{event.group_id}"))


def get_word_input(state: T_State, msg: str = EventPlainText()) -> bool:
    """获取输入干员"""
    if msg.startswith("#"):
        state["cht_name"] = msg[1:]
        return True
    return False


shortcut("猜干员", [], rule=to_me())
shortcut("提示", ["--hint"], rule=is_game_running)
shortcut("结束", ["--stop"], rule=is_game_running)


word_matcher = on_message(Rule(is_game_running) & get_word_input)
@word_matcher.handle()
async def _(matcher: Matcher, event: GroupMessageEvent, state: T_State):
    cht_name: str = state["cht_name"]
    await handle_arkguess(matcher, event, [cht_name])


__plugin_meta__ = PluginMetadata(
    name="猜干员",
    description="与wordle玩法相同，猜明日方舟干员",
    usage=(
        "命令:"
        "\n    猜干员 => 开始新游戏"
        "\n    #干员名称(例: #艾雅法拉) => 猜干员"
        "\n    提示 => 查看答案干员的信息"
        "\n    结束 => 结束当前游戏"
    ),
    extra={
        "name": "guess_operator",
        "author": "NumberSir<number_sir@126.com>",
        "version": "0.1.0"
    }
)
