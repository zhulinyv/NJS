"""非游戏数据，如用户理智恢复提醒的表"""
from tortoise import fields
from tortoise.models import Model


class UserSanityModel(Model):
    """理智提醒"""
    gid = fields.IntField(null=True)
    uid = fields.IntField(null=True)
    record_san = fields.IntField(null=True, default=0)
    notify_san = fields.IntField(null=True, default=135)
    record_time = fields.DatetimeField(null=True)
    notify_time = fields.DatetimeField(null=True)
    status = fields.BooleanField(null=True, default=False)

    class Meta:
        table = "uo_user_sanity"  # uo = UnOfficial


class RSSNewsModel(Model):
    """游戏公告"""
    time = fields.DatetimeField(null=True)
    title = fields.CharField(null=True, max_length=255)
    content = fields.TextField(null=True)
    link = fields.CharField(null=True, max_length=255)

    class Meta:
        table = "uo_rss_news"  # uo = UnOfficial


class MAACopilotSubsModel(Model):
    """抄作业"""
    sub_groups = fields.CharField(max_length=255)               # 哪些群
    sub_keyword = fields.CharField(max_length=255, null=True)   # 什么关键词
    latest_upload_time = fields.BigIntField(default=0)          # 最新上传时间

    latest_id = fields.BigIntField(default=0)                   # 作业编号
    operators = fields.JSONField(null=True)                     # 阵容(干员、技能)
    stage = fields.CharField(max_length=255, null=True)         # 关卡
    title = fields.CharField(max_length=255, null=True)         # 作业标题
    details = fields.CharField(max_length=255, null=True)       # 简介

    class Meta:
        table = "uo_maa_copilot_subs"  # uo = UnOfficial


PLUGIN_SQLITE_MODEL_MODULE_NAME = __name__


__all__ = [
    "UserSanityModel",
    "RSSNewsModel",
    "MAACopilotSubsModel",

    "PLUGIN_SQLITE_MODEL_MODULE_NAME"
]
