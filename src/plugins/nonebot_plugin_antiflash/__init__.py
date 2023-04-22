from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot import on_message, on_command
from nonebot.rule import Rule
from nonebot.matcher import Matcher
import re
from .config import handler

__anti_flash_vsrsion__ = "v0.2.3"
__anti_flash_notes__ = f'''
群聊反闪照 {__anti_flash_vsrsion__}
开启/启用/禁用反闪照
'''

async def _checker(event: GroupMessageEvent) -> bool:
    msg = str(event.get_message())
    return True if 'type=flash' in msg and handler.on else False

anti_flash_on = on_command(cmd="开启反闪照", aliases={"启用反闪照"}, permission=SUPERUSER | GROUP_ADMIN| GROUP_OWNER, priority=10, block=True)
anti_flash_off = on_command(cmd="禁用反闪照", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=10, block=True)

flashimg = on_message(priority=1, rule=Rule(_checker))
@flashimg.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    
    # 当前群聊开启
    if handler.check_permission(gid):
        msg = str(event.get_message())
        comment = re.compile(r'file=(.*?).image',re.S)
        comment1 = str(comment.findall(msg))
        reg = "[^0-9A-Za-z\u4e00-\u9fa5]"
        text = comment1
        x = str(re.sub(reg, '', text.upper()))
        id = event.get_user_id()
        url = ('https://gchat.qpic.cn/gchatpic_new/' + id + '/2640570090-2264725042-' + x.upper() + '/0?term=3')

        await flashimg.finish((MessageSegment.image(url)))

@anti_flash_on.handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    gid = str(event.group_id)
    
    if not handler.on:
       await matcher.finish("已全局禁用反闪照，需管理员权限可启用/禁用")
    
    handler.add_group(gid)
    await matcher.finish("当前群聊已启用反闪照")

@anti_flash_off.handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    gid = str(event.group_id)
    
    if not handler.on:
       await matcher.finish("已全局禁用反闪照，需管理员权限可启用/禁用")
    
    handler.remove_group(gid)
    await matcher.finish("当前群聊已禁用反闪照")