from aiohttp import ClientConnectorError
from nonebot.typing import T_State
from nonebot import on_command
from nonebot.params import CommandArg, ArgPlainText
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, Bot, GroupMessageEvent, PrivateMessageEvent, MessageEvent
from .cartoon import GetCartoons, Cartoons, global_config

anime_res = on_command("资源", aliases={"动漫资源"})


@anime_res.handle()
async def _(state: T_State, msg: Message = CommandArg()):
    if text := msg.get("text"):
        state["param"] = text


@anime_res.got("param", prompt="动漫名字叫什么呀！")
async def _(matcher: Matcher, state: T_State, param: str = ArgPlainText()):
    try:
        if res := await GetCartoons(param):
            state["res"] = res
            await matcher.send(f"你要哪种？\n" + '\n'.join(f'{i}:{v}' for i, v in enumerate(res.keys, 1)))
        else:
            await matcher.finish("没有找到你想要的，看看是不是打错了吧！")
    except ClientConnectorError as err:
        await matcher.finish("获取失败" + str(err.args[-1]))


@anime_res.got("index")
async def _(bot: Bot, matcher: Matcher, event: MessageEvent, state: T_State, index: str = ArgPlainText()):
    cartoons: Cartoons = state["res"]
    if animes := cartoons.get((int(index) - 1) if index.isdigit() else index):
        animes = animes[:global_config.cartoon_length]
        if global_config.cartoon_forward:   # 发送合并转发
            forward_msg = await animes.forward_msg(event.self_id)
            if isinstance(event, GroupMessageEvent):  # 群合并转发
                await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=forward_msg)
            elif isinstance(event, PrivateMessageEvent):    # 私聊合并转发
                await bot.call_api("send_private_forward_msg", user_id=event.user_id, messages=forward_msg)
        else:   # 纯消息文本
            await matcher.finish("\n\n".join([await a.to_string() for a in animes]))
    else:
        await matcher.finish("没有找到你要的东西...")


__helper__ = {
    "cmd": "资源",
    "params": "动漫名字",
    "tags": "搜索 动漫 动漫资源",
    "use": "资源 [动漫名字]",
    "doc": "根据一些动漫的关键字进行资源搜索，具体搜索是依靠关键字哦，例如：资源 天气之子，这时候会根据名字就行搜索\n"
           "如果搜索的结果不理想，可以换个方式搜索，例如需要搜索的天气之子资源需要是mkv格式的生肉资源，就可以这样写\n"
           "资源 天气之子 mkv raws\n"
           "将这些关键字以空格的方式分开搜索，可以提高搜索结果的精准度。"
}
