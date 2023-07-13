import os
import platform

from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .fetch_resources import download_database
from .permission_manager import pm
from .setu_message import HELP_MSG


class ManagerHandle:
    """
    这个类里面是一大堆setu其他指令的handle函数
    """

    @staticmethod
    def verify_sid(sid: str) -> bool:
        """验证会话sid是否合法"""
        try:
            stype, sid = sid.split("_")
            return bool(stype in ["group", "user"] and sid.isdigit())
        except Exception:
            return False

    async def open_setu(
        self, matcher: Matcher, event: MessageEvent, cmd: Message = CommandArg()
    ) -> None:
        """开启或关闭会话的setu功能"""
        # 获取命令后面的参数
        msg = cmd.extract_plain_text().strip()
        # 分析是新增还是删除
        if "add" in msg:
            add_mode = True
        elif "del" in msg:
            add_mode = False
        else:
            await matcher.finish(
                f"无效参数: {msg}, 请输入 add 或 del 为参数, eg: add group_114514"
            )

        if isinstance(event, GroupMessageEvent):
            sid = f"group_{str(event.group_id)}"
        else:
            sid = msg.replace("add", "").replace("del", "").strip()
            if not self.verify_sid(sid):
                await matcher.finish(f"无效目标对象: {sid}")
        await matcher.finish(pm.update_white_list(sid, add_mode))

    async def set_r18(
        self, matcher: Matcher, event: MessageEvent, cmd: Message = CommandArg()
    ) -> None:
        """开启或关闭会话的r18模式"""
        # 获取命令后面的参数
        msg = cmd.extract_plain_text().strip()
        # 分析是开启还是关闭
        if "on" in msg:
            r18mode = True
        elif "off" in msg:
            r18mode = False
        else:
            await matcher.finish(f"无效参数: {msg}, 请输入 on 或 off 为参数, eg: on group_114514")
        if isinstance(event, GroupMessageEvent):
            sid = f"group_{str(event.group_id)}"
        else:
            sid = msg.replace("on", "").replace("off", "").strip()
            if not self.verify_sid(sid):
                await matcher.finish(f"无效目标对象: {sid}")
        await matcher.finish(pm.update_r18(sid, r18mode))

    async def set_cd(
        self, matcher: Matcher, event: MessageEvent, cmd: Message = CommandArg()
    ) -> None:
        """获取setu的cd时间"""
        # 获取命令后面的参数
        msg = cmd.extract_plain_text().strip()
        if msg.isdigit() and isinstance(event, GroupMessageEvent):
            cd_time = int(msg)
            sid = f"group_{str(event.group_id)}"
            await matcher.finish(pm.update_cd(sid, cd_time))
        else:
            args = msg.split(" ")
            if len(args) != 2 or not args[0].isdigit() or not self.verify_sid(args[1]):
                await matcher.finish(
                    f"无效参数: {msg}, 请输入\n正整数或零 + 空格 + 会话类型_会话id\n为参数\n例如: 0 group_114514"
                )
            else:
                cd_time = int(args[0])
                sid = args[1]
                await matcher.finish(pm.update_cd(sid, cd_time))

    async def set_wd(
        self, matcher: Matcher, event: MessageEvent, cmd: Message = CommandArg()
    ) -> None:
        """获取setu的撤回时间"""
        # 获取命令后面的参数
        msg = cmd.extract_plain_text().strip()
        if msg.isdigit() and isinstance(event, GroupMessageEvent):
            wd_time = int(msg)
            sid = f"group_{str(event.group_id)}"
            await matcher.finish(pm.update_withdraw_time(sid, wd_time))
        else:
            args = msg.split(" ")
            if len(args) != 2 or not args[0].isdigit() or not self.verify_sid(args[1]):
                await matcher.finish(
                    f"无效参数: {msg}, 请输入\n正整数 + 空格 + 会话类型_会话id\n为参数\n例如: 100 group_114514"
                )
            else:
                wd_time = int(args[0])
                sid = args[1]
                await matcher.finish(pm.update_withdraw_time(sid, wd_time))

    async def set_maxnum(
        self, matcher: Matcher, event: MessageEvent, cmd: Message = CommandArg()
    ) -> None:
        """获取一次性setu的最大张数"""
        # 获取命令后面的参数
        msg = cmd.extract_plain_text().strip()
        if msg.isdigit() and isinstance(event, GroupMessageEvent):
            max_num = int(msg)
            sid = f"group_{str(event.group_id)}"
            await matcher.finish(pm.update_max_num(sid, max_num))
        else:
            args = msg.split(" ")
            if len(args) != 2 or not args[0].isdigit() or not self.verify_sid(args[1]):
                await matcher.finish(
                    f"无效参数: {msg}, 请输入\n正整数 + 空格 + 会话类型_会话id\n为参数\n例如: 10 group_114514"
                )
            else:
                max_num = int(args[0])
                sid = args[1]
                await matcher.finish(pm.update_max_num(sid, max_num))

    async def ban_setu(
        self, matcher: Matcher, event: MessageEvent, cmd: Message = CommandArg()
    ) -> None:
        """开启或关闭会话的setu功能"""
        # 获取命令后面的参数
        msg = cmd.extract_plain_text().strip()
        # 分析是新增还是删除
        if "add" in msg:
            add_mode = True
        elif "del" in msg:
            add_mode = False
        else:
            await matcher.finish(
                f"无效参数: {msg}, 请输入 add 或 del 为参数, eg: add group_114514"
            )

        if isinstance(event, GroupMessageEvent):
            sid = f"group_{str(event.group_id)}"
        else:
            sid = msg.replace("add", "").replace("del", "").strip()
            if not self.verify_sid(sid):
                await matcher.finish(f"无效目标对象: {sid}")
        await matcher.finish(pm.update_ban_list(sid, add_mode))

    @staticmethod
    async def setu_help(
        matcher: Matcher,
    ) -> None:
        """setu指令帮助"""
        await matcher.finish(HELP_MSG)

    @staticmethod
    async def setu_db(
        matcher: Matcher,
    ) -> None:
        """拉取数据库"""
        await matcher.send(
            "此功能由于大陆对github的半墙, 国内服务器可能造成数据丢失或无法写入等错误, 不确定性较大, 万一数据库丢失请重新clone"
        )
        try:
            remsg = await download_database()
        except Exception as e:
            remsg = f"获取 lolicon.db 失败: {repr(e)}"
        await matcher.finish(remsg)

    @staticmethod
    async def query_black_white_list(matcher: Matcher) -> None:
        """查新黑白名单"""
        res = pm.read_cfg()
        key_list = list(res.keys())  # 拿到所有的keys
        for element in ["ban", "last", "proxy"]:
            if element in key_list:
                key_list.remove(element)
        # 黑名单内容则在res['ban']
        await matcher.send(f"白名单: {key_list}\n\n黑名单: {res['ban']}")

    @staticmethod
    async def set_proxy(proxy) -> str:
        """设置代理并且ping"""
        pm.update_proxy(proxy)
        plat = platform.system().lower()  # 获取系统
        return (
            os.popen(f"ping {proxy}").read()
            if plat == "windows"
            else os.popen(f"ping -c 4 {proxy}").read()
        )

    async def replace_proxy_got(self, matcher: Matcher, event: MessageEvent) -> None:
        """没参数的情况下"""
        msg: str = str(event.get_message())  # 获取消息文本
        if not msg or msg.isspace():
            await matcher.finish("需要输入proxy")
        await matcher.send(f"{msg}已经替换, 正在尝试ping操作验证连通性")  # 发送消息
        result = await self.set_proxy(msg.strip())
        await matcher.send(f"{result}\n如果丢失的数据比较多, 请考虑重新更换代理")  # 发送消息

    async def replace_proxy(
        self, matcher: Matcher, arg: Message = CommandArg()
    ) -> None:
        """有参数的情况"""
        msg = arg.extract_plain_text().strip()  # 获取消息文本
        if not msg or msg.isspace():
            await matcher.pause(
                f"请输入你要替换的proxy, 当前proxy为:{pm.read_proxy()}\ntips: 一些也许可用的proxy\ni.pixiv.re\nsex.nyan.xyz\npx2.rainchan.win\npximg.moonchan.xyz\npiv.deception.world\npx3.rainchan.win\npx.s.rainchan.win\npixiv.yuki.sh\npixiv.kagarise.workers.dev\nsetu.woshishaluan.top\npixiv.a-f.workers.dev\n等等....\n\neg:px2.rainchan.win\n警告:不要尝试命令行注入其他花里胡哨的东西, 可能会损伤你的电脑"
            )
        else:
            await matcher.send(f"{msg}已经替换, 正在尝试ping操作验证连通性")  # 发送消息
            result = await self.set_proxy(msg)
            await matcher.finish(f"{result}\n如果丢失的数据比较多, 请考虑重新更换代理")  # 发送消息


manager_handle = ManagerHandle()
