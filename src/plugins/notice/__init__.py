
from nonebot.adapters.onebot.v11 import Event, Message, GroupUploadNoticeEvent, GroupDecreaseNoticeEvent, GroupAdminNoticeEvent
from nonebot.plugin import on_notice
from nonebot.rule import Rule
from nonebot import get_bot
import nonebot

from datetime import datetime


try:
    super_qq: str = list(nonebot.get_driver().config.superusers)[0]
except:
    super_qq: str = "123456789"
try:
    notice: list = nonebot.get_driver().config.notice
except:
    notice: list = []
try:
    bot = get_bot()
    bot_qq = int(bot.self_id)
except:
    bot_qq = 1255891784


# 群成员减少
async def _is_del_user(event: Event) -> bool:
    return isinstance(event, GroupDecreaseNoticeEvent)
# 获取文件上传
async def _is_checker(event: Event) -> bool:
    return isinstance(event, GroupUploadNoticeEvent)
# 管理员变动
async def _is_admin_change(event: Event) -> bool:
    return isinstance(event, GroupAdminNoticeEvent)

# 群员减少
del_user = on_notice(Rule(_is_del_user), priority=50, block=True)
# 群文件
files = on_notice(Rule(_is_checker), priority=50, block=True)
# 群管理
admin = on_notice(Rule(_is_admin_change), priority=50, block=True)


@del_user.handle()
async def send_rongyu(event: GroupDecreaseNoticeEvent):
    rely_msg = del_user_bey(event.time, event.user_id)
    await del_user.finish(message=Message(rely_msg))
@admin.handle()
async def send_rongyu(event: GroupAdminNoticeEvent):
    rely_msg = admin_change(event.sub_type, event.user_id)
    await admin.finish(message=Message(rely_msg))
@files.handle()
async def handle_first_receive(event: GroupUploadNoticeEvent):
    rely = f'[CQ:at,qq={event.user_id}]\n' \
           f'[CQ:image,file=https://q4.qlogo.cn/headimg_dl?dst_uin={event.user_id}&spec=640]' \
           f'\n 上传了新文件，群贡献值+1~[CQ:face,id=175]'
    await files.finish(message=Message(rely))


def admin_change(sub_type, user_id):
    admin_msg = ""
    if sub_type == "set":
        if user_id == bot_qq:
            admin_msg = f"芜湖，脑积水以后也是管理了~"
        else:
            admin_msg = f"[CQ:at,qq={user_id}]成为群管理~"
    elif sub_type == "unset":
        if user_id == bot_qq:
            admin_msg = f"呜呜，绿帽子没啦吖QwQ"
        else:
            admin_msg = f"[CQ:at,qq={user_id}]失去群管理~"
    return admin_msg

def del_user_bey(add_time, user_id):
    global del_user_msg
    del_time = datetime.fromtimestamp(add_time)
    if user_id in int(super_qq):
        del_user_msg = f"<{del_time}>@{user_id}主人离开啦，好伤心~"
    else:
        del_user_msg = f"<{del_time}>QQ号为：{user_id}的小可爱离开了我们，天下没有不散的筵席，有缘再见吖~" \
                       f"[CQ:image,file=https://q4.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=640]"
        return del_user_msg