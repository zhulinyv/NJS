from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg, _command_arg, _command_start
from nonebot.rule import to_me
from nonebot.typing import T_State

from .chatgpt import Chatbot
from .config import config
from .utils import Session, cooldow_checker, create_matcher, single_run_locker, lockers
from .data import setting

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

if config.chatgpt_image:
    require("nonebot_plugin_htmlrender")

    from nonebot_plugin_htmlrender import md_to_pic


__zx_plugin_name__ = "ChatGPT-PLUS"
__plugin_meta__ = PluginMetadata(
    name="ChatGPT-PLUS",
    description="ChatGPT PLUS插件",
    usage=f"""触发方式：{'@bot ' if config.chatgpt_to_me else ''}{config.chatgpt_command} 触发
刷新会话/刷新对话	重置会话记录，开始新的对话
导出会话/导出对话	导出当前会话记录
导入会话/导入对话 + 会话ID + 父消息ID(可选)	将会话记录导入，这会替换当前的会话
保存会话/保存对话 + 会话名称	将当前会话保存
查看会话/查看对话	查看已保存的所有会话
切换会话/切换对话 + 会话名称	切换到指定的会话
回滚会话/回滚对话	返回到之前的会话，输入数字可以返回多个会话，但不可以超过最大支持数量
人格设定/设置人格 + 名称 使用人格预设
查看人格/查询人格   查看已有的人格预设列表
清空会话/清空对话   清空所有会话（超级用户）
查看人格/查询人格 + 名称   查看已有的人格预设（超级用户）
人格设定/设置人格 + 名称 + 人格信息 编辑人格信息（超级用户）
刷新token   强制刷新token（超级用户）""",
    extra={
        "unique_name": "chatgpt-plus",
        "example": """@bot 人格设定 香草""",
        "author": "A-kirami",
        "version": "0.8.6",
    },
)
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": [
        "ChatGPT4.0",
        "ChatGPT-PLUS",
        "gpt3",
        "gpt4",
    ],
}

chat_bot = Chatbot(
    token=setting.token or config.chatgpt_session_token,
    access_token=setting.access_token or config.chatgpt_access_token,
    model=config.chatgpt_model,
    account=config.chatgpt_account,
    password=config.chatgpt_password,
    api=config.chatgpt_api,
    proxies=config.chatgpt_proxies,
    presets=setting.presets,
    timeout=config.chatgpt_timeout,
)

matcher = create_matcher(
    config.chatgpt_command,
    config.chatgpt_to_me,
    config.chatgpt_private,
    config.chatgpt_priority,
    config.chatgpt_block,
)

session = Session(config.chatgpt_scope)


def check_purview(event: MessageEvent) -> bool:
    return not (
        isinstance(event, GroupMessageEvent)
        and config.chatgpt_scope == "public"
        and event.sender.role == "member"
    )


@matcher.handle(parameterless=[cooldow_checker(config.chatgpt_cd_time), single_run_locker()])
async def ai_chat(event: MessageEvent, state: T_State) -> None:
    lockers[event.user_id] = True
    message = _command_arg(state) or event.get_message()
    text = message.extract_plain_text().strip()
    if start := _command_start(state):
        text = text[len(start) :]
    has_title = True
    played_name = config.chatgpt_default_preset
    if not chat_bot.presets.get(played_name):
        played_name = ""
    cvst = session[event]
    if cvst:
        if not cvst['conversation_id'][-1]:
            has_title = False
    else:
        has_title = False
    if not has_title:
        for name in chat_bot.presets.keys():
            if text.find(name) > -1:
                played_name = name
    try:
        if config.chatgpt_notice:
            msg = "收到请求，等待响应..."
            if not has_title:
                msg += f"\n首次请求，人格设定: {played_name if played_name else '无'}"
            await matcher.send(msg, reply_message=True)
        msg = await chat_bot(**cvst, played_name=played_name).get_chat_response(text)
        if (
            msg == "token失效，请重新设置token"
            and chat_bot.session_token != config.chatgpt_session_token
        ):
            chat_bot.session_token = config.chatgpt_session_token
            msg = await chat_bot(**cvst, played_name=played_name).get_chat_response(text)
        elif (
            msg == "会话不存在"
        ):
            if config.chatgpt_auto_refresh:
                has_title = False
                cvst['conversation_id'].append(None)
                cvst['parent_id'].append(chat_bot.id)
                await matcher.send("会话不存在，已自动刷新对话，等待响应...", reply_message=True)
                msg = await chat_bot(**cvst, played_name=played_name).get_chat_response(text)
            else:
                msg += ",请刷新会话"
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        logger.opt(exception=e).error(f"ChatGPT request failed: {error}")
        await matcher.finish(
            f"请求 ChatGPT 服务器时出现问题，请稍后再试\n错误信息: {error}", reply_message=True
        )
    finally:
        lockers[event.user_id] = False
    if config.chatgpt_image:
        if msg.count("```") % 2 != 0:
            msg += "\n```"
        img = await md_to_pic(msg, width=config.chatgpt_image_width)
        msg = MessageSegment.image(img)
    await matcher.send(msg, reply_message=True)
    session[event] = chat_bot.conversation_id, chat_bot.parent_id
    if not has_title:
        await chat_bot(**session[event]).edit_title(session.id(event=event))
        session.save_sessions()


refresh = on_command("刷新对话", aliases={"刷新会话"}, block=True, rule=to_me(), priority=1)


@refresh.handle()
async def refresh_conversation(event: MessageEvent) -> None:
    if not check_purview(event):
        await import_.finish("当前为公共会话模式, 仅支持群管理操作")
    session[event]['conversation_id'].append(None)
    session[event]['parent_id'].append(chat_bot.id)
    await refresh.send("当前会话已刷新")


export = on_command("导出对话", aliases={"导出会话"}, block=True, rule=to_me(), priority=1)


@export.handle()
async def export_conversation(event: MessageEvent) -> None:
    if cvst := session[event]:
        await export.send(
            f"已成功导出会话:\n"
            f"会话ID: {cvst['conversation_id'][-1]}\n"
            f"父消息ID: {cvst['parent_id'][-1]}",
            reply_message=True,
        )
    else:
        await export.finish("你还没有任何会话记录", reply_message=True)


import_ = on_command(
    "导入对话", aliases={"导入会话", "加载对话", "加载会话"}, block=True, rule=to_me(), priority=1
)


@import_.handle()
async def import_conversation(event: MessageEvent, arg: Message = CommandArg()) -> None:
    if not check_purview(event):
        await import_.finish("当前为公共会话模式, 仅支持群管理操作")
    args = arg.extract_plain_text().strip().split()
    if not args:
        await import_.finish("至少需要提供会话ID", reply_message=True)
    if len(args) > 2:
        await import_.finish("提供的参数格式不正确", reply_message=True)
    session[event] = args.pop(0), args[0] if args else None
    await import_.send("已成功导入会话", reply_message=True)


save = on_command("保存对话", aliases={"保存会话"}, block=True, rule=to_me(), priority=1)


@save.handle()
async def save_conversation(event: MessageEvent, arg: Message = CommandArg()) -> None:
    if not check_purview(event):
        await save.finish("当前为公共会话模式, 仅支持群管理操作")
    if session[event]:
        name = arg.extract_plain_text().strip()
        if not name:
            session.save_sessions()
            await save.finish("已保存所有会话记录", reply_message=True)
        else:
            session.save(name, event)
            await save.send(f"已将当前会话保存为: {name}", reply_message=True)
    else:
        await save.finish("你还没有任何会话记录", reply_message=True)


check = on_command("查看对话", aliases={"查看会话"}, block=True, rule=to_me(), priority=1)


@check.handle()
async def check_conversation(event: MessageEvent) -> None:
    name_list = "\n".join(list(session.find(event).keys()))
    await check.send(f"已保存的会话有:\n{name_list}", reply_message=True)


switch = on_command("切换对话", aliases={"切换会话"}, block=True, rule=to_me(), priority=1)


@switch.handle()
async def switch_conversation(event: MessageEvent, arg: Message = CommandArg()) -> None:
    if not check_purview(event):
        await switch.finish("当前为公共会话模式, 仅支持群管理操作")
    name = arg.extract_plain_text().strip()
    if not name:
        await save.finish("请输入会话名称", reply_message=True)
    try:
        session[event] = session.find(event)[name]
        await switch.send(f"已切换到会话: {name}", reply_message=True)
    except KeyError:
        await switch.send(f"找不到会话: {name}", reply_message=True)

refresh = on_command("刷新token", block=True, rule=to_me(), permission=SUPERUSER, priority=1)


@refresh.handle()
@scheduler.scheduled_job("interval", minutes=config.chatgpt_refresh_interval)
async def refresh_session() -> None:
    if chat_bot.session_token:
        await chat_bot.refresh_session()
    setting.token = chat_bot.session_token
    setting.access_token = chat_bot.authorization
    setting.save()
    session.save_sessions()
    logger.opt(colors=True).debug(
        f"\ntoken: {setting.token}"
    )

clear = on_command("清空对话", aliases={"清空会话"}, block=True, rule=to_me(), permission=SUPERUSER, priority=1)


@clear.handle()
async def clear_session() -> None:
    session.clear()
    session.save_sessions()
    await clear.finish('已清除所有会话...', reply_message=True)

rollback = on_command("回滚对话", aliases={"回滚会话"}, block=True, rule=to_me(), priority=1)


@rollback.handle()
async def rollback_conversation(event: MessageEvent, arg: Message = CommandArg()):
    num = arg.extract_plain_text().strip()
    if num.isdigit():
        num = int(num)
        if session[event]:
            count = session.count(event)
            if num > count:
                await rollback.finish(f"历史会话数不足，当前历史会话数为{count}", reply_message=True)
            else:
                for _ in range(num):
                    session.pop(event)
                await rollback.send(f"已成功回滚{num}条会话", reply_message=True)
        else:
            await save.finish("你还没有任何会话记录", reply_message=True)
    else:
        await rollback.finish(
            f"请输入有效的数字，最大回滚数为{config.chatgpt_max_rollback}", reply_message=True
        )

set_preset = on_command("人格设定", aliases={"设置人格"}, block=True, rule=to_me(), priority=1)


@set_preset.handle()
async def set_preset_(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip().split()
    if not args:
        await set_preset.finish("至少需要提供人格名称", reply_message=True)
    if len(args) >= 2:
        if event.get_user_id() not in bot.config.superusers:
            await set_preset.finish("权限不足", reply_message=True)
        else:
            setting.presets[args[0]] = '\n'.join(args[1:])
            await set_preset.finish("人格设定修改成功: " + args[0], reply_message=True)
    else:
        if session[event]:
            if session[event]['conversation_id'][-1]:
                await set_preset.finish("已存在会话，请刷新会话后设定。", reply_message=True)
        try:
            msg = await chat_bot(**session[event], played_name=args[0]).get_chat_response(args[0])
            session[event] = chat_bot.conversation_id, chat_bot.parent_id
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
            logger.opt(exception=e).error(f"ChatGPT request failed: {error}")
            await set_preset.finish(
                f"请求 ChatGPT 服务器时出现问题，请稍后再试\n错误信息: {error}", reply_message=True
            )
        await set_preset.send(msg, reply_message=True)
        await chat_bot(**session[event]).edit_title(session.id(event=event))

query = on_command("查看人格", aliases={"查询人格"}, block=True, rule=to_me(), priority=1)


@query.handle()
async def query_preset(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    preset = arg.extract_plain_text().strip()
    if not preset:
        msg = "人格如下：\n"
        msg += "、".join(setting.presets.keys())
        await query.finish(msg, reply_message=True)
    if setting.presets.get(preset):
        if event.get_user_id() not in bot.config.superusers:
            await query.finish("权限不足", reply_message=True)
        await query.finish(f"名称：{preset}\n人格设定：{setting.presets.get(preset)}", reply_message=True)
    else:
        await query.finish("人格设定不存在", reply_message=True)