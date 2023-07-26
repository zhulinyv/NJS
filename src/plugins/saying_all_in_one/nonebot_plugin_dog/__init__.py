import re
import httpx
import random
import nonebot
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot import on_command, on_endswith
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_OWNER, GROUP_ADMIN

from .utils import *


openstats = on_endswith("文案", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
                       priority=10, block=True)

dog_matcher = on_command("舔狗日记", aliases={"舔狗嘤嘤嘤"},
                         priority=10, block=True)

laugh_matcher = on_command("讲个笑话", aliases={"说个笑话"},
                           priority=10, block=True)

wenan_matcher = on_command("文案", aliases={"语录"},
                           priority=10, block=True)

love_message = on_command("土味情话", aliases={"情话"},
                          priority=10, block=True)


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
        urls = ["https://v.api.aa1.cn/api/tiangou/", "https://api.oick.cn/dog/api.php", "https://api.gmit.vip/Api/Dog?format=text"]
        url = random.choice(urls)
        try:
            # 使用 httpx.AsyncClient 获取 API，存储为 response 变量
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
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
        urls = ["https://api.vvhan.com/api/joke", "https://api.gmit.vip/Api/Xiaohua?format=text"]
        url = random.choice(urls)
        try:
            # 使用 httpx.AsyncClient 获取 API，存储为 response 变量
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
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
        urls = ["https://api.gmit.vip/Api/WaSentence?format=text"]
        url = random.choice(urls)
        try:
            # 使用 httpx.AsyncClient 获取 API，存储为 response 变量
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response_text = response.text
        except Exception as error:
            await laugh_matcher.finish(MessageSegment.text(str(error)))
        await matcher.finish(MessageSegment.text(response_text.strip()), block=True)
    else:
        await laugh_matcher.finish(
            MessageSegment.text(f"文案准备中喵，等待{wenan_cd - cd:.0f}秒后再找我喵~"),
            at_sender=True, block=True)

@love_message.handle()
async def love(event: GroupMessageEvent, matcher: Matcher):  # 定义异步函数love
    if not (await check_group_allow(str(event.group_id))):
        await love_message.finish(notAllow, at_sender=True)
    uid = event.get_user_id()                                            # 获取用户id
    try:
        cd = event.time - love_CD_dir[uid]                           # 计算cd
    except KeyError:
        cd = love_cd + 1                                           # 没有记录则cd为cd_time+1
    if (
        cd > love_cd
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):                                                                        # 记录cd
        love_CD_dir.update({uid: event.time})
        urls = ["https://api.gmit.vip/Api/LoveSentence?format=text"]
        url = random.choice(urls)
        try:
            # 使用 httpx.AsyncClient 获取 API，存储为 response 变量
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response_text = response.text
        except Exception as error:
            await laugh_matcher.finish(MessageSegment.text(str(error)))
        await matcher.finish(MessageSegment.text(response_text.strip()), block=True)
    else:
        await laugh_matcher.finish(
            MessageSegment.text(f"情话准备中喵，等待{love_cd - cd:.0f}秒后再找我喵~"),
            at_sender=True, block=True)

@openstats.handle()
async def _(event: GroupMessageEvent):
    command = event.message.extract_plain_text().replace("文案", "")
    gid = str(event.group_id)  # 群号
    if "开启" == command:
        if gid in groupdata:
            groupdata[gid]["allow"] = True
            write_group_data()
            await openstats.finish("功能已开启喵~")
        else:
            groupdata.update({gid: {"allow": True}})
            write_group_data()
            await openstats.finish("功能已开启喵~")
    elif "关闭" == command:
        if gid in groupdata:
            groupdata[gid]["allow"] = False
            write_group_data()
            await openstats.finish("功能已禁用喵~")
        else:
            groupdata.update({gid: {"allow": False}})
            write_group_data()
            await openstats.finish("功能已禁用喵~")
    else:
        await openstats.finish()