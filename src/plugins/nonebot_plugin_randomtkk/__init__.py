from nonebot import on_command, on_regex
from typing import List
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent, GroupMessageEvent
from nonebot.params import Depends, CommandArg, RegexMatched
from nonebot.rule import Rule
from .config import find_charac
from .handler import random_tkk_handler

__randomtkk_version__ = "v0.1.5a1"
__randomtkk_usages__ = f'''
随机唐可可 {__randomtkk_version__}
[随机唐可可]+[简单/普通/困难/地狱/自定义数量] 开启寻找唐可可挑战
不指定难度则默认普通
答案格式：[答案是][行][空格][列]，例如：答案是114 514
[找不到唐可可] 发起者可提前结束游戏
将[唐可可]替换成其他角色可以寻找她们！'''.strip()

__plugin_meta__ = PluginMetadata(
    name="随机唐可可",
    description="找到唐可可！",
    usage=__randomtkk_usages__,
    extra={
        "author": "KafCoppelia <k740677208@gmail.com>",
        "version": __randomtkk_version__
    }
)

def inplaying_check(event: MessageEvent) -> bool:
    uuid: str = str(event.group_id) if isinstance(event, GroupMessageEvent) else str(event.user_id)  
    return random_tkk_handler.check_tkk_playing(uuid)

def unplaying_check(event: MessageEvent) -> bool:
    uuid: str = str(event.group_id) if isinstance(event, GroupMessageEvent) else str(event.user_id)  
    return not random_tkk_handler.check_tkk_playing(uuid)

def starter_check(event: MessageEvent) -> bool:
    uid: str = str(event.user_id)
    gid = str(event.group_id) if isinstance(event, GroupMessageEvent) else None       
    return random_tkk_handler.check_starter(gid, uid)

def characs_check(event: MessageEvent) -> bool:
    _charac: str = event.get_message().extract_plain_text()[2:]
    return bool(find_charac(_charac))
    
random_tkk = on_regex(pattern="^随机\S{1,8}\s{1}(帮助|简单|普通|困难|地狱|\d{1,2})$", priority=12)
random_tkk_default = on_regex(pattern="^随机\S{1,8}$", rule=Rule(characs_check), priority=12)
guess_tkk = on_command(cmd="答案是", rule=Rule(inplaying_check), priority=12, block=True)
surrender_tkk = on_regex(pattern="^找不到\S{1,8}$", rule=Rule(inplaying_check, starter_check), priority=12, block=True)

@random_tkk.handle()
async def _(matcher: Matcher, event: MessageEvent, matched: str = RegexMatched()):
    uid: str = str(event.user_id)
    gid: str = ""
    level: str = ""
    
    # Check whether the game has started
    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
        if random_tkk_handler.check_tkk_playing(gid):
            await matcher.finish("游戏已经开始啦！", at_sender=True)
    else:
        if random_tkk_handler.check_tkk_playing(uid):
            await matcher.finish("游戏已经开始啦！")
    
    args: List[str] = matched.strip().split()
    _charac: str = args[0][2:]
    if not find_charac(_charac):
        await matcher.finish(f"角色名 {_charac} 不存在，是不是记错名字了？")
        
    if len(args) == 1:
        await matcher.send("未指定难度，默认普通模式")
        level = "普通"
    elif len(args) == 2: 
        if args[1] == "帮助":
            await matcher.finish(__randomtkk_usages__)
        else:
            level = args[1]
    else:
        await matcher.finish("参数太多啦~")
    
    if isinstance(event, GroupMessageEvent):
        img_file, waiting = random_tkk_handler.one_go(matcher, gid, uid, level, _charac)
    else:
        img_file, waiting = random_tkk_handler.one_go(matcher, uid, uid, level, _charac)
    
    await matcher.send(MessageSegment.image(img_file))
    
    # 确保在此为send，超时回调内还需matcher.finish
    await matcher.send(f"将在 {waiting}s 后公布答案\n答案格式：[答案是][行][空格][列]\n例如：答案是114 514\n提前结束游戏请发起者输入[找不到{_charac}]")
    
@random_tkk_default.handle()
async def _(matcher: Matcher, event: MessageEvent, matched: str = RegexMatched()):
    if matched[-2:] == "帮助":
        await matcher.finish(__randomtkk_usages__)
        
    uid: str = str(event.user_id)
    gid: str = ""
    _charac: str = matched[2:]
    
    # Check whether the game has started
    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
        if random_tkk_handler.check_tkk_playing(gid):
            await matcher.finish("游戏已经开始啦！", at_sender=True)
    else:
        if random_tkk_handler.check_tkk_playing(uid):
            await matcher.finish("游戏已经开始啦！")

    await matcher.send("未指定难度，默认普通模式")
    
    if isinstance(event, GroupMessageEvent):
        img_file, waiting = random_tkk_handler.one_go(matcher, gid, uid, "普通", _charac)
    else:
        img_file, waiting = random_tkk_handler.one_go(matcher, uid, uid, "普通", _charac)
    
    await matcher.send(MessageSegment.image(img_file))
    
    # 确保在此为send，超时回调内还需matcher.finish
    await matcher.send(f"将在 {waiting}s 后公布答案\n答案格式：[答案是][行][空格][列]\n例如：答案是114 514\n提前结束游戏请发起者输入[找不到{_charac}]")

async def get_user_guess(args: Message = CommandArg()) -> List[int]:
    arg: List[str] = args.extract_plain_text().strip().split()

    if not arg:
        await guess_tkk.finish("答案是啥捏？")
    elif len(arg) == 1:    
        await guess_tkk.finish("答案格式错误~")
    elif len(arg) == 2:
        arg_list: List[int] = [int(x) for x in arg]
        return arg_list
    else:
        await guess_tkk.finish("参数太多啦~")

@guess_tkk.handle()
async def _(event: MessageEvent, pos: List[int] = Depends(get_user_guess)):
    if isinstance(event, GroupMessageEvent):
        gid: str = str(event.group_id)
        
        if random_tkk_handler.check_answer(gid, pos):
            if not random_tkk_handler.bingo_close_game(gid):
                await guess_tkk.finish("结束游戏出错……")
            
            await guess_tkk.finish("答对啦，好厉害！", at_sender=True)
        else:
            await guess_tkk.finish("不对哦~", at_sender=True)
    else:
        uid: str = str(event.user_id)
        if random_tkk_handler.check_answer(uid, pos):
            if not random_tkk_handler.bingo_close_game(uid):
                await guess_tkk.finish("结束游戏出错……")
            
            await guess_tkk.finish("答对啦，好厉害！")
        else:
            await guess_tkk.finish("不对哦~")
        
@surrender_tkk.handle()
async def _(matcher: Matcher, event: MessageEvent, matched: str = RegexMatched()):
    arg: str = matched[3:]
    
    if isinstance(event, GroupMessageEvent):
        gid: str = str(event.group_id)
        if random_tkk_handler.check_surrender_charac(gid, arg):
            await random_tkk_handler.surrender(matcher, gid)
    else:
        uid: str = str(event.user_id)
        if random_tkk_handler.check_surrender_charac(uid, arg):
            await random_tkk_handler.surrender(matcher, uid)
    
    await matcher.finish(f"{arg} 与寻找的角色不匹配")