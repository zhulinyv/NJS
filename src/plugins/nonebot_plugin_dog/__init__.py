# import httpx
import nonebot
import requests
import re
from re import I
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11.permission import GROUP_OWNER, GROUP_ADMIN
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent

from .utils import *


openstats = on_regex(r"^(开启文案|关闭文案)", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
                     flags=I, priority=10, block=True)

dog_matcher = on_command("舔狗日记", aliases={"舔狗嘤嘤嘤"},
                         priority=10, block=True)

laugh_matcher = on_command("讲个笑话", aliases={"说个笑话"},
                           priority=10, block=True)

# hitokoto_matcher = on_command("一言", aliases={"一言"},
#                               priority=10, block=True)

wenan_matcher = on_command("文案", aliases={"语录"},
                           priority=10, block=True)

# music_matcher = on_command("点歌", aliases={"点歌"},
#                           priority=10, block=True)

@dog_matcher.handle()
async def dog(event: GroupMessageEvent, matcher: Matcher):     # 定义异步函数 dog
    if not (await check_group_allow(str(event.group_id))):
        await dog_matcher.finish(notAllow, at_sender=True)
    uid = event.get_user_id()                                         # 获取用户id
    try:
        cd = event.time - dog_CD_dir[uid]                             # 计算cd
    except KeyError:
        cd = dog_cd + 1                                        # 没有记录则cd为cd_time+1
    if (
        cd > dog_cd
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):                                                                     # 记录cd
        dog_CD_dir.update({uid: event.time})
        try:
            response = requests.get("https://api.juncikeji.xyz/api/tgrj.php", verify=False)
            response_text = response.text
        except Exception as error:
            await dog_matcher.finish(MessageSegment.text(str(error)))
        await matcher.finish(MessageSegment.text(response_text.strip()), block=True)
    else:
        await dog_matcher.finish(
            MessageSegment.text(f"不要深情了喵，休息{dog_cd - cd:.0f}秒后再找我喵~"),
            at_sender=True, block=True)


@laugh_matcher.handle()
async def laugh(event: GroupMessageEvent, matcher: Matcher):     # 定义异步函数 laugh
    if not (await check_group_allow(str(event.group_id))):
        await dog_matcher.finish(notAllow, at_sender=True)
    uid = event.get_user_id()                                           # 获取用户id
    try:
        cd = event.time - laugh_CD_dir[uid]                             # 计算cd
    except KeyError:
        cd = laugh_cd + 1                                          # 没有记录则cd为cd_time+1
    if (
        cd > laugh_cd
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):                                                                       # 记录cd
        laugh_CD_dir.update({uid: event.time})
        try:
            response = requests.get("https://api.juncikeji.xyz/api/qwxh.php", verify=False)
            response_text = response.text
        except Exception as error:
            await laugh_matcher.finish(MessageSegment.text(str(error)))
        response_text = re.sub(r'。。\\n', '\n', response_text)
        response_text = response_text.replace('。。', '')
        await matcher.finish(MessageSegment.text(response_text.strip()), block=True)
    else:
        await laugh_matcher.finish(
            MessageSegment.text(f"我在准备更精彩的笑话喵，等待{laugh_cd - cd:.0f}秒后再找我喵~"),
            at_sender=True, block=True)

'''
@hitokoto_matcher.handle()
async def hitokoto(event: GroupMessageEvent, matcher: Matcher):  # 定义异步函数hitokoto
    if not (await check_group_allow(str(event.group_id))):
        await dog_matcher.finish(notAllow, at_sender=True)
    uid = event.get_user_id()                                            # 获取用户id
    try:
        cd = event.time - hitokoto_CD_dir[uid]                           # 计算cd
    except KeyError:
        # 没有记录则cd为cd_time+1
        cd = hitokoto_cd + 1
    if (
        cd > hitokoto_cd
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):                                                                        # 记录cd
        hitokoto_CD_dir.update({uid: event.time})
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://v1.hitokoto.cn?c=a&c=b&c=c&c=d&c=e&c=f&c=j")
        except Exception as error:
            await hitokoto_matcher.finish(MessageSegment.text(f"获取一言失败"), at_sender=True, block=True)
        data = response.json()
        msg = data["hitokoto"]
        add = ""
        if works := data["from"]:
            add += f"《{works}》"
        if from_who := data["from_who"]:
            add += f"{from_who}"
        if add:
            msg += f"\n——{add}"
        await matcher.finish(msg)
    else:
        await laugh_matcher.finish(
            MessageSegment.text(f"休息 {hitokoto_cd - cd:.0f}秒后才能再使用喵~"),
            at_sender=True, block=True)
'''

@wenan_matcher.handle()
async def wenan(event: GroupMessageEvent, matcher: Matcher):  # 定义异步函数wenan
    if not (await check_group_allow(str(event.group_id))):
        await wenan_matcher.finish(notAllow, at_sender=True)
    uid = event.get_user_id()                                            # 获取用户id
    try:
        cd = event.time - wenan_CD_dir[uid]                           # 计算cd
    except KeyError:
        cd = wenan_cd + 1                                           # 没有记录则cd为cd_time+1
    if (
        cd > wenan_cd
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):                                                                        # 记录cd
        wenan_CD_dir.update({uid: event.time})
        try:
            response = requests.get("https://api.juncikeji.xyz/api/sgyl.php", verify=False)
            response_text = response.text
        except Exception as error:
            await laugh_matcher.finish(MessageSegment.text(str(error)))
        await matcher.finish(MessageSegment.text(response_text.strip()), block=True)
    else:
        await laugh_matcher.finish(
            MessageSegment.text(f"文案准备中喵，等待{wenan_cd - cd:.0f}秒后再找我喵~"),
            at_sender=True, block=True)
'''
@music_matcher.handle()
async def music(event: GroupMessageEvent, matcher: Matcher, msg: Message = CommandArg()):  # 定义异步函数music
    if not (await check_group_allow(str(event.group_id))):
        await music_matcher.finish(notAllow, at_sender=True)
    uid = event.get_user_id()                                            # 获取用户id
    try:
        cd = event.time - music_CD_dir[uid]                           # 计算cd
    except KeyError:
        cd = music_cd + 1                                           # 没有记录则cd为cd_time+1
    if (
        cd > music_cd
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):                                                                        # 记录cd
        music_CD_dir.update({uid: event.time})
    api = 'https://api.juncikeji.xyz/api/music.php?mode=list&type=json&song={song_name}'
    song_name = msg.extract_plain_text().strip()
    message = await music_search(api)
    await music_matcher.finish(message)

async def music_search(api):
    async with httpx.AsyncClient() as client:
        response =(await client.get(api)).json()
        if response["code"] == 200:
            id = (response["data"]["id"])
            name = (response["date"]["name"])
            singer = (response["data"]["singer"])
            response = f"序号: {id}\n歌曲名称: {name}\n作曲家: {singer}"
            return response
        elif response["code"] == 400:
            response = (response["msg"])
            return response
'''

@openstats.handle()
async def _(event: GroupMessageEvent, state: T_State):
    gid = str(event.group_id)  # 群号
    # 获取用户输入的参数
    args = list(state["_matched_groups"])
    command = args[0]
    if "开启文案" in command:
        if gid in groupdata:
            groupdata[gid]["allow"] = True
            write_group_data()
            await openstats.finish("功能已开启喵~")
        else:
            groupdata.update({gid: {"allow": True}})
            write_group_data()
            await openstats.finish("功能已开启喵~")
    elif "关闭文案" in command:
        if gid in groupdata:
            groupdata[gid]["allow"] = False
            write_group_data()
            await openstats.finish("功能已禁用喵~")
        else:
            groupdata.update({gid: {"allow": False}})
            write_group_data()
            await openstats.finish("功能已禁用喵~")
