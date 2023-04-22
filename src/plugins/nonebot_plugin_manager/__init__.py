from argparse import Namespace

from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.message import run_preprocessor
from nonebot.exception import IgnoredException
from nonebot.plugin import on_shell_command, get_loaded_plugins
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent, GroupMessageEvent

from .handle import Handle
from .parser import npm_parser
from .manager import plugin_manager

npm = on_shell_command("npm", parser=npm_parser, priority=1)

# 在 Matcher 运行前检测其是否启用
@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event):
    plugin = matcher.plugin_name

    conv = {
        "user": [event.user_id] if hasattr(event, "user_id") else [],  # type: ignore
        "group": [event.group_id] if hasattr(event, "group_id") else [],  # type: ignore
    }

    if (
        hasattr(event, "user_id")
        and not hasattr(event, "group_id")
        and str(event.user_id) in bot.config.superusers  # type: ignore
    ):
        conv["user"] = []
        conv["group"] = []

    plugin_manager.update_plugin(
        {
            str(p.name): p.name != "nonebot_plugin_manager" and bool(p.matcher)
            for p in get_loaded_plugins()
        }
    )

    if plugin and not plugin_manager.get_plugin(conv=conv, perm=1)[plugin]:
        raise IgnoredException(f"Nonebot Plugin Manager has blocked {plugin} !")


@npm.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    args.conv = {
        "user": [event.user_id],
        "group": [event.group_id] if isinstance(event, GroupMessageEvent) else [],
    }
    args.is_admin = (
        event.sender.role in ["admin", "owner"]
        if isinstance(event, GroupMessageEvent)
        else False
    )
    args.is_superuser = str(event.user_id) in bot.config.superusers

    if hasattr(args, "handle"):
        message = getattr(Handle, args.handle)(args)
        if message is not None:
            message = message.split("\n")
            if len(message) > 15:
                i = 1
                messages = []
                while len(message) > 15:
                    messages.append("\n".join(message[:15]) + f"\n【第{i}页】")
                    message = message[15:]
                    i = i + 1
                messages.append("\n".join(message[:15]) + f"\n【第{i}页-完】")
                if isinstance(event, GroupMessageEvent):
                    await bot.send_group_forward_msg(
                        group_id=event.group_id,
                        messages=[
                            {
                                "type": "node",
                                "data": {
                                    "name": "NBPM",
                                    "uin": bot.self_id,
                                    "content": msg,
                                },
                            }
                            for msg in messages
                        ],
                    )
                else:
                    await bot.send_private_forward_msg(
                        user_id=event.user_id,
                        messages=[
                            {
                                "type": "node",
                                "data": {
                                    "name": "NBPM",
                                    "uin": bot.self_id,
                                    "content": msg,
                                },
                            }
                            for msg in messages
                        ],
                    )
            else:
                await bot.send(event, "\n".join(message[:30]))
