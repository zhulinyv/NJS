"""
* Copyright (c) 2023, Agnes Digital
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from nonebot import require

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")
require("nonebot_plugin_txt2img")
import time
from time import sleep
from typing import List, Tuple, Union

from nonebot import get_driver, require
from nonebot.matcher import Matcher
from nonebot.params import Arg, ArgPlainText, CommandArg, Keyword, RegexGroup
from nonebot.typing import T_State

from .l4d2_anne.server import updata_anne_server
from .l4d2_data import sq_L4D2
from .l4d2_file import all_zip_to_one, updown_l4d2_vpk
from .l4d2_file.input_json import *
from .l4d2_image.steam import url_to_byte, url_to_byte_name
from .l4d2_image.vtfs import img_to_vtf
from .l4d2_push import *
from .l4d2_queries.qqgroup import add_ip, del_ip, get_number_url, show_ip
from .l4d2_queries.utils import queries_server
from .l4d2_utils.command import *
from .l4d2_utils.config import *
from .l4d2_utils.txt_to_img import mode_txt_to_img
from .l4d2_utils.utils import *
from .l4d2_web import web, webUI

scheduler = require("nonebot_plugin_apscheduler").scheduler
from nonebot.plugin import PluginMetadata

driver = get_driver()

__version__ = "0.6.0"
__plugin_meta__ = PluginMetadata(
    name="求生之路小助手",
    description="可用于管理求生之路查服和本地管理",
    usage="群内对有关求生之路的查询和操作",
    type="application",
    homepage="https://github.com/Agnes4m/nonebot_plugin_l4d2_server",
    supported_adapters={"~onebot.v11"},
    extra={
        "version": __version__,
        "author": "Agnes4m <Z735803792@163.com>",
    },
)


"""相当于启动就检查数据库"""


@up.handle()
async def _(matcher: Matcher, event: NoticeEvent):
    args = event.dict()
    if args["notice_type"] != "offline_file":
        matcher.set_arg("txt", args)  # type: ignore
        return
    l4_file_path = l4_config.l4_ipall[l4_config.l4_number]["location"]
    map_path = Path(l4_file_path, vpk_path)  # type: ignore
    # 检查下载路径是否存在
    if not Path(l4_file_path).exists():  # type: ignore
        await matcher.finish("你填写的路径不存在辣")
    if not Path(map_path).exists():
        await matcher.finish("这个路径并不是求生服务器的路径，请再看看罢")
    url: str = args["file"]["url"]
    name: str = args["file"]["name"]
    # 如果不符合格式则忽略
    await up.send("已收到文件，开始下载")
    sleep(1)  # 等待一秒防止因为文件名获取出现BUG
    vpk_files = await updown_l4d2_vpk(map_path, name, url)
    if vpk_files:
        mes = "解压成功，新增以下几个vpk文件"
        await matcher.finish(mes_list(mes, vpk_files))
    else:
        await matcher.finish("你可能上传了相同的文件，或者解压失败了捏")


path_list: str = "请选择上传位置（输入阿拉伯数字)"
times = 0
for one_path in l4_config.l4_ipall:
    times += 1
    path_msg = one_path["location"]
    path_list += f"\n {str(times)} | {path_msg}"


@up.got("is_sure", prompt=path_list)
async def _(matcher: Matcher):
    args = matcher.get_arg("txt")
    l4_file = l4_config.l4_ipall
    if not args:
        await matcher.finish("获取文件出错辣，再试一次吧")

    is_sure = str(matcher.get_arg("is_sure")).strip()
    if not is_sure.isdigit():
        await matcher.finish("已取消上传")

    file_path: str = ""
    for one_server in l4_file:
        if one_server["id_rank"] == is_sure:
            file_path = one_server["location"]
    if not file_path:
        await matcher.finish("没有这个序号拉baka")

    map_path = Path(file_path, vpk_path)

    # 检查下载路径是否存在
    if not Path(file_path).exists():
        await matcher.finish("你填写的路径不存在辣")
    if not map_path.exists():
        await matcher.finish("这个路径并不是求生服务器的路径，请再看看罢")

    url = args["file"]["url"]
    name = args["file"]["name"]
    # 如果不符合格式则忽略
    if not name.endswith(file_format):  # type: ignore
        return

    await matcher.send("已收到文件，开始下载")
    sleep(1)  # 等待一秒防止因为文件名获取出现BUG
    vpk_files = await updown_l4d2_vpk(map_path, name, url)  # type: ignore

    if vpk_files:
        logger.info("检查到新增文件")
        mes = "解压成功，新增以下几个vpk文件"
    elif vpk_files is None:
        await matcher.finish("文件错误")
    else:
        mes = "你可能上传了相同的文件，或者解压失败了捏"

    await matcher.finish(mes_list(mes, vpk_files))


@find_vpk.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    map_path = Path(l4_config.l4_ipall[l4_config.l4_number]["location"], vpk_path)
    name_vpk = get_vpk(map_path)
    logger.info("获取文件列表成功")
    mes = "当前服务器下有以下vpk文件"
    msg = ""
    msg = mes_list(msg, name_vpk).replace(" ", "")

    await matcher.finish(mode_txt_to_img(mes, msg))


@del_vpk.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    num1 = args.extract_plain_text()
    if num1:
        matcher.set_arg("num", args)


@del_vpk.got("num", prompt="你要删除第几个序号的地图(阿拉伯数字)")
async def _(matcher: Matcher, tag: str = ArgPlainText("num")):
    map_path = Path(l4_config.l4_ipall[l4_config.l4_number]["location"], vpk_path)
    vpk_name = del_map(int(tag), map_path)
    await matcher.finish("已删除地图：" + vpk_name)


@rename_vpk.handle()
async def _(
    matcher: Matcher,
    matched: Tuple[int, str, str] = RegexGroup(),
):
    num, useless, rename = matched
    map_path = Path(l4_config.l4_ipall[l4_config.l4_number]["location"], vpk_path)
    logger.info("检查是否名字是.vpk后缀")
    if not rename.endswith(".vpk"):
        rename = rename + ".vpk"
    logger.info("尝试改名")
    try:
        map_name = rename_map(num, rename, map_path)
        if map_name:
            await matcher.finish("改名成功\n原名:" + map_name + "\n新名称:" + rename)
    except ValueError:
        await matcher.finish("参数错误,请输入格式如【求生地图 5 改名 map.vpk】,或者输入【求生地图】获取全部名称")


@anne_player.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    name = args.extract_plain_text()
    name = name.strip()
    at = await get_message_at(event.json())
    usr_id = at_to_usrid(at)
    if not usr_id:
        usr_id = event.user_id
    # 没有参数则从db里找数据
    msg = await search_anne(name, str(usr_id))
    if isinstance(msg, str):
        await matcher.finish(msg)
    elif isinstance(msg, bytes):
        await matcher.finish(MessageSegment.image(msg))


@anne_bind.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    tag = args.extract_plain_text()
    tag = tag.strip()
    if tag == "" or tag.isspace():
        await matcher.finish("虚空绑定?")
    usr_id = str(event.user_id)
    nickname = event.sender.card or event.sender.nickname
    if not nickname:
        nickname = "宁宁"
    msg = await bind_steam(usr_id, tag, nickname)
    await matcher.finish(msg)


@del_bind.handle()
async def _(matcher: Matcher, event: MessageEvent):
    usr_id = event.user_id
    await matcher.finish(name_exist(str(usr_id)))


@rcon_to_server.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("command", args)


@rcon_to_server.got("command", prompt="请输入向服务器发送的指令")
async def _(matcher: Matcher, tag: str = ArgPlainText("command")):
    tag = tag.strip()
    msg = await command_server(tag)
    try:
        await matcher.finish(mode_txt_to_img("服务器返回", msg))
    except:
        await matcher.finish(msg, reply_message=True)


@check_path.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg.startswith("切换"):
        msg_number = int("".join(msg.replace("切换", " ").split()))
        if msg_number > len(l4_config.l4_ipall) or msg_number < 0:
            await matcher.send("没有这个序号的路径呐")
        else:
            l4_config.l4_number = msg_number - 1
            now_path = l4_config.l4_ipall[l4_config.l4_number]["location"]
            await matcher.send(f"已经切换路径为\n{str(l4_config.l4_number+1)}、{now_path}")
            config_manager.save()
    else:
        now_path = l4_config.l4_ipall[l4_config.l4_number]["location"]
        await matcher.send(f"当前的路径为\n{str(l4_config.l4_number+1)}、{now_path}")


@queries_comm.handle()
async def _(matcher: Matcher, event: MessageEvent, keyword: str = Keyword()):
    msg = event.get_plaintext()

    if not msg:
        await matcher.finish("ip格式如中括号内【127.0.0.1】【114.51.49.19:1810】")
    ip = msg.split(keyword)[-1].split("\r")[0].split("\n")[0].split(" ")
    one_msg = None
    for one in ip:
        if one and one[-1].isdigit():
            one_msg = one
            break
    if not one_msg:
        await matcher.finish()
    ip_list = split_maohao(one_msg)
    msg = await queries_server(ip_list)
    await str_to_picstr(msg, matcher, keyword)


@add_queries.handle()
async def _(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if len(msg) == 0:
        await matcher.finish("请在该指令后加入参数，例如【114.51.49.19:1810】")
    [host, port] = split_maohao(msg)
    group_id = event.group_id
    msg = await add_ip(group_id, host, port)
    await matcher.finish(msg)


@del_queries.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if not msg.isdigit():
        await matcher.finish("请输入正确的序号数字")
    group_id = event.group_id
    msg = await del_ip(group_id, msg)
    await matcher.finish(msg)


@show_queries.handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    group_id = event.group_id
    msg = await show_ip(group_id)
    if not msg:
        await matcher.finish("当前没有启动的服务器捏")
    if isinstance(msg, str):
        await matcher.finish(msg)
    else:
        await matcher.finish(MessageSegment.image(msg))


@join_server.handle()
async def _(args: Message = CommandArg()):
    msg = args.extract_plain_text()
    url = await get_number_url(msg)
    await join_server.finish(url)


@up_workshop.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("ip", args)


@up_workshop.got("ip", prompt="请输入创意工坊网址或者物品id")
async def _(matcher: Matcher, state: T_State, tag: str = ArgPlainText("ip")):
    # 这一部分注释类型有大问题，反正能跑就不改了
    msg = await workshop_msg(tag)
    if not msg:
        await matcher.finish("没有这个物品捏")
    elif isinstance(msg, dict):
        pic = await url_to_byte(msg["图片地址"])
        if not pic:
            return
        message: str = ""
        for item, value in msg.items():
            if item in ["图片地址", "下载地址", "细节"] or not isinstance(item, str):
                continue
            message += item + ":" + value + "\n"
        state["dic"] = msg
        await matcher.finish(MessageSegment.image(pic) + (message))
    elif isinstance(msg, list):
        lenge = len(msg)
        pic = await url_to_byte(msg[0]["图片地址"])  # type: ignore
        message: str = f"有{lenge}个文件\n"
        ones = []
        for one in msg:
            for item, value in one.items():
                if item in ["图片地址", "下载地址", "细节"]:
                    continue
                message += f"{item}:{value}\n"
            ones.append(one)
        state["dic"] = ones


@up_workshop.got("is_sure", prompt='如果需要上传，请发送 "yes"')
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent, state: T_State):
    is_sure = str(state["is_sure"])
    if is_sure == "yes":
        data_dict: Union[dict, List[dict]] = state["dic"]
        logger.info("开始上传")
        if isinstance(data_dict, dict):
            data_file = await url_to_byte(data_dict["下载地址"])
            if not data_file:
                return
            file_name = data_dict["名字"] + ".vpk"
            await matcher.send("获取地址成功，尝试上传")
            await upload_file(bot, event, data_file, file_name)
        else:
            data_file_list = []
            for data_one in data_dict:
                data_file = await url_to_byte(data_one["下载地址"])
                data_file_list.append(data_file)
                if not data_file:
                    return
                file_name = data_one["名字"] + ".vpk"
                await all_zip_to_one(data_file_list)
                await upload_file(bot, event, data_file, file_name)
    else:
        await matcher.finish("已取消上传")


@updata.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    """更新"""
    anne_ip_dict = await updata_anne_server()
    if not anne_ip_dict:
        await matcher.finish("网络开小差了捏")
    server_number = len(anne_ip_dict["云"])
    await matcher.finish(f"更新成功\n一共更新了{server_number}个电信anne服ip")


@vtf_make.handle()
async def _(matcher: Matcher, state: T_State, args: Message = CommandArg()):
    msg: str = args.extract_plain_text()
    if msg not in ["拉伸", "填充", "覆盖", ""]:
        await matcher.finish("错误的图片处理方式")
    if msg == "":
        msg = "拉伸"
    state["way"] = msg
    logger.info("方式", msg)


@vtf_make.got("image", prompt="请发送喷漆图片")
async def _(bot: Bot, event: MessageEvent, state: T_State, tag=Arg("image")):
    pic_msg: MessageSegment = state["image"][0]
    pic_url = pic_msg.data["url"]
    logger.info(pic_url)
    logger.info(type(pic_url))
    tag = state["way"]
    pic_bytes = await url_to_byte(pic_url)
    if not pic_bytes:
        return
    img_io = await img_to_vtf(pic_bytes, tag)
    img_bytes = img_io.getbuffer()
    usr_id = event.user_id
    file_name: str = str(usr_id) + ".vtf"
    await upload_file(bot, event, img_bytes, file_name)


@smx_file.handle()
async def _(
    matcher: Matcher,
):
    smx_path = Path(
        l4_config.l4_ipall[l4_config.l4_number]["location"],
        "left4dead2/addons/sourcemod/plugins",
    )
    name_smx = get_vpk(smx_path, file_=".smx")
    logger.info("获取文件列表成功")
    mes = "当前服务器下有以下smx文件"
    msg = ""
    msg = mes_list(msg, name_smx).replace(" ", "")
    await matcher.finish(mode_txt_to_img(mes, msg))


# @search_api.handle()
# async def _(matcher:Matcher,state:T_State,event:GroupMessageEvent,args:Message = CommandArg()):
#     msg:str = args.extract_plain_text()
#     # if msg.startswith('代码'):
#         # 建图代码返回三方图信息
#     data = await seach_map(msg,l4_config.l4_master[0],l4_config.l4_key)
#     # else:
#     if type(data) == str:
#         await matcher.finish(data)
#     else:
#         state['maps'] = data
#         await matcher.send(await map_dict_to_str(data))
@help_.handle()
async def _(matcher: Matcher):
    msg = [
        "=====求生机器人帮助=====",
        "1、电信服战绩查询【求生anne[id/steamid/@]】",
        "2、电信服绑定【求生绑定[id/steamid]】",
        "3、电信服状态查询【云xx】" "4、创意工坊下载【创意工坊下载[物品id/链接]】",
        "5、指定ip查询【求生ip[ip]】(可以是域名)",
        "6、求生喷漆制作【求生喷漆】",
        "6、本地服务器操作(略，详情看项目地址)",
    ]
    messgae = ""
    for i in msg:
        messgae += i + "\n"
    await matcher.finish(messgae)


@search_api.got("is_sure", prompt='如果需要上传，请发送 "yes"')
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent, state: T_State):
    is_sure = str(state["is_sure"])
    if is_sure == "yes":
        data_dict: dict = state["maps"][0]
        if isinstance(data_dict, dict):
            logger.info("开始上传")
            if l4_config.l4_only:
                reu = await url_to_byte_name(data_dict["url"], "htp")
            else:
                reu = await url_to_byte_name(data_dict["url"])
            if not reu:
                return
            data_file, file_name = reu
            if data_file:
                await matcher.send("获取地址成功，尝试上传")
                await upload_file(bot, event, data_file, file_name)
            else:
                await search_api.send("出错了，原因是下载链接不存在")
        else:
            ...
            # logger.info("开始上传")
            # for data_one in data_dict:
            #     reu = await url_to_byte_name(data_one["url"])
            #     if not reu:
            #         return
            #     data_file, file_name = reu
            #     await all_zip_to_one()
            #     await upload_file(bot, event, data_file, file_name)
    else:
        await matcher.finish("已取消上传")


# @reload_ip.handle()
# async def _(matcher:Matcher):
#     global matchers
#     await matcher.send('正在重载ip，可能需要一点时间')
#     for _, l4_matchers in matchers.items():
#         for l4_matcher in l4_matchers:
#             l4_matcher.destroy()
#     await get_des_ip()
#     await matcher.finish('已重载ip')


@driver.on_shutdown
async def close_db():
    """关闭数据库"""
    sq_L4D2._close()
