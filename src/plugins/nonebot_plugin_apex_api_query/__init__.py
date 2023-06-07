from nonebot import get_bot, on_command, get_driver, require
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, PrivateMessageEvent, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot_plugin_guild_patch import GuildMessageEvent, GUILD_ADMIN, GUILD_OWNER, GUILD_SUPERUSER
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
import sqlite3

require('nonebot_plugin_apscheduler')
require("nonebot_plugin_localstore")

from nonebot_plugin_apscheduler import scheduler
import nonebot_plugin_localstore as store
from nonebot_plugin_txt2img import Txt2Img
from pathlib import Path
from httpx import AsyncClient
from typing import Union
from .config import Config

# 插件元数据
__plugin_meta__ = PluginMetadata(
    'Apex API Query',
    'Apex Legends API 查询插件',
    '''
    `/bridge [玩家名称]` 、`/玩家 [玩家名称]` - 根据玩家名称查询玩家信息 (暂仅支持查询 PC 平台玩家信息), 
    `/uid [玩家 UID]`、`/UID [玩家 UID]` - 根据玩家 UID 查询玩家信息 (暂仅支持查询 PC 平台玩家信息), 
    `/uid`、`/自查` - 根据玩家已绑定的 UID 自动查询玩家信息, 
    `/maprotation` 、 `/地图` - 查询当前地图轮换, 
    `/predator` 、 `/猎杀` - 查询顶尖猎杀者信息, 
    `/crafting` 、 `/制造` - 查询当前制造轮换, 
    `/servers`、`/服务` - 查看当前服务器状态, 
    `/submap`、`/订阅地图` - 订阅地图轮换 (每整点查询) (仅 群聊/频道 可用), 
    `/unsubmap`、`/取消订阅地图` - 取消订阅地图轮换 (仅 群聊/频道 可用), 
    `/subcraft`、`/订阅制造` - 订阅制造轮换 (每日 2 时查询) (仅 群聊/频道 可用), 
    `/unsubcraft`、`/取消订阅制造` - 取消订阅制造轮换 (仅 群聊/频道 可用), 
    `/bind [玩家 UID]`、`/绑定 [玩家 UID]` - 将 UID 与 QQ 账号绑定, 
    `/unbind`、`/解绑` - 将 UID 与 QQ 账号解除绑定.
    '''
)

# 读取配置
plugin_config = Config.parse_obj(get_driver().config)
api_key = plugin_config.apex_api_key
api_url = plugin_config.apex_api_url
api_t2i = plugin_config.apex_api_t2i
plugin_data_file: Path = store.get_data_file("nonebot_plugin_apex_api_query", "database.db")

# 创建事件响应器
player_statistics = on_command('bridge', aliases = {'玩家'})
uid_statistics = on_command('uid', aliases = {'UID', '自查'})
map_protation = on_command('maprotation', aliases = {'地图'})
predator = on_command('predator', aliases = {'猎杀'})
crafting_rotation = on_command('crafting', aliases = {'制造'})
servers = on_command('servers', aliases = {'服务'})
sub_map = on_command('submap', aliases = {'订阅地图'}, permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER | GUILD_ADMIN | GUILD_OWNER | GUILD_SUPERUSER)
unsub_map = on_command('unsubmap', aliases = {'取消订阅地图'}, permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER | GUILD_ADMIN | GUILD_OWNER | GUILD_SUPERUSER)
sub_craft = on_command('subcraft', aliases = {'订阅制造'}, permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER | GUILD_ADMIN | GUILD_OWNER | GUILD_SUPERUSER)
unsub_craft = on_command('unsubcraft', aliases = {'取消订阅制造'}, permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER | GUILD_ADMIN | GUILD_OWNER | GUILD_SUPERUSER)
bind_uid = on_command('bind', aliases = {'绑定'})
unbind_uid = on_command('unbind', aliases = {'解绑'})

# Bot 连接
@get_driver().on_bot_connect
async def bot_connect():
    await sql().on_start()
    await job().on_start()

# Bot 断开
@get_driver().on_bot_disconnect
async def bot_disconnect():
    await sql().on_close()

# 玩家名称查询
@player_statistics.handle()
async def player_func(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent], player_name: Message = CommandArg()):
    if not player_name:
        await player_statistics.send('用法: /玩家 [玩家名称]')
        return
    service = 'bridge'
    payload = {'auth': api_key, 'player': str(player_name), 'platform': 'PC'}
    await player_statistics.send(f'正在查询: 玩家 {player_name}')
    response = await api_query(service, payload)
    if api_t2i:
        msg = await t2i(service, response)
    else:
        msg = response
    await player_statistics.send(msg)

# 玩家 UID 查询
@uid_statistics.handle()
async def uid_func(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent], player_name: Message = CommandArg()):
    if not player_name:
        if await sql().check_uid(event.user_id):
            player_name = await sql().check_uid(event.user_id)
        else:
            await player_statistics.send('用法: /UID [玩家 UID]')
            return
    service = 'bridge'
    payload = {'auth': api_key, 'uid': str(player_name), 'platform': 'PC'}
    await uid_statistics.send(f'正在查询: UID {player_name}')
    response = await api_query(service, payload)
    if api_t2i:
        msg = await t2i(service, response)
    else:
        msg = response
    await uid_statistics.send(msg)

# 地图轮换查询
@map_protation.handle()
async def map_func(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]):
    service = 'maprotation'
    payload = {'auth': api_key, 'version': '2'}
    await map_protation.send('正在查询: 地图轮换')
    response = await api_query(service, payload)
    if api_t2i:
        msg = await t2i(service, response)
    else:
        msg = response
    await map_protation.send(msg)

# 顶尖猎杀者查询
@predator.handle()
async def predator_func(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]):
    service = 'predator'
    payload = {'auth': api_key}
    await predator.send('正在查询: 顶尖猎杀者')
    response = await api_query(service, payload)
    if api_t2i:
        msg = await t2i(service, response)
    else:
        msg = response
    await predator.send(msg)

# 制造轮换查询
@crafting_rotation.handle()
async def crafting_func(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]):
    service = 'crafting'
    payload = {'auth': api_key}
    await crafting_rotation.send('正在查询: 制造轮换')
    response = await api_query(service, payload)
    if api_t2i:
        msg = await t2i(service, response)
    else:
        msg = response
    await crafting_rotation.send(msg)

# 服务器状态查询
@servers.handle()
async def servers_func(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]):
    service = 'servers'
    payload = {'auth': api_key}
    await servers.send('正在查询: 服务器状态')
    response = await api_query(service, payload)
    if api_t2i:
        msg = await t2i(service, response)
    else:
        msg = response
    await servers.send(msg)

# 订阅地图轮换
@sub_map.handle()
async def submap_func(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    try:
        hour = None
        bot_id = bot.self_id
        if isinstance(event, GroupMessageEvent):
            id = str(event.group_id) + '_map'
            await job().add(submap, id, hour, bot_id, group_id = event.group_id)
        elif isinstance(event, GuildMessageEvent):
            id = str(event.channel_id) + '_map'
            await job().add(submap, id, hour, bot_id, guild_id = event.guild_id, channel_id = event.channel_id)
        await sql().addsub(event, bot_id, 'maprotation')
        await sub_map.send('已订阅地图轮换。')
    except Exception as err:
        await sub_map.send(f'订阅地图轮换失败。\n{err}')

# 地图轮换定时任务
async def submap(bot_id, group_id, guild_id, channel_id):
    bot = get_bot(bot_id)
    service = 'maprotation'
    payload = {'auth': api_key, 'version': '2'}
    response = await api_query(service, payload)
    if api_t2i:
        msg = await t2i(service, response)
    else:
        msg = response
    if group_id:
        await bot.send_group_msg(group_id = group_id, message = msg)
    elif channel_id:
        await bot.send_guild_channel_msg(guild_id = guild_id, channel_id = channel_id, message = msg)

# 取消订阅地图轮换
@unsub_map.handle()
async def unsub_map_func(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    try:
        if isinstance(event, GroupMessageEvent):
            id = str(event.group_id) + '_map'
        elif isinstance(event, GuildMessageEvent):
            id = str(event.channel_id) + '_map'
        await job().remove(id)
        await sql().delsub(event, 'maprotation')
        await unsub_map.send('已取消订阅地图轮换。')
    except Exception as err:
        await unsub_map.send(f'取消订阅地图轮换失败。\n{err}')

# 订阅制造轮换
@sub_craft.handle()
async def subcraft_func(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    try:
        hour = 2
        bot_id = bot.self_id
        if isinstance(event, GroupMessageEvent):
            id = str(event.group_id) + '_craft'
            await job().add(subcraft, id, hour, bot_id, group_id = event.group_id)
        elif isinstance(event, GuildMessageEvent):
            id = str(event.channel_id) + '_craft'
            await job().add(subcraft, id, hour, bot_id, guild_id = event.guild_id, channel_id = event.channel_id)
        await sql().addsub(event, bot_id, 'crafting')
        await sub_craft.send('已订阅制造轮换。')
    except Exception as err:
        await sub_craft.send(f'订阅制造轮换失败。\n{err}')


# 制造轮换定时任务
async def subcraft(bot_id, group_id, guild_id, channel_id):
    bot = get_bot(bot_id)
    service = 'crafting'
    payload = {'auth': api_key}
    response = await api_query(service, payload)
    if api_t2i:
        msg = await t2i(service, response)
    else:
        msg = response
    if group_id:
        await bot.send_group_msg(group_id = group_id, message = msg)
    elif channel_id:
        await bot.send_guild_channel_msg(guild_id = guild_id, channel_id = channel_id, message = msg)

# 取消订阅制造轮换
@unsub_craft.handle()
async def unsub_craft_func(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    try:
        if isinstance(event, GroupMessageEvent):
            id = str(event.group_id) + '_craft'
        elif isinstance(event, GuildMessageEvent):
            id = str(event.channel_id) + "_craft"
        await job().remove(id)
        await sql().delsub(event, 'crafting')
        await unsub_craft.send(f'已取消订阅制造轮换。')
    except Exception as err:
        await unsub_craft.send(f'取消订阅制造轮换失败。\n{err}')

# 异步查询
async def api_query(service, payload):
    try:
        async with AsyncClient() as client:
            response = await client.get(api_url + service, params = payload, timeout = None)
        if response.status_code != 200 or response.text.find('Error') != -1:
            data = f'查询失败: API 错误: {response.text}'
        else:
            data = process(service, response)
        return data
    except Exception as err:
        data = f'查询失败: 网络错误: {err}'
        return data

# txt2img
async def t2i(service, response):
    title = convert(service)
    font_size = 32
    text = response
    Txt2Img().set_font_size(font_size)
    pic = Txt2Img().draw(title, text)
    msg = MessageSegment.image(pic)
    return msg

# 绑定 UID
@bind_uid.handle()
async def bind_uid_func(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent], uid: Message = CommandArg()):
    if uid:
        try:
            if isinstance(event, GuildMessageEvent):
                await sql().adduid(event, uid)
                await bind_uid.send(f'已将 UID {uid} 绑定至 频道用户 {event.sender.nickname} 。')
            else:
                await sql().adduid(event, uid)
                await bind_uid.send(f'已将 UID {uid} 绑定至 QQ {event.user_id} 。')
        except Exception as err:
            await bind_uid.send(f'绑定失败。\n{err}')
    else: 
        await bind_uid.send('用法: /绑定 [玩家 UID]')

# 解绑 UID
@unbind_uid.handle()
async def unbind_uid_func(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent, GuildMessageEvent]):
    try:
        if isinstance(event, GuildMessageEvent):
            await sql().deluid(event)
            await unbind_uid.send(f'已将 频道用户 {event.user_id} 解绑。')
        else:
            await sql().deluid(event)
            await unbind_uid.send(f'已将 QQ {event.user_id} 解绑')
    except Exception as err:
        await unbind_uid.send(f'解绑失败。\n{err}')

# 数据库操作
class sql:

    # 连接数据库
    conn = sqlite3.connect(plugin_data_file)
    c = conn.cursor()

    # 启动时创建数据库
    async def on_start(self):
        self.c.execute('CREATE TABLE IF NOT EXISTS "ID" ("QQ" TEXT, "EA" TEXT, PRIMARY KEY ("QQ"))')
        self.c.execute('CREATE TABLE IF NOT EXISTS "SUB" ("ID" TEXT, "Guild_ID" TEXT, "Craft" INTEGER, "Map" INTEGER, "Bot_ID" TEXT NOT NULL, PRIMARY KEY ("ID"))')
        self.conn.commit()

    # 关闭时关闭数据库
    async def on_close(self):
        self.conn.close()

    # 添加绑定信息
    async def adduid(self, event, uid):
        self.c.execute(f'INSERT INTO "ID" ("QQ", "EA") VALUES ("{event.user_id}", "{uid}") ON CONFLICT ("QQ") DO UPDATE SET "EA" = "{uid}"')
        self.conn.commit()

    # 删除绑定信息
    async def deluid(self, event):
        self.c.execute(f'DELETE FROM "ID" WHERE "QQ" = "{event.user_id}"')
        self.conn.commit()

    # 添加订阅信息
    async def addsub(self, event, bot_id, service):
        if isinstance(event, GroupMessageEvent):
            if service == 'maprotation':
                self.c.execute(f'INSERT INTO "SUB" ("ID", "Map", "Bot_ID") VALUES ("{event.group_id}", "1", "{bot_id}") ON CONFLICT ("ID") DO UPDATE SET "Map" = 1')
            elif service == 'crafting':
                self.c.execute(f'INSERT INTO "SUB" ("ID", "Craft", "Bot_ID") VALUES ("{event.group_id}", "1", "{bot_id}") ON CONFLICT ("ID") DO UPDATE SET "Craft" = 1')
        elif isinstance(event, GuildMessageEvent):
            if service == 'maprotation':
                self.c.execute(f'INSERT INTO "SUB" ("ID", "Guild_ID", "Map", "Bot_ID") VALUES ("{event.channel_id}", "{event.guild_id}", "1", "{bot_id}") ON CONFLICT ("ID") DO UPDATE SET "Map" = 1')
            elif service == 'crafting':
                self.c.execute(f'INSERT INTO "SUB" ("ID", "Guild_ID", "Craft", "Bot_ID") VALUES ("{event.channel_id}", "{event.guild_id}", "1", "{bot_id}") ON CONFLICT ("ID") DO UPDATE SET "Craft" = 1')
        self.c.execute
        self.conn.commit()

    # 修改订阅信息
    async def delsub(self, event, service):
        if isinstance(event, GroupMessageEvent):
            if service == 'maprotation':
                self.c.execute(f'UPDATE "SUB" SET "Map" = 0 WHERE "ID" = "{event.group_id}"')
            elif service == 'crafting':
                self.c.execute(f'UPDATE "SUB" SET "Craft" = 0 WHERE "ID" = "{event.group_id}"')
        elif isinstance(event, GuildMessageEvent):
            if service == 'maprotation':
                self.c.execute(f'UPDATE "SUB" SET "Map" = 0 WHERE "ID" = "{event.channel_id}"')
            elif service == 'crafting':
                self.c.execute(f'UPDATE "SUB" SET "Craft" = 0 WHERE "ID" = "{event.channel_id}"')
        self.conn.commit()

    # 查询 UID
    async def check_uid(self, user_id):
        cursor = self.c.execute(f'SELECT "QQ", "EA" FROM "ID" WHERE "QQ" = "{user_id}"')
        return cursor.fetchone()[1]

    # 查询订阅信息
    async def get_sub(self):
        cursor = self.c.execute('SELECT * FROM "SUB"')
        return cursor.fetchall()

# 定时任务操作
class job:

    # 添加定时任务
    async def add(self, func, id, hour, bot_id, group_id = None, guild_id = None, channel_id = None):
        scheduler.add_job(func=func, trigger='cron', id=id, hour=hour, minute=1, kwargs={'bot_id': bot_id, 'group_id': group_id, 'guild_id': guild_id, 'channel_id': channel_id})

    # 删除定时任务
    async def remove(self, id):
        scheduler.remove_job(job_id=id)
    
    # 自动添加定时任务
    async def on_start(self):
        cursor = await sql().get_sub()
        for row in cursor:
            ID = row[0]
            Guild_ID = row[1]
            Craft = bool(row[2])
            Map = bool(row[3])
            Bot_ID = row[4]
            if Craft:
                if Guild_ID:
                    await job().add(func=subcraft, id=(ID + '_craft'), hour=2, bot_id=Bot_ID, guild_id=Guild_ID, channel_id=ID)
                elif not Guild_ID:
                    await job().add(func=subcraft, id=(ID + '_craft'), hour=2, bot_id=Bot_ID, group_id=ID)
            if Map:
                if Guild_ID:
                    await job().add(func=submap, id=(ID + '_map'), hour=None, bot_id=Bot_ID, guild_id=Guild_ID, channel_id=ID)
                elif not Guild_ID:
                    await job().add(func=submap, id=(ID + '_map'), hour=None, bot_id=Bot_ID, group_id=ID)

# 处理获取信息
def process(service, response):

    # 玩家数据
    if service == 'bridge':
        globals = response.json().get('global')
        realtime = response.json().get('realtime')
        data = (
            '玩家信息:\n'
            '名称: {}\n'
            'UID: {}\n'
            '平台: {}\n'
            '等级: {}\n'
            '距下一级百分比: {}%\n'
            '封禁状态: {}\n'
            '剩余秒数: {}\n'
            '最后封禁原因: {}\n'
            '大逃杀分数: {}\n'
            '大逃杀段位: {} {}\n'
            '大厅状态: {}\n'
            '在线: {}\n'
            '游戏中: {}\n'
            '可加入: {}\n'
            '群满员: {}\n'
            '已选传奇: {}\n'
            '当前状态: {}\n'
            '状态: {}'
            .format(
                globals.get('name'),
                globals.get('uid'),
                globals.get('platform'),
                globals.get('level'),
                globals.get('toNextLevelPercent'),
                convert(globals.get('bans').get('isActive')),
                globals.get('bans').get('remainingSeconds'),
                convert(globals.get('bans').get('last_banReason')),
                globals.get('rank').get('rankScore'),
                convert(globals.get('rank').get('rankName')),
                globals.get('rank').get('rankDiv'),
                convert(realtime.get('lobbyState')),
                convert(realtime.get('isOnline')),
                convert(realtime.get('isInGame')),
                convert(realtime.get('canJoin')),
                convert(realtime.get('partyFull')),
                convert(realtime.get('selectedLegend')),
                convert(realtime.get('currentState')),
                realtime.get('currentStateAsText')
            )
        )
        return data

    # 地图轮换数据
    elif service == 'maprotation':
        battle_royale = response.json().get('battle_royale')
        ranked = response.json().get('ranked')
        ltm = response.json().get('ltm')
        data = (
            '大逃杀:\n'
            '当前地图: {}\n'
            '下个地图: {}\n'
            '剩余时间: {}\n\n'
            '排位赛联盟:\n'
            '当前地图: {}\n'
            '下个地图: {}\n'
            '剩余时间: {}\n\n'
            '混录带:\n'
            '当前地图: {}\n'
            '下个地图: {}\n'
            '剩余时间: {}'
            .format(
                convert(battle_royale.get('current').get('map')),
                convert(battle_royale.get('next').get('map')),
                convert(battle_royale.get('current').get('remainingTimer')),
                convert(ranked.get('current').get('map')),
                convert(ranked.get('next').get('map')),
                convert(ranked.get('current').get('remainingTimer')),
                convert(ltm.get('current').get('map')),
                convert(ltm.get('next').get('map')),
                convert(ltm.get('current').get('remainingTimer'))
            )
        )
        return data

    # 顶尖猎杀者数据
    elif service == 'predator':
        rp = response.json().get('RP')
        data = (
            '大逃杀:\n'
            'PC 端:\n'
            '顶尖猎杀者人数: {}\n'
            '顶尖猎杀者分数: {}\n'
            '顶尖猎杀者UID: {}\n'
            '大师和顶尖猎杀者人数: {}\n'
            'PS4/5 端:\n'
            '顶尖猎杀者人数: {}\n'
            '顶尖猎杀者分数: {}\n'
            '顶尖猎杀者UID: {}\n'
            '大师和顶尖猎杀者人数: {}\n'
            'Xbox 端:\n'
            '顶尖猎杀者人数: {}\n'
            '顶尖猎杀者分数: {}\n'
            '顶尖猎杀者UID: {}\n'
            '大师和顶尖猎杀者人数: {}\n'
            'Switch 端:\n'
            '顶尖猎杀者人数: {}\n'
            '顶尖猎杀者分数: {}\n'
            '顶尖猎杀者UID: {}\n'
            '大师和顶尖猎杀者人数: {}'
            .format(
                rp.get('PC').get('foundRank'),
                rp.get('PC').get('val'),
                rp.get('PC').get('uid'),
                rp.get('PC').get('totalMastersAndPreds'),
                rp.get('PS4').get('foundRank'),
                rp.get('PS4').get('val'),
                rp.get('PS4').get('uid'),
                rp.get('PS4').get('totalMastersAndPreds'),
                rp.get('X1').get('foundRank'),
                rp.get('X1').get('val'),
                rp.get('X1').get('uid'),
                rp.get('X1').get('totalMastersAndPreds'),
                rp.get('SWITCH').get('foundRank'),
                rp.get('SWITCH').get('val'),
                rp.get('SWITCH').get('uid'),
                rp.get('SWITCH').get('totalMastersAndPreds'),
            )
        )
        return data

    # 制造数据
    elif service == 'crafting':
        data = (
            '每日制造:\n'
            '{} {} {} 点\n'
            '{} {} {} 点\n\n'
            '每周制造:\n'
            '{} {} {} 点\n'
            '{} {} {} 点\n\n'
            '赛季制造:\n'
            '{} {} {} 点\n'
            '{} {} {} 点'
            .format(
                convert(response.json()[0]['bundleContent'][0]['itemType']['name']),
                convert(response.json()[0]['bundleContent'][0]['itemType']['rarity']),
                convert(response.json()[0]['bundleContent'][0]['cost']),
                convert(response.json()[0]['bundleContent'][1]['itemType']['name']),
                convert(response.json()[0]['bundleContent'][1]['itemType']['rarity']),
                convert(response.json()[0]['bundleContent'][1]['cost']),
                convert(response.json()[1]['bundleContent'][0]['itemType']['name']),
                convert(response.json()[1]['bundleContent'][0]['itemType']['rarity']),
                convert(response.json()[1]['bundleContent'][0]['cost']),
                convert(response.json()[1]['bundleContent'][1]['itemType']['name']),
                convert(response.json()[1]['bundleContent'][1]['itemType']['rarity']),
                convert(response.json()[1]['bundleContent'][1]['cost']),
                convert(response.json()[2]['bundleContent'][0]['itemType']['name']),
                convert(response.json()[2]['bundleContent'][0]['itemType']['rarity']),
                convert(response.json()[2]['bundleContent'][0]['cost']),
                convert(response.json()[3]['bundleContent'][0]['itemType']['name']),
                convert(response.json()[3]['bundleContent'][0]['itemType']['rarity']),
                convert(response.json()[3]['bundleContent'][0]['cost'])
            )
        )
        return data
    
    # 服务器数据
    elif service == 'servers':
        data = (
            'Origin 登录:\n'
            '欧盟西部: {}\n'
            '欧盟东部: {}\n'
            '美国西部: {}\n'
            '美国中部: {}\n'
            '美国东部: {}\n'
            '南美洲: {}\n'
            '亚洲: {}\n\n'
            'EA 融合:\n'
            '欧盟西部: {}\n'
            '欧盟东部: {}\n'
            '美国西部: {}\n'
            '美国中部: {}\n'
            '美国东部: {}\n'
            '南美洲: {}\n'
            '亚洲: {}\n\n'
            'EA 账户:\n'
            '欧盟西部: {}\n'
            '欧盟东部: {}\n'
            '美国西部: {}\n'
            '美国中部: {}\n'
            '美国东部: {}\n'
            '南美洲: {}\n'
            '亚洲: {}\n\n'
            'Apex 跨平台验证:\n'
            '欧盟西部: {}\n'
            '欧盟东部: {}\n'
            '美国西部: {}\n'
            '美国中部: {}\n'
            '美国东部: {}\n'
            '南美洲: {}\n'
            '亚洲: {}\n\n'
            '自我核心测试:\n'
            '网站状态: {}\n'
            '统计 API: {}\n'
            '溢出 #1: {}\n'
            '溢出 #2: {}\n'
            'Origin API: {}\n'
            'Playstation API: {}\n'
            'Xbox API: {}\n\n'
            '其他平台:\n'
            'Playstation Network: {}\n'
            'Xbox Live: {}\n\n'
            'Data from apexlegendsstatus.com'
            .format(
                convert(response.json().get('Origin_login').get('EU-West').get('Status')),
                convert(response.json().get('Origin_login').get('EU-East').get('Status')),
                convert(response.json().get('Origin_login').get('US-West').get('Status')),
                convert(response.json().get('Origin_login').get('US-Central').get('Status')),
                convert(response.json().get('Origin_login').get('US-East').get('Status')),
                convert(response.json().get('Origin_login').get('SouthAmerica').get('Status')),
                convert(response.json().get('Origin_login').get('Asia').get('Status')),
                convert(response.json().get('EA_novafusion').get('EU-West').get('Status')),
                convert(response.json().get('EA_novafusion').get('EU-East').get('Status')),
                convert(response.json().get('EA_novafusion').get('US-West').get('Status')),
                convert(response.json().get('EA_novafusion').get('US-Central').get('Status')),
                convert(response.json().get('EA_novafusion').get('US-East').get('Status')),
                convert(response.json().get('EA_novafusion').get('SouthAmerica').get('Status')),
                convert(response.json().get('EA_novafusion').get('Asia').get('Status')),
                convert(response.json().get('EA_accounts').get('EU-West').get('Status')),
                convert(response.json().get('EA_accounts').get('EU-East').get('Status')),
                convert(response.json().get('EA_accounts').get('US-West').get('Status')),
                convert(response.json().get('EA_accounts').get('US-Central').get('Status')),
                convert(response.json().get('EA_accounts').get('US-East').get('Status')),
                convert(response.json().get('EA_accounts').get('SouthAmerica').get('Status')),
                convert(response.json().get('EA_accounts').get('Asia').get('Status')),
                convert(response.json().get('ApexOauth_Crossplay').get('EU-West').get('Status')),
                convert(response.json().get('ApexOauth_Crossplay').get('EU-East').get('Status')),
                convert(response.json().get('ApexOauth_Crossplay').get('US-West').get('Status')),
                convert(response.json().get('ApexOauth_Crossplay').get('US-Central').get('Status')),
                convert(response.json().get('ApexOauth_Crossplay').get('US-East').get('Status')),
                convert(response.json().get('ApexOauth_Crossplay').get('SouthAmerica').get('Status')),
                convert(response.json().get('ApexOauth_Crossplay').get('Asia').get('Status')),
                convert(response.json().get('selfCoreTest').get('Status-website').get('Status')),
                convert(response.json().get('selfCoreTest').get('Stats-API').get('Status')),
                convert(response.json().get('selfCoreTest').get('Overflow-#1').get('Status')),
                convert(response.json().get('selfCoreTest').get('Overflow-#2').get('Status')),
                convert(response.json().get('selfCoreTest').get('Origin-API').get('Status')),
                convert(response.json().get('selfCoreTest').get('Playstation-API').get('Status')),
                convert(response.json().get('selfCoreTest').get('Xbox-API').get('Status')),
                convert(response.json().get('otherPlatforms').get('Playstation-Network').get('Status')),
                convert(response.json().get('otherPlatforms').get('Xbox-Live').get('Status'))
            )
        )
        return data

# 请求内容转换
def convert(name):
    names = {
        # Map
        'Kings Canyon': '诸王峡谷',
        'World\'s Edge': '世界尽头',
        'Olympus': '奥林匹斯',
        'Storm Point': '风暴点',
        'Broken Moon': '残月',
        'Encore': '再来一次',
        'Habitat': '栖息地 4',
        'Overflow': '熔岩流',
        'Phase runner': '相位穿梭器',
        'Party crasher': '派对破坏者',
        'Drop Off': '原料场',
        'Skulltown': '骷髅镇',
        'Barometer': '气压计',
        'Wall': '高墙',
        'Siphon': '岩浆汲取器',
        'Fragment': '碎片东部',
        'Unknown': '未知',
        'None': '无',
        # Barrels
        'barrel_stabilizer': '枪管稳定器',
        'laser_sight': '激光瞄准镜',
        # Mags
        'extended_energy_mag': '加长式能量弹匣',
        'extended_heavy_mag': '加长式重型弹匣',
        'extended_light_mag': '加长式轻型弹匣',
        'extended_sniper_mag': '加长狙击弹匣',
        'shotgun_bolt': '霰弹枪枪栓',
        # Optics
        'optic_hcog_classic': '单倍全息衍射式瞄准镜"经典"',
        'optic_holo': '单倍幻影',
        'optic_variable_holo': '单倍至 2 倍可调节式幻影瞄准镜',
        'optic_hcog_bruiser': '2 倍全息衍射式瞄准镜"格斗家"',
        'optic_sniper': '6 倍狙击手',
        'optic_variable_aog': '2 倍至 4 倍可调节式高级光学瞄准镜',
        'optic_hcog_ranger': '3 倍全息衍射式瞄准镜"游侠"',
        'optic_variable_sniper': '4 倍至 8 倍可调节式狙击手',
        'optic_digital_threat': '单倍数字化威胁',
        'optic_digital_sniper_threat': '4 倍至 10 倍数字化狙击威胁',
        # Hop_Ups
        'anvil_receiver': '铁砧接收器',
        'double_tap_trigger': '双发扳机',
        'skullpiercer_rifling': '穿颅器',
        'turbocharger': '涡轮增压器',
        # Stocks
        'standard_stock': '标准枪托',
        'sniper_stock': '狙击枪枪托',
        # Gear
        'helmet': '头盔',
        'evo_shield': '进化护盾',
        'knockdown_shield': '击倒护盾',
        'backpack': '背包',
        'survival': '隔热板',
        'mobile_respawn_beacon': '移动重生信标',
        # Regen
        'shield_cell': '小型护盾电池',
        'syringe': '注射器',
        'large_shield_cell': '护盾电池',
        'med_kit': '医疗箱',
        'phoenix_kit': '凤凰治疗包',
        'ultimate_accelerant': '绝招加速剂',
        # Ammo
        'special': '特殊弹药',
        'energy': '能量弹药',
        'heavy': '重型弹药',
        'light': '轻型弹药',
        'shotgun': '霰弹枪弹药',
        'sniper': '狙击弹药',
        # Other
        'evo_points': '进化点数',
        'Rare': '稀有',
        'Epic': '史诗',
        # Rank
        'Unranked': '菜鸟',
        'Bronze': '青铜',
        'Silver': '白银',
        'Gold': '黄金',
        'Platinum': '白金',
        'Diamond': '钻石',
        'Master': '大师',
        'Apex Predator': 'Apex 猎杀者',
        # Legends
        'Bloodhound': '寻血猎犬',
        'Gibraltar': '直布罗陀',
        'Lifeline': '命脉',
        'Pathfinder': '探路者',
        'Wraith': '恶灵',
        'Bangalore': '班加罗尔',
        'Caustic': '侵蚀',
        'Mirage': '幻象',
        'Octane': '动力小子',
        'Wattson': '沃特森',
        'Crypto': '密客',
        'Revenant': '亡灵',
        'Loba': '罗芭',
        'Rampart': '兰伯特',
        'Horizon': '地平线',
        'Fuse': '暴雷',
        'Valkyrie': '瓦尔基里',
        'Seer': '希尔',
        'Ash': '艾许',
        'Mad Maggie': '疯玛吉',
        'Newcastle': '纽卡斯尔',
        'Vantage': '万蒂奇',
        'Catalyst': '卡特莉丝',
        # Level
        'Common': '等级1',
        'Rare': '等级2',
        'Epic': '等级3',
        'Legendary': '等级4',
        'Mythic': '等级5',
        # Weapon
        'peacekeeper': '和平捍卫者',
        'spitfire': '喷火轻机枪',
        'longbow': '长弓',
        'volt': '电能冲锋枪',
        'havoc': '哈沃克步枪',
        'flatline': '平行步枪',
        'hemlok': '赫姆洛克突击步枪',
        'r-301': 'R-301 卡宾枪',
        'alternator': '转换者冲锋枪',
        'prowler': '猎兽冲锋枪',
        'r-99': 'R-99 冲锋枪',
        'car': 'CAR',
        'devotion': '专注轻机枪',
        'l-star': 'L-STAR 能量机枪',
        'rampage': '暴走',
        'g7-scout': 'G7 侦察枪',
        'triple-take': '三重式狙击枪',
        'repeater': '30-30',
        'bow': '波塞克',
        'charge-rifle': '充能步枪',
        'kraber': '克雷贝尔狙击枪',
        'sentinel': '哨兵狙击步枪',
        'eva': 'EVA-8',
        'mastiff': '敖犬霰弹枪',
        'mozambique': '莫桑比克',
        're-45': 'RE-45 自动手枪',
        'p2020': 'P2020 手枪',
        'wingman': '辅助手枪',
        # API
        'offline': '离线',
        'online': '在线',
        0: '否',
        1: '是',
        'invite': '邀请',
        'open': '打开',
        'inLobby': '在大厅',
        'inMatch': '比赛中',
        'true': '是',
        'false': '否',
        'COMPETITIVE_DODGE_COOLDOWN': '竞技逃跑冷却',
        'None': '无',
        'EU-West': '欧盟西部',
        'EU-East': '欧盟东部',
        'US-West': '美国西部',
        'US-Central': '美国中部',
        'US-East': '美国东部',
        'SouthAmerica': '南美洲',
        'Asia': '亚洲',
        'Status-website': '网站状态',
        'Stats-API': '统计 API',
        'Overflow-#1': '溢出 #1',
        'Overflow-#2': '溢出 #2',
        'Origin-API': 'Origin API',
        'Playstation-API': 'Playstation API',
        'Xbox-API': 'Xbox API',
        'Playstation-Network': 'Playstation Network',
        'Xbox-Live': 'Xbox Live',
        'UP': '在线',
        'DOWN': '离线',
        'SLOW': '缓慢',
        'OVERLOADED': '过载',
        # Plugin
        'bridge': '玩家查询',
        'maprotation': '地图轮换',
        'predator': '顶尖猎杀者',
        'crafting': '制造轮换',
        'servers': '服务器状态'
    }
    return names.get(name, name)
