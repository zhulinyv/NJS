import json
import random
import time

from loguru import logger

from .config import DATA_PATH, config
from .setu_message import setu_sendcd

"""{
    'group_114':{
        'cd'       : 30,     # cd时长
        'r18'      : True,   # r18开关
        'withdraw' : 100,    # 撤回延时
        'maxnum'   : 10      # 单次最高张数
    },
    'last':{
        'user_1919' : 810    # 最近一次发送setu的时间
    },
    'ban':[
        'user_1919',         # 禁用的群组或用户，跨会话生效，会覆盖白名单设置
        'group_810'
    ],
    'proxy':'i.pixiv.re'  # 代理地址
}"""


class PermissionManager:
    def __init__(self) -> None:
        """初始化一些配置"""
        self.setu_perm_cfg_filepath = DATA_PATH / "setu_perm_cfg.json"
        self.setu_cd = config.setu_cd
        self.setu_withdraw_time = config.setu_withdraw_time
        self.setu_max_num = config.setu_max_num
        self.setu_disable_wlist = config.setu_disable_wlist
        self.setu_enable_private = config.setu_enable_private
        self.read_cfg()

    def read_cfg(self) -> dict:
        """读取配置文件"""
        try:
            # 尝试读取
            with open(self.setu_perm_cfg_filepath, "r", encoding="utf-8") as f:
                self.cfg: dict = json.loads(f.read())
        except Exception as e:
            # 读取失败
            logger.warning(f"setu_perm_cfg.json 读取失败, 尝试重建\n{repr(e)}")
            self.cfg = {"proxy": "i.pixiv.re"}
            self.write_cfg()
        return self.cfg

    def write_cfg(self):
        """写入配置文件"""
        with open(self.setu_perm_cfg_filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.cfg))

    # --------------- 文件读写 开始 ---------------

    # --------------- 查询系统 开始 ---------------
    def read_last_send(self, session_id: str) -> float:
        """查询最后一次发送时间"""
        try:
            return self.cfg["last"][session_id]
        except KeyError:
            return 0

    def read_cd(self, session_id: str) -> int:
        """查询cd"""
        try:
            return self.cfg[session_id]["cd"]
        except KeyError:
            return self.setu_cd

    def read_withdraw_time(self, session_id: str) -> int:
        """查询撤回时间"""
        try:
            return self.cfg[session_id]["withdraw"]
        except KeyError:
            return self.setu_withdraw_time

    def read_max_num(self, session_id: str) -> int:
        """查询最大张数"""
        try:
            return self.cfg[session_id]["maxnum"]
        except KeyError:
            return self.setu_max_num

    def read_r18(self, session_id: str) -> bool:
        """查询r18"""
        try:
            return self.cfg[session_id]["r18"]
        except KeyError:
            return False

    def read_ban_list(self, session_id: str) -> bool:
        """查询黑名单"""
        try:
            return session_id in self.cfg["ban"]
        except KeyError:
            return False

    # --------------- 查询系统 结束 ---------------

    # --------------- 逻辑判断 开始 ---------------
    def check_permission(
        self, session_id: str, r18flag: bool, num: int, user_type: str = "group"
    ):
        """查询权限, 并返回修正过的参数

        Args:
            sessionId (str): [会话信息]
            r18flag (bool): [是否开启r18]
            num (int): [需求张数]
            su (bool, optional): [是否为管理员]. Defaults to False.

        Raises:
            PermissionError: [未在白名单]
            PermissionError: [cd时间未到]

        Returns:
            [bool, int, int]: [r18是否启用, 图片张数, 撤回时间]
        """
        # 优先采用黑名单检查
        if self.read_ban_list(session_id):
            logger.warning(f"涩图功能对 {session_id} 禁用！")
            raise PermissionError(f"涩图功能对 {session_id} 禁用！")
        # 采用白名单检查, 如果白名单被禁用则跳过
        if (
            not self.setu_disable_wlist
            and (
                user_type == "group"
                or ((not self.setu_enable_private) and user_type == "private")
            )
            and session_id not in self.cfg.keys()
        ):
            logger.warning(f"涩图功能在 {session_id} 会话中未启用")
            raise PermissionError("涩图功能在此会话中未启用！")

        # 查询冷却时间
        tile_left = (
            self.read_cd(session_id) + self.read_last_send(session_id) - time.time()
        )
        if tile_left > 0:
            hours, minutes, seconds = 0, 0, 0
            if tile_left >= 60:
                minutes, seconds = divmod(tile_left, 60)
                hours, minutes = divmod(minutes, 60)
            else:
                seconds = tile_left
            cd_msg = f"{f'{str(round(hours))}小时' if hours else ''}{f'{str(round(minutes))}分钟' if minutes else ''}{f'{str(round(seconds, 3))}秒' if seconds else ''}"
            logger.warning(f"setu的cd还有{cd_msg}")
            raise PermissionError(f"{random.choice(setu_sendcd)} 你的CD还有{cd_msg}！")

        # 检查r18权限, 图片张数, 撤回时间
        r18 = bool(r18flag and self.read_r18(session_id))
        num_ = (
            num
            if num <= self.read_max_num(session_id)
            else self.read_max_num(session_id)
        )
        return r18, num_, self.read_withdraw_time(session_id)

    # --------------- 逻辑判断 结束 ---------------

    # --------------- 冷却更新 开始 ---------------
    def update_last_send(self, session_id: str):
        """更新最后一次发送时间"""
        try:
            self.cfg["last"][session_id] = time.time()
        except KeyError:
            self.cfg["last"] = {session_id: time.time()}

    # --------------- 冷却更新 结束 ---------------

    # --------------- 增删系统 开始 ---------------
    def update_white_list(self, session_id: str, add_mode: bool) -> str:
        """更新白名单"""
        if add_mode:
            if session_id in self.cfg.keys():
                return f"{session_id}已在白名单"
            self.cfg[session_id] = {}
            self.write_cfg()
            return f"成功添加{session_id}至白名单"
        # 移除出白名单
        else:
            if session_id in self.cfg.keys():
                self.cfg.pop(session_id)
                self.write_cfg()
                return f"成功移除{session_id}出白名单"
            return f"{session_id}不在白名单"

    def update_cd(self, session_id: str, cd_time: int) -> str:
        """更新cd时间"""
        # 检查是否已在白名单, 不在则结束
        if session_id not in self.cfg.keys():
            return f"{session_id}不在白名单, 请先添加至白名单后操作"
        # 检查数据是否超出范围，超出则设定至范围内
        cd_time = max(cd_time, 0)
        # 读取原有数据
        try:
            cd_time_old = self.cfg[session_id]["cd"]
        except Exception:
            cd_time_old = "未设定"
        # 写入新数据
        self.cfg[session_id]["cd"] = cd_time
        self.write_cfg()
        # 返回信息
        return f"成功更新冷却时间 {cd_time_old} -> {cd_time}"

    def update_withdraw_time(self, session_id: str, withdraw_time: int) -> str:
        """更新撤回时间"""
        # 检查是否已在白名单, 不在则结束
        if session_id not in self.cfg.keys():
            return f"{session_id}不在白名单, 请先添加至白名单后操作"
        # 检查数据是否超出范围，超出则设定至范围内
        withdraw_time = max(withdraw_time, 0)
        withdraw_time = min(withdraw_time, 100)
        # 读取原有数据
        try:
            withdraw_time_old = self.cfg[session_id]["withdraw"]
        except KeyError:
            withdraw_time_old = "未设定"
        # 写入新数据
        self.cfg[session_id]["withdraw"] = withdraw_time
        self.write_cfg()
        # 返回信息
        return f"成功更新撤回时间 {withdraw_time_old} -> {withdraw_time}"

    def update_max_num(self, session_id: str, max_num: int) -> str:
        """更新最大张数"""
        # 检查是否已在白名单, 不在则结束
        if session_id not in self.cfg.keys():
            return f"{session_id}不在白名单, 请先添加至白名单后操作"
        # 检查数据是否超出范围，超出则设定至范围内
        max_num = max(max_num, 1)
        max_num = min(max_num, 25)
        # 读取原有数据
        try:
            max_num_old = self.cfg[session_id]["maxnum"]
        except KeyError:
            max_num_old = "未设定"
        # 写入新数据
        self.cfg[session_id]["maxnum"] = max_num
        self.write_cfg()
        # 返回信息
        return f"成功更新最大张数 {max_num_old} -> {max_num}"

    def update_r18(self, session_id: str, r18_mode: bool) -> str:
        # sourcery skip: extract-duplicate-method
        """更新r18权限"""
        # 检查是否已在白名单, 不在则结束
        if session_id not in self.cfg.keys():
            return f"{session_id}不在白名单, 请先添加至白名单后操作"

        if r18_mode:
            if self.read_r18(session_id):
                return f"{session_id}已开启r18"
            self.cfg[session_id]["r18"] = True
            self.write_cfg()
            return f"成功开启{session_id}的r18权限"
        else:
            if self.read_r18(session_id):
                self.cfg[session_id]["r18"] = False
                self.write_cfg()
                return f"成功关闭{session_id}的r18权限"
            return f"{session_id}未开启r18"

    def update_ban_list(self, session_id: str, add_mode: bool) -> str:
        """更新黑名单"""
        if add_mode:
            try:
                if session_id in self.cfg["ban"]:
                    return f"{session_id}已在黑名单"
            except KeyError:
                self.cfg["ban"] = []
            self.cfg["ban"].append(session_id)
            self.write_cfg()
            return f"成功添加{session_id}至黑名单"
        # 移出黑名单
        else:
            try:
                self.cfg["ban"].remove(session_id)
                self.write_cfg()
                return f"成功移除{session_id}出黑名单"
            except ValueError:
                return f"{session_id}不在黑名单"

    def update_proxy(self, proxy: str) -> None:
        """更新代理"""
        self.cfg["proxy"] = proxy
        self.write_cfg()

    def read_proxy(self) -> str:
        """查询代理"""
        try:
            return self.cfg["proxy"]
        except KeyError:
            return "i.pixiv.re"

    # --------------- 增删系统 结束 ---------------


# 实例化权限管理
pm = PermissionManager()
