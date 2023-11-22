from arclet.alconna import Args, Option, Alconna, Subcommand
from nonebot.exception import FinishedException
from nonebot_plugin_alconna import on_alconna, AlcResult
from nonebot_plugin_saa_cx import MessageFactory, Text, Image
from nonebot_plugin_spark_gpt.const import menus

from ..chatbots import chatbots
from ..type_store import common_config
from ..type_store import prompt_config, command_config, public_user
from ..utils import Command_Start
from ..utils import is_valid_name
from ..utils.extractor import A_User
chat = on_alconna(
    Alconna(
        f"{Command_Start}chat",
        Subcommand("help"),
        Subcommand(
            "list",
            Option("-help"),
        ),
        Subcommand(
            "add",
            Option("-n", Args["chat_name", str]),
            Option("-m", Args["model", str]),
            Option("-p", Args["prompt", str]),
            Option("-c", Args["command", str]),
            Option("-auto_pic", Args["auto_pic", bool]),
            Option("-num_limit", Args["num_limit", int]),
            Option("-pic", Args["pic", bool]),
            Option("-url", Args["url", bool]),
            Option("-stream", Args["stream", bool]),
            Option("-public"),
            Option("-help"),
        ),
        Subcommand(
            "edit",
            Option("-on", Args["old_name", str]),
            Option("-nn", Args["new_name", str]),
            Option("-m", Args["model", str]),
            Option("-p", Args["prompt", str]),
            Option("-c", Args["command", str]),
            Option("-auto_pic", Args["auto_pic", bool]),
            Option("-num_limit", Args["num_limit", int]),
            Option("-pic", Args["pic", bool]),
            Option("-url", Args["url", bool]),
            Option("-stream", Args["stream", bool]),
            Option("-public"),
            Option("-help"),
        ),
        Subcommand(
            "del",
            Option("-n", Args["chat_name", str]),
            Option("-public"),
            Option("-help"),
        ),
    ),
    aliases={"会话"},
)


@chat.assign("$main")
async def chat_():
    await MessageFactory(Text(menus.get_menu_string("chat"))).finish()


@chat.assign("help")
async def chat_help():
    await MessageFactory(Image(await menus.get_menu_image("chat"))).finish()


@chat.assign("list")
async def chat_list(
    user: A_User,
    arp: AlcResult,
):
    if arp.result.find("list.help"):
        await MessageFactory(Text(menus.get_func_string("chat.list"))).finish()
    await MessageFactory(Image(await user.get_bots_img())).finish(reply=True)


@chat.assign("add")
async def chat_add(arp: AlcResult, user: A_User):
    if arp.result.find("add.help"):
        await MessageFactory(Text(menus.get_func_string("chat.add"))).finish()

    create_params = arp.result.all_matched_args
    name = create_params.get("chat_name", None)
    model = create_params.get("model", "")

    prompt = create_params.get("prompt", "")
    command = create_params.get("command", "")
    auto_pic = create_params.get("auto_pic", True)
    num_limit = create_params.get("num_limit", 500)
    pic = create_params.get("pic", False)
    url = create_params.get("url", True)
    stream = create_params.get("stream", False)
    public = arp.result.find("add.public")

    if not (name or model):
        result = "命令有误:\n格式:chat add -n {chat_name} -m {model} (-p {prompt} -c {command} -auto_pic {bool} -num_limit {int} -pic {bool} -url {bool} -stream {bool} -public)\n错误如下:\n "
        if not name:
            result += "参数 name 未填写\n"
        if not model:
            result += "参数 model 未填写\n"
        result += "\n如有疑问,请使用'chat help'查看图片版详细说明"
        await MessageFactory(Text(result)).finish(reply=True)
    else:
        try:
            is_valid_name(name)

            if public:
                if user.user_id in common_config().superusers:
                    user = public_user
                else:
                    await MessageFactory(Text("你无权管理公有对话")).finish(reply=True)
            if prompt.startswith("."):
                prompt_name = prompt[1:]
                prompt = prompt_config()[prompt_name]
            elif prompt:
                prompt_name = "自定义预设"
            else:
                prompt_name = "无"

            if command.startswith("."):
                command_name = command[1:]
                command = command_config()[command_name]
            elif command:
                command_name = "自定义指令"
            else:
                command_name = "无"

            class_ = chatbots.get_model_class(model)

            user.bots[name] = class_(
                name=name,
                prompt_name=prompt_name,
                prompt=prompt,
                command_name=command_name,
                command=command,
                owner_id=user.user_id,
                stream=stream,
                pic=pic,
                url=url,
                auto_pic=auto_pic,
                num_limit=num_limit,
            )
            user.save()

            await MessageFactory(Text(f"成功添加{'公有' if public else '私有'}会话.")).finish(
                reply=True
            )
        except FinishedException:
            ...
        except Exception as e:
            await MessageFactory(Text(f"添加失败: {e}")).finish(reply=True)


@chat.assign("edit")
async def chat_edit(arp: AlcResult, user: A_User):
    if arp.result.find("edit.help"):
        await MessageFactory(Text(menus.get_func_string("chat.edit"))).finish()

    edit_params = arp.result.all_matched_args

    old_name = edit_params.get("old_name", None)
    new_name = edit_params.get("new_name", old_name)
    public = arp.result.find("edit.public")

    if public:
        if user.user_id in common_config().superusers:
            user = public_user
        else:
            await MessageFactory(Text("你无权管理公有对话")).finish(reply=True)

    if old_name not in user.bots.keys():
        await MessageFactory(Text("原会话不存在.")).finish(reply=True)
    else:
        origin_params = user.bots[old_name].dict()

    prompt = edit_params.get("prompt")
    command = edit_params.get("command")
    prompt_name = origin_params.get("prompt_name")
    if prompt and prompt.startswith("."):
        prompt_name = prompt[1:]
        prompt = prompt_config()[prompt_name]
    elif prompt:
        prompt_name = "自定义预设"
    else:
        prompt = origin_params.get("prompt", "")

    command_name = origin_params.get("command_name")
    if command and command.startswith("."):
        command_name = command[1:]
        command = command_config()[command_name]
    elif command:
        command_name = "自定义指令"
    else:
        command = origin_params.get("command", "")

    model = edit_params.get("model", origin_params.get("model"))

    chatbot_params = {
        "name": new_name,
        "owner_id": origin_params.get("owner_id"),
        "prompt": prompt,
        "prompt_name": prompt_name,
        "command": command,
        "command_name": command_name,
        "auto_pic": edit_params.get("auto_pic", origin_params.get("auto_pic", True)),
        "num_limit": edit_params.get("num_limit", origin_params.get("num_limit", 500)),
        "pic": edit_params.get("pic", origin_params.get("pic", False)),
        "url": edit_params.get("url", origin_params.get("url", True)),
        "stream": edit_params.get("stream", origin_params.get("url", False)),
    }

    if not old_name:
        result = "命令有误:\n格式:chat edit -on {old_name} (-nn {new_name} -m {model} -p {prompt} -c {command} -auto_pic {bool} -num_limit {int} -pic {bool} -url {bool} -stream {bool} -public)\n错误如下:\n参数 old_name 未填写\n\n如有疑问,请使用'chat help'查看图片版详细说明"
        await MessageFactory(Text(result)).finish(reply=True)
    else:
        try:
            is_valid_name(new_name)

            if old_name not in user.bots:
                await MessageFactory(Text("原会话不存在")).finish(reply=True)

            class_ = chatbots.get_model_class(model)

            del user.bots[old_name]

            user.bots[new_name] = class_(**chatbot_params)

            user.save()

            await MessageFactory(Text(f"修改{'公有' if public else '私有'}会话成功.")).finish(
                reply=True
            )

        except FinishedException:
            ...
        except Exception as e:
            await MessageFactory(Text(f"修改{'公有' if public else '私有'}会话失败: {e}")).finish(
                reply=True
            )


@chat.assign("del")
async def chat_del(arp: AlcResult, user: A_User):
    if arp.result.find("del.help"):
        await MessageFactory(Text(menus.get_func_string("chat.del"))).finish()
    del_params = arp.result.all_matched_args
    name = del_params.get("chat_name")
    public = arp.result.find("del.public")
    if not name:
        result = "命令有误:\n格式:chat del -n {chat_name} (-public)\n错误如下:\n参数 name 未填写\n\n如有疑问,请使用'chat help'查看图片版详细说明"
        await MessageFactory(Text(result)).finish(reply=True)
    if public:
        if user.user_id in common_config().superusers:
            user = public_user
        else:
            await MessageFactory(Text("你无权管理公有对话")).finish(reply=True)

    try:
        if name in user.bots.keys():
            del user.bots[name]
            user.save()
            await MessageFactory(
                Text(f"删除{'公有' if public else '私有'}会话 {name} 成功")
            ).finish(reply=True)
        else:
            await MessageFactory(
                Text(f"{'公有' if public else '私有'}会话 {name} 不存在")
            ).finish(reply=True)
    except FinishedException:
        ...
    except Exception as e:
        await MessageFactory(Text(f"删除{'公有' if public else '私有'}会话失败: {e}")).finish(
            reply=True
        )
