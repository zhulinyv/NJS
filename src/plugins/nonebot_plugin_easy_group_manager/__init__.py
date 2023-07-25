"""导入依赖"""
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, ActionFailed, Message
from nonebot.adapters.onebot.v11.permission import GROUP_OWNER, GROUP_ADMIN
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot import on_command
from httpx import AsyncClient
import nonebot
import re
try:
    import ujson as json
except:
    import json

__plugin_meta__ = PluginMetadata(
    name="群管",
    description="简易群管",
    usage=("""
设置管理员 + @somebody: 设置一个管理员
取消管理员 + @somebody: 取消一个管理员
禁言/口球 + @somebody + 阿拉伯数字: 禁言某人，单位分钟，需要 BOT 为管理员
解禁 + @somebody: 解除某人禁言，需要 BOT 为管理员
移出 + @somebody: 移出某人，需要 BOT 为管理员
移出并拉黑 + @somebody: 移出并拉黑，需要 BOT 为管理员
(开启)全员禁言: 开启全员禁言
解除/关闭全员禁言: 关闭全员禁言
"""
    ),
    extra={
        "author": "zhulinyv <zhulinyv2005@outlook.com>",
        "version": "0.3.1",
    },
)



"""导入变量"""
config = nonebot.get_driver().config
admin_model: int =  getattr(config, "admin_model", 1)
skey: str =  getattr(config, "skey", "")
pskey: str =  getattr(config, "pskey", "")


"""响应部分"""
set_admin = on_command('添加管理员', aliases={'设置管理员'}, permission=SUPERUSER|GROUP_OWNER, priority=2, block=True)
unset_admin = on_command('取消管理员', permission=SUPERUSER|GROUP_OWNER, priority=2, block=True)
ban = on_command('禁言',aliases={"口球"}, permission=SUPERUSER|GROUP_OWNER|GROUP_ADMIN, priority=10, block=True)
unban = on_command('解禁', permission=SUPERUSER|GROUP_OWNER|GROUP_ADMIN, priority=10, block=True)
kick = on_command('移出', permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER, priority=10, block=True)
kick_ban = on_command('移出并拉黑', permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER, priority=10, block=True)
shut = on_command('全员禁言', aliases={'开启全员禁言'}, permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER, priority=10, block=True)
not_shut = on_command('解除全员禁言', aliases={'关闭全员禁言'}, permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER, priority=10, block=True)



"""执行部分"""
@set_admin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # 获取被操作群员的ID、所在群号、所在群群主ID
    qid_list = await get_at(event.json())
    gid = event.group_id
    member_list = await bot.get_group_member_list(group_id=gid)
    for owner in member_list:
        if owner['role']=='owner':
            owner_id = owner['user_id']
            break
    # 模式判断
    if admin_model == 1:
        for qid in qid_list:
            api = f'https://ovooa.muban.plus/API/quns/api.php?qq={owner_id}&skey={skey}&pskey={pskey}&group={gid}&uin={qid}&kt=1'
            print(api)
            msg = await admin_api(api)
            await set_admin.send(f"{msg}", at_sender=True)
    elif admin_model == 2:
        for qid in qid_list:
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
    qid_list = await get_at(event.json())
    gid = event.group_id
    member_list = await bot.get_group_member_list(group_id=gid)
    for owner in member_list:
        if owner['role']=='owner':
            owner_id = owner['user_id']
            break
    # 模式判断
    if admin_model == 1:
        for qid in qid_list:
            api = f'https://ovooa.com/API/quns/api.php?qq={owner_id}&skey={skey}&pskey={pskey}&group={gid}&uin={qid}&kt=2'
        msg = await admin_api(api)
        await unset_admin.send(f"{msg}", at_sender=True)
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
    qid_list = await get_at(event.json())
    msg = msg.extract_plain_text().strip()
    # 这里去除 CQ 码提取数字并扩大 60 倍变单位为分钟
    time = int(re.sub(r"\[.*?\]", "", msg))*60
    for qid in qid_list:
        try:
            print(qid)
            await bot.set_group_ban(group_id = event.group_id, user_id = qid, duration = time)
        except ActionFailed:
            await unset_admin.send('权限不足捏', at_sender=True)

@unban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qid_list = await get_at(event.json())
    # duration = 0 即为解除禁言
    for qid in qid_list:
        await bot.set_group_ban(group_id = event.group_id, user_id = qid, duration = 0)

@kick.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qid_list = await get_at(event.json())
    gid = event.group_id
    for qid in qid_list:
        try:
            await bot.set_group_kick(group_id=gid, user_id=qid, reject_add_request=False)
            await kick.send(f'已移出群员{qid}')
        except ActionFailed:
            await kick.send('权限不足捏', at_sender=True)

@kick_ban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qid_list = await get_at(event.json())
    gid = event.group_id
    for qid in qid_list:
        try:
            # reject_add_request=True 阻止再次申请
            await bot.set_group_kick(group_id=gid, user_id=qid, reject_add_request=True)
            await kick.send(f'已移出并拉黑群员{qid}')
        except ActionFailed:
            await kick_ban.send('权限不足捏', at_sender=True)

@shut.handle()
async def the_world(bot: Bot, event: GroupMessageEvent):
    try:
        await bot.set_group_whole_ban(group_id=event.group_id, enable=True)
        await bot.send_msg(message="已开启全员禁言~", at_sender=True)
    except:
        await bot.send_msg(message="权限不足捏~", at_sender=True)

@not_shut.handle()
async def time_flow(bot: Bot, event: GroupMessageEvent):
    try:
        await bot.set_group_whole_ban(group_id=event.group_id, enable=False)
        await bot.send_msg(message="已关闭全员禁言~", at_sender=True)
    except:
        await bot.send_msg(message="权限不足捏~", at_sender=True)



"""一些工具"""
# 获取被艾特用户 ID列表
async def get_at(data:str) -> list[int]:
    qq_list = []
    data = json.loads(data)
    try:
        for msg in data['message']:
            if msg['type'] == 'at':
                qq_list.append(int(msg['data']['qq']))
        return qq_list
    except Exception:
        return []

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