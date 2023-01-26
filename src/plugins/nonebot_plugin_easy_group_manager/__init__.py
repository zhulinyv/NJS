"""导入依赖"""
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, ActionFailed, Message
from nonebot.adapters.onebot.v11.permission import GROUP_OWNER, GROUP_ADMIN
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot import on_command
from httpx import AsyncClient
import nonebot
import re

"""导入变量"""
try:
    # 当 admin_model 为 1 时，调用 API，BOT 不需要为群主。
    # 当 admin_model 为 2 时，使用 Nonebot 内置函数，BOT 必须为群主。
    admin_model: int = nonebot.get_driver().config.admin_model
    skey: str = nonebot.get_driver().config.skey
    pskey: str = nonebot.get_driver().config.pskey
except:
    admin_model: int = 1
    skey: str = ''
    pskey: str = ''


"""响应部分"""
set_admin = on_command('添加管理员', aliases={'设置管理员'}, permission=SUPERUSER|GROUP_OWNER, priority=2, block=True)
unset_admin = on_command('取消管理员', permission=SUPERUSER|GROUP_OWNER, priority=2, block=True)
ban = on_command('禁言',aliases={"口球"}, permission=SUPERUSER|GROUP_OWNER|GROUP_ADMIN, priority=10, block=True)
unban = on_command('解禁', permission=SUPERUSER|GROUP_OWNER|GROUP_ADMIN, priority=10, block=True)
kick = on_command('移出', permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER, priority=10, block=True)
kick_ban = on_command('移出并拉黑', permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER, priority=10, block=True)



"""执行部分"""
@set_admin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # 获取被操作群员的ID、所在群号、所在群群主ID
    qid = await get_at(event)
    gid = event.group_id
    member_list = await bot.get_group_member_list(group_id=gid)
    for owner in member_list:
        if owner['role']=='owner':
            owner_id = owner['user_id']
            break
    # 模式判断
    if admin_model == 1:
        api = f'https://ovooa.com/API/quns/api.php?qq={owner_id}&skey={skey}&pskey={pskey}&group={gid}&uin={qid}&kt=1'
        msg = await admin_api(api)
        await set_admin.send(f"{msg}", at_sender=True)
    elif admin_model == 2:
        try:
            await bot.set_group_admin(group_id=gid, user_id=qid, enable=True)
            await set_admin.send('设置管理员成功~', at_sender=True)
        except ActionFailed:
            await set_admin.send('权限不足捏', at_sender=True)
    else:
        await set_admin.send('env 配置项有误，联系 SUPPERUSER 检查！', at_sender=True)

@unset_admin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # 获取被操作群员的ID、所在群号、所在群群主ID
    qid = await get_at(event)
    gid = event.group_id
    member_list = await bot.get_group_member_list(group_id=gid)
    for owner in member_list:
        if owner['role']=='owner':
            owner_id = owner['user_id']
            break
    # 模式判断
    if admin_model == 1:
        api = f'https://ovooa.com/API/quns/api.php?qq={owner_id}&skey={skey}&pskey={pskey}&group={gid}&uin={qid}&kt=2'
        msg = await admin_api(api)
        await unset_admin.send(f"{msg}")
    elif admin_model == 2:
        try:
            await bot.set_group_admin(group_id=gid, user_id=qid, enable=False)
            await unset_admin.send('取消管理员成功~', at_sender=True)
        except ActionFailed:
            await unset_admin.send('权限不足捏', at_sender=True)
    else:
        await unset_admin.send('env 配置项有误，联系 SUPPERUSER 检查！', at_sender=True)

@ban.handle()
async def _(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    qid = await get_at(event)
    msg = msg.extract_plain_text().strip()
    # 这里去除 CQ 码提取数字并扩大 60 倍变单位为分钟
    time = int(re.sub(r"\[.*?\]", "", msg))*60
    await bot.set_group_ban(group_id = event.group_id, user_id = qid, duration = time)

@unban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qid = await get_at(event)
    # duration = 0 即为解除禁言
    await bot.set_group_ban(group_id = event.group_id, user_id = qid, duration = 0)

@kick.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qid = await get_at(event)
    gid = event.group_id
    try:
        await bot.set_group_kick(group_id=gid, user_id=qid, reject_add_request=False)
    except ActionFailed:
        await kick.send('权限不足捏', at_sender=True)

@kick_ban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qid = await get_at(event)
    gid = event.group_id
    try:
        # reject_add_request=True 阻止再次申请
        await bot.set_group_kick(group_id=gid, user_id=qid, reject_add_request=True)
    except ActionFailed:
        await kick_ban.send('权限不足捏', at_sender=True)



"""一些工具"""
# 获取倍艾特用户 ID
async def get_at(event: GroupMessageEvent) -> int:
    msg=event.get_message()
    for msg_seg in msg:
        if msg_seg.type == "at":
            return int(msg_seg.data["qq"])

# 调用 API 设置群员身份
async def admin_api(api):
    async with AsyncClient() as client:
        res = (await client.get(api)).json()
        if res["code"] == 1:
            text = res["text"]
            return text
        elif res["code"] == -2:
            return 'skey为空'
        elif res["code"] == -3:
            return 'pskey为空'
        elif res["code"] == -8:
            return 'key过期或者上下管理的人本身就是/不是管理'
        else:
            return "寄, 咱也布吉岛啦 >_<"