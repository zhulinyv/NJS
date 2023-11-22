import asyncio
from asyncio import ensure_future

from arclet.alconna import Alconna, Subcommand, Option, Args
from nonebot.exception import FinishedException
from nonebot_plugin_alconna import on_alconna, AlconnaMatch, Match, AlcResult
from nonebot_plugin_saa_cx import MessageFactory, Image, Text

from ..const import menus
from ..type_store import command_config, common_config
from ..utils import Command_Start
from ..utils import get_url
from ..utils.extractor import A_User
command = on_alconna(
    Alconna(f"{Command_Start}command",
            Subcommand("help"),
            Subcommand(
                "add", Option("-n", Args["name", str]), Option("-c", Args["content", str])
            ),  # noqa: E501
            Subcommand("del", Option("-n", Args["name", str])),
            Subcommand("list", Option("-p", Args["page", int])),
            Subcommand("show", Option("-n", Args["name", str])),
            ),
    aliases={"指令"},
)


@command.assign("$main")
async def command_main():
    await MessageFactory(Text(menus.get_menu_string("command"))).finish()


@command.assign("help")
async def command_help():
    await MessageFactory(Image(await menus.get_menu_image("command"))).finish()


@command.assign("add")
async def command_add(arp: AlcResult, user: A_User):
    if user.user_id not in common_config().superusers:
        await MessageFactory(Text("无权管理指令")).finish(reply=True)
    command_params = {"name": "", "content": ""}
    command_params.update(arp.result.all_matched_args)
    result = "命令有误:\n格式:command add -n {name} -c {content}\n错误如下: "
    for key, value in command_params.items():
        if not value:
            result += f"\n参数{key}未填写"

    if not (command_params["name"] and command_params["content"]):
        result += "\n\n如有疑问,请使用'command help'查看图片版详细说明"
        await MessageFactory(Text(result)).finish(reply=True)
    else:
        command_ = command_config()
        try:
            command_.data_dict[command_params["name"]] = command_params["content"]
            command_.save()
        except FinishedException:
            ...
        except Exception as e:
            await MessageFactory(Text(f"添加失败: {e}")).finish(reply=True)
        await MessageFactory(Text(f"成功添加新指令: {command_params['name']}")).finish(
            reply=True
        )


@command.assign("del")
async def command_del(user: A_User, name: Match[str] = AlconnaMatch("name")):
    if user.user_id not in common_config().superusers:
        await MessageFactory(Text("无权管理指令")).finish(reply=True)
    command_ = command_config()
    if name.available:
        if name.result in command_.data_dict.keys():
            del command_.data_dict[name.result]
            command_.save()
            await MessageFactory(Text(f"成功删除了指令: {name.result}")).finish(reply=True)
        else:
            await MessageFactory(
                Text("不存在该名称的指令,请先使用 'command list -p {num}'查询可用指令列表")
            ).finish(reply=True)
    else:
        await MessageFactory(
            Text(
                "命令有误:\n格式:command del -n {name}\n错误如下:参数name未填写,请补全后重新发送\n如有疑问,请使用'command help'查看图片版详细说明"
            )
        ).finish(reply=True)


@command.assign("list")
async def command_list_(page: Match[int] = AlconnaMatch("page")):
    if page.available:
        page = page.result - 1
    else:
        page = 0
    images = await command_config().get_images()
    await MessageFactory(Image(images[page])).finish()


@command.assign("show")
async def command_show(name: Match[str] = AlconnaMatch("name")):
    command_ = command_config()
    if name.available:
        if name.result in command_.data_dict.keys():
            image_bytes = ensure_future(command_.get_image(name.result))
            url = ensure_future(get_url(command_.data_dict.get(name.result)))
            await asyncio.gather(image_bytes, url)
            await MessageFactory(
                Image(image_bytes.result()) + Text(url.result())
            ).finish(
                reply=True
            )  # noqa: E501
        else:
            await MessageFactory(
                Text("不存在该名称的指令,请先使用 'command list -p {num}'查询可用指令列表")
            ).finish(reply=True)
    else:
        await MessageFactory(
            Text(
                "命令有误:\n格式:command show -n {name}\n错误如下:参数name未填写,请补全后重新发送\n如有疑问,请使用'command help'查看图片版详细说明"
            )
        ).finish(reply=True)
