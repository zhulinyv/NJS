import json
import os
import random
import time

import nonebot
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from .txt2img import txt_to_img


class Utils:
    def __init__(self) -> None:
        """读取配置, 可能有人要问了, 为什么要搞这么多个json, 因为我自己的bot上个数据有多个用户数据, 我懒得合并了"""
        self.data_path: str = "./data/impact"
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            self.userdata = {}
            self.write_user_data()
            self.userdata_new = {}
            self.write_user_data_new()
            self.ejaculation_data = {}
            self.write_ejaculation_data()
            self.groupdata = {}
            self.write_group_data()
        else:
            if os.path.exists(f"{self.data_path}/userdata.json"):  # 读取用户数据
                with open(
                    f"{self.data_path}/userdata.json", "r", encoding="utf-8"
                ) as f:
                    self.userdata = json.load(f)  # json结构 {"user_id":int}
            else:  # 不存在则创建
                self.userdata = {}
                self.write_user_data()
            if os.path.exists(f"{self.data_path}/userdata_new.json"):  # 读取用户数据
                with open(
                    f"{self.data_path}/userdata_new.json", "r", encoding="utf-8"
                ) as f:
                    self.userdata_new = json.load(f)  # json结构 {"user_id":int}
            else:  # 不存在则创建
                self.userdata_new = {}
                self.write_user_data_new()
            if os.path.exists(f"{self.data_path}/groupdata.json"):
                with open(
                    f"{self.data_path}/groupdata.json", "r", encoding="utf-8"
                ) as f:
                    self.groupdata = json.load(f)
            else:
                self.groupdata = {}
                self.write_group_data()  # json结构{"group_id": {"allow": true|false}}
            if os.path.exists(f"{self.data_path}/ejaculation_data.json"):  # 读取用户数据
                with open(
                    f"{self.data_path}/ejaculation_data.json", "r", encoding="utf-8"
                ) as f:
                    self.ejaculation_data = json.load(f)
            else:
                self.ejaculation_data = {}
                self.write_ejaculation_data()  # 这种结构, 不想重构也不想新建json了，所以放宽了这么多{"user_id": {"date": {"ejaculation": 123}}}
        self.usage = """指令1: 嗦牛子 (给目标牛牛增加长度, 自己或者他人, 通过艾特选择对象, 没有at时目标是自己)
指令2: 打胶 | 开导 (给自己牛牛增加长度)
指令3: 牛子pk | 牛子对决 (普通的pk,单纯的random实现输赢, 胜利方获取败方随机数/2的牛牛长度)
指令4: 牛子查询 (目标牛牛长度, 自己或者他人, 通过艾特选择对象, 没有at时目标是自己)
指令5: jj排行榜 | jj排名 | jj榜单 | jjrank (字面意思, 输出倒数五位和前五位, 以及自己的排名)
指令6: 开启淫趴|禁止淫趴 (由管理员 | 群主 | SUPERUSERS开启或者关闭淫趴)
指令7: 日群友|透群友|日群主|透群主|日管理|透管理 (字面意思, 当使用透群友的时候如果at了人那么直接指定)
指令8: 注入查询 | 摄入查询 (查询目标被透注入的量，后接(历史|全部), 可查看总被摄入的量, 无艾特的时候是自己, 有at的时候是目标)
指令9: 淫趴介绍 | 淫趴说明| 淫趴帮助 (输出淫趴插件的命令列表)

指令1: 扣 (给目标小学增加深度, 自己或者他人, 通过艾特选择对象, 没有at时目标是自己)
指令2: 扣扣 (给自己小学增加深度)
指令3:小学pk | 小学对决 (普通的pk,单纯的random实现输赢, 胜利方获取败方随机数/2的小学长度)
指令4: 小学查询 (目标小学长度, 自己或者他人, 通过艾特选择对象, 没有at时目标是自己)
指令5: xx排行榜 | xx排名 | xx榜单 | xxrank (字面意思, 输出倒数五位和前五位, 以及自己的排名)"""
        self.not_allow = '群内还未开启淫趴游戏, 请管理员或群主发送"开启淫趴", "禁止淫趴"以开启/关闭该功能'  # 未开启该功能的send信息
        self.jj_variable = ["牛子", "牛牛", "丁丁", "JJ"]  # JJ变量
        self.xx_variable = ["小学", "小雪", "穴穴", "BB"]
        self.cd_data = {}  # 冷却数据
        self.pk_cd_data = {}  # pk冷却数据
        self.suo_cd_data = {}  # 嗦牛子冷却数据
        self.ejaculation_cd = {}  # 射精CD
        config = nonebot.get_driver().config  # 获取配置
        self.dj_cd_time: int = getattr(config, "djcdtime", 10)  # 打胶冷却时间
        self.pk_cd_time: int = getattr(config, "pkcdtime", 10)  # pk冷却时间
        self.suo_cd_time: int = getattr(config, "suocdtime", 10)  # 嗦牛子冷却时间
        self.fuck_cd_time: int = getattr(config, "fuckcdtime", 10)  # 透群友冷却时间

    def write_group_data(self) -> None:
        """写入群配置"""
        with open(f"{self.data_path}/groupdata.json", "w", encoding="utf-8") as f:
            json.dump(self.groupdata, f, indent=4, ensure_ascii=False)

    def write_user_data(self) -> None:
        """写入用户数据"""
        with open(f"{self.data_path}/userdata.json", "w", encoding="utf-8") as f:
            json.dump(self.userdata, f, indent=4)

    def write_user_data_new(self) -> None:
        """写入用户数据"""
        with open(f"{self.data_path}/userdata_new.json", "w", encoding="utf-8") as f:
            json.dump(self.userdata_new, f, indent=4)

    def write_ejaculation_data(self) -> None:
        """写入注入数据"""
        with open(
            f"{self.data_path}/ejaculation_data.json", "w", encoding="utf-8"
        ) as f:
            json.dump(self.ejaculation_data, f, indent=4, ensure_ascii=False)

    @staticmethod
    async def rule(event: GroupMessageEvent) -> bool:
        """rule检查, 是否有at"""
        msg = event.get_message()
        return next(
            (msg_seg.data["qq"] != "all" for msg_seg in msg if msg_seg.type == "at"),
            False,
        )

    @staticmethod
    async def get_at(event: GroupMessageEvent) -> str:
        """获取at的qq号, 不存在则返回寄, 类型为str"""
        msg = event.get_message()
        return next(
            (
                "寄" if msg_seg.data["qq"] == "all" else str(msg_seg.data["qq"])
                for msg_seg in msg
                if msg_seg.type == "at"
            ),
            "寄",
        )

    async def cd_check(self, uid: str) -> bool:
        """冷却检查"""
        cd = (
            time.time() - self.cd_data[uid]
            if uid in self.cd_data
            else self.dj_cd_time + 1
        )
        return cd > self.dj_cd_time

    async def pkcd_check(self, uid: str) -> bool:
        """pk冷却检查"""
        cd = (
            time.time() - self.pk_cd_data[uid]
            if uid in self.pk_cd_data
            else self.pk_cd_time + 1
        )
        return cd > self.pk_cd_time

    async def suo_cd_check(self, uid: str) -> bool:
        """嗦牛子冷却检查"""
        cd = (
            time.time() - self.suo_cd_data[uid]
            if uid in self.suo_cd_data
            else self.suo_cd_time + 1
        )
        return cd > self.suo_cd_time

    async def fuck_cd_check(self, event: GroupMessageEvent) -> bool:
        """透群友检查"""
        uid = event.get_user_id()
        cd = (
            time.time() - self.ejaculation_cd[uid]
            if uid in self.ejaculation_cd
            else self.fuck_cd_time + 1
        )
        return (
            cd > self.fuck_cd_time
            or event.get_user_id() in nonebot.get_driver().config.superusers
        )

    async def check_group_allow(self, gid: str) -> bool:
        """检查群是否允许"""
        return self.groupdata[gid]["allow"] if gid in self.groupdata else False

    @staticmethod
    def get_today() -> str:
        """获取当前年月日  2023-02-04"""
        return time.strftime("%Y-%m-%d", time.localtime())

    async def update_ejaculation(self, ejaculation: float, lucky_user: str) -> None:
        """更新ejaculation_data数据并且写入json"""
        if lucky_user in self.ejaculation_data:
            target_dict: dict = self.ejaculation_data[lucky_user]
            target_dict[self.get_today()] = {"ejaculation": ejaculation}
            self.ejaculation_data.update({lucky_user: target_dict})
        else:
            target_dict = {lucky_user: {self.get_today(): {"ejaculation": ejaculation}}}
            self.ejaculation_data.update(target_dict)
        self.write_ejaculation_data()

    def get_today_ejaculation(self, user_id: str) -> float:
        """获取当日注入的量"""
        try:
            return self.ejaculation_data[user_id][self.get_today()]["ejaculation"]
        except Exception:
            return 0

    @staticmethod
    def get_random_num() -> float:
        """获取随机数 0.1的概率是1-2随机获取, 剩下0.9是0-1"""
        rand_num = random.random()
        rand_num = random.uniform(0, 1) if rand_num > 0.1 else random.uniform(1, 2)
        return round(rand_num, 3)

    @staticmethod
    async def get_user_card(bot: Bot, group_id: int, qid: int) -> str:
        """返还用户nickname"""
        user_info: dict = await bot.get_group_member_info(
            group_id=group_id, user_id=qid
        )
        return user_info["card"] or user_info["nickname"]

    async def plugin_usage(self) -> bytes:
        return await txt_to_img.txt_to_img(self.usage)


utils = Utils()
