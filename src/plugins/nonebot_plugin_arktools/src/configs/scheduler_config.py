"""定时任务设置"""
from pydantic import BaseModel, Extra


class SchedulerConfig(BaseModel, extra=Extra.ignore):
    """定时任务相关配置"""
    announce_push_switch: bool = False  # 自动获取 & 推送舟舟最新公告开关
    announce_push_interval: int = 1  # 间隔多少分钟运行一次

    sanity_notify_switch: bool = False  # 检测理智提醒开关
    sanity_notify_interval: int = 10  # 间隔多少分钟运行一次

    arknights_update_check_switch: bool = True  # 检测更新开关

    maa_copilot_switch: bool = False  # 查询 MAA 作业站订阅内容开关
    maa_copilot_interval: int = 60  # 间隔多少分钟运行一次


__all__ = [
    "SchedulerConfig"
]
