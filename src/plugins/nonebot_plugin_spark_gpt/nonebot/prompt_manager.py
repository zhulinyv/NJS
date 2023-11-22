import asyncio
from asyncio import ensure_future

from arclet.alconna import Alconna, Subcommand, Option, Args
from nonebot.exception import FinishedException
from nonebot_plugin_alconna import on_alconna, AlconnaMatch, Match, AlcResult
from nonebot_plugin_saa_cx import MessageFactory, Image, Text

from ..const import menus
from ..type_store import prompt_config, common_config
from ..utils import Command_Start
from ..utils import get_url
from ..utils.extractor import A_User
prompt = on_alconna(
    Alconna(
        f"{Command_Start}prompt",
        Subcommand("help"),
        Subcommand("add", Option("-n", Args["name", str]), Option("-c", Args["content", str])),
        Subcommand("del", Option("-n", Args["name", str])),
        Subcommand("list", Option("-p", Args['page', int])),
        Subcommand("show", Option("-n", Args["name", str]))
    ),
    aliases={"预设"},
)


@prompt.assign("$main")
async def prompt_main():
    await MessageFactory(Text(menus.get_menu_string("prompt"))).finish()


@prompt.assign("help")
async def prompt_help():
    await MessageFactory(Image(await menus.get_menu_image("prompt"))).finish()


@prompt.assign("add")
async def prompt_add(arp: AlcResult, user: A_User):
    if user.user_id not in common_config().superusers:
        await MessageFactory(Text("无权管理预设")).finish(reply=True)
    prompt_params = {"name": "", "content": ""}
    prompt_params.update(arp.result.all_matched_args)
    result = "命令有误:\n格式:prompt add -n {name} -c {content}\n错误如下: "
    for key, value in prompt_params.items():
        if not value:
            result += f"\n参数{key}未填写"

    if not (prompt_params['name'] and prompt_params['content']):
        result += "\n\n如有疑问,请使用'prompt help'查看图片版详细说明"
        await MessageFactory(Text(result)).finish(reply=True)
    else:
        prompt_ = prompt_config()
        try:
            prompt_.data_dict[prompt_params["name"]] = prompt_params["content"]
            prompt_.save()
        except FinishedException:
            ...
        except Exception as e:
            await MessageFactory(Text(f"添加失败: {e}")).finish(reply=True)
        await MessageFactory(Text(f"成功添加新预设: {prompt_params['name']}")).finish(reply=True)


@prompt.assign("del")
async def prompt_del(user: A_User, name: Match[str] = AlconnaMatch("name")):
    if user.user_id not in common_config().superusers:
        await MessageFactory(Text("无权管理预设")).finish(reply=True)
    prompt_ = prompt_config()
    if name.available:
        if name.result in prompt_.data_dict.keys():
            del prompt_.data_dict[name.result]
            prompt_.save()
            await MessageFactory(Text(f"成功删除了预设: {name.result}")).finish(reply=True)
        else:
            await MessageFactory(Text("不存在该名称的预设,请先使用 'prompt list -p {num}'查询可用预设列表")).finish(
                reply=True)
    else:
        await MessageFactory(
            Text(
                "命令有误:\n格式:prompt del -n {name}\n错误如下:参数name未填写,请补全后重新发送\n如有疑问,请使用'prompt help'查看图片版详细说明")).finish(
            reply=True)


@prompt.assign("list")
async def prompt_list_(page: Match[int] = AlconnaMatch('page')):
    if page.available:
        page = page.result - 1
    else:
        page = 0
    images = await prompt_config().get_images()
    await MessageFactory(Image(images[page])).finish()


@prompt.assign("show")
async def prompt_show(name: Match[str] = AlconnaMatch("name")):
    prompt_ = prompt_config()
    if name.available:
        if name.result in prompt_.data_dict.keys():
            image_bytes = ensure_future(prompt_.get_image(name.result))
            url = ensure_future(get_url(prompt_.data_dict.get(name.result)))
            await asyncio.gather(image_bytes, url)
            await MessageFactory(Image(image_bytes.result()) + Text(url.result())).finish(reply=True)  # noqa: E501
        else:
            await MessageFactory(Text("不存在该名称的预设,请先使用 'prompt list -p {num}'查询可用预设列表")).finish(
                reply=True)
    else:
        await MessageFactory(
            Text(
                "命令有误:\n格式:prompt show -n {name}\n错误如下:参数name未填写,请补全后重新发送\n如有疑问,请使用'prompt help'查看图片版详细说明")).finish(
            reply=True)
