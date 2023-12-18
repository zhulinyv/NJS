import re
import random

import ujson as json

from io import BytesIO
from pathlib import Path
from loguru import logger
from typing import Any, Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont
from EdgeGPT import Chatbot, ConversationStyle

from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)

from .config import config



class NewBing:
    def __init__(self) -> None:
        """初始化newbing, 标记cookie是否有效, 以及是否私聊启用"""
        self.cookie_allow = bool(utils.bing_cookies)
        self.reply_private: bool = utils.reply_private
        self.style: Dict[str, ConversationStyle] = {
            "creative": ConversationStyle.creative,
            "balanced": ConversationStyle.balanced,
            "precise": ConversationStyle.precise,
        }

    @staticmethod
    async def reserve_bing(matcher: Matcher, event: MessageEvent) -> None:
        await utils.newbing_new_chat(event=event, matcher=matcher)
        await matcher.send("newbing会话已重置", at_sender=True)

    async def pretreatment(
        self, event: MessageEvent, matcher: Matcher, msg: str
    ) -> None:
        """稍微预处理一下"""
        uid: str = event.get_user_id()  # 获取用户id
        if not self.reply_private and isinstance(event, PrivateMessageEvent):
            await matcher.finish()  # 配置私聊不启用后，私聊信息直接结束处理
        if msg.isspace() or not msg:  # 如果消息为空或者全为空格, 则结束处理
            await matcher.finish()
        if not self.cookie_allow:
            await matcher.finish("cookie未设置, 无法访问")
        if msg in utils.nonsense:
            await matcher.finish(
                MessageSegment.text(await utils.rand_hello()), reply_message=True
            )
        if uid not in utils.bing_chat_dict:
            await utils.newbing_new_chat(event=event, matcher=matcher)
            await matcher.send(MessageSegment.text("newbing新会话已创建"), reply_message=True)
        if utils.bing_chat_dict[uid]["isRunning"]:
            await matcher.finish(
                MessageSegment.text("当前会话正在运行中, 请稍后再发起请求"), reply_message=True
            )
        utils.bing_chat_dict[uid]["isRunning"] = True

    async def bing_handle(
        self, matcher: Matcher, event: MessageEvent, args: Message = CommandArg()
    ) -> None:
        """newbing聊天的handle函数"""
        uid: str = event.get_user_id()  # 获取用户id
        msg: str = args.extract_plain_text()  # 获取消息

        await self.pretreatment(event=event, matcher=matcher, msg=msg)  # 预处理

        bot: Chatbot = utils.bing_chat_dict[uid]["chatbot"]  # 获取当前会话的Chatbot对象
        style: str = utils.bing_chat_dict[uid]["model"]  # 获取当前会话的对话样式

        try:  # 尝试获取bing的回复
            data: Dict[str, Any] = await bot.ask(
                prompt=msg, conversation_style=self.style[style], simplify_response=True
            )
        except Exception as e:  # 如果出现异常, 则返回异常信息, 并且将当前会话状态设置为未运行
            utils.bing_chat_dict[uid]["isRunning"] = False
            await matcher.finish(
                MessageSegment.text(f'askError: {repr(e)}多次askError请尝试"重置bing"'),
                reply_message=True,
            )

        utils.bing_chat_dict[uid]["isRunning"] = False  # 将当前会话状态设置为未运行
        utils.bing_chat_dict[uid]["sessions_number"] += 1  # 会话数+1
        if "text" not in data:
            await matcher.finish(
                MessageSegment.text("bing没有返回text, 请重试"), reply_message=True
            )
        current_conversation: int = utils.bing_chat_dict[uid]["sessions_number"]
        max_conversation: int = data["messages_left"] + current_conversation

        rep_message: str = await utils.bing_string_handle(data["text"])

        try:  # 尝试发送回复
            await matcher.send(
                MessageSegment.text(
                    f"{rep_message}\n\n当前{current_conversation} 共 {max_conversation}"
                ),
                reply_message=True,
            )
            if max_conversation <= current_conversation:
                await matcher.send(
                    MessageSegment.text("达到对话上限, 正帮你重置会话"), reply_message=True
                )
                try:
                    await utils.newbing_new_chat(event=event, matcher=matcher)
                except Exception:
                    return
        except Exception as e:  # 如果发送失败, 则尝试把文字写在图片上发送
            try:
                await matcher.send(
                    MessageSegment.text(f"文本消息可能被风控了\n错误信息:{repr(e)}\n这里咱尝试把文字写在图片上发送了")
                    + MessageSegment.image(await utils.text_to_img(rep_message)),
                    reply_message=True,
                )
            except Exception as eeee:  # 如果还是失败, 我也没辙了, 只能返回异常信息了
                await matcher.send(
                    MessageSegment.text(f"消息全被风控了, 这是捕获的异常: \n{repr(eeee)}"),
                    reply_message=True,
                )

# 实例化一个NewBing对象
newbing = NewBing()



class Utils:
    def __init__(self) -> None:
        """初始化"""
        self.reply_private: bool = config.ai_reply_private
        self.nonsense: Tuple = (
            "你好啊",
            "你好",
            "在吗",
            "在不在",
            "您好",
            "您好啊",
            "你好",
            "在",
        )
        # ==================================== bing工具属性 ====================================================
        # 会话字典，用于存储会话   {"user_id": {"chatbot": bot, "last_time": time, "model": "balanced", isRunning: bool}}
        self.bing_chat_dict: Dict = {}
        bing_cookies_files: List[Path] = [
            file
            for file in config.smart_reply_path.rglob("*.json")
            if file.stem.startswith("cookie")
        ]
        try:
            self.bing_cookies: List = [
                json.load(open(file, "r", encoding="utf-8"))
                for file in bing_cookies_files
            ]
            logger.success(f"bing_cookies读取, 初始化成功, 共{len(self.bing_cookies)}个cookies")
        except Exception as e:
            logger.error(f"读取bing cookies失败 error信息: {repr(e)}")
            self.bing_cookies: List = []

    async def newbing_new_chat(self, event: MessageEvent, matcher: Matcher) -> None:
        """重置会话"""
        current_time: int = event.time
        user_id: str = str(event.user_id)
        if user_id in self.bing_chat_dict:
            last_time: int = self.bing_chat_dict[user_id]["last_time"]
            if (current_time - last_time < config.newbing_cd_time) and (
                event.get_user_id() not in config.superusers
            ):  # 如果当前时间减去上一次时间小于CD时间, 直接返回 # type: ignore
                await matcher.finish(
                    MessageSegment.reply(event.message_id)
                    + MessageSegment.text(
                        f"非报错情况下每个会话需要{config.newbing_cd_time}秒才能新建哦, 当前还需要{config.newbing_cd_time - (current_time - last_time)}秒"
                    )
                )
        bot: Chatbot = await Chatbot.create(
            cookies=random.choice(self.bing_cookies), proxy=self.proxy
        )  # 随机选择一个cookies创建一个Chatbot
        self.bing_chat_dict[user_id] = {
            "chatbot": bot,
            "last_time": current_time,
            "model": config.newbing_style,
            "sessions_number": 0,
            "isRunning": False,
        }

    @staticmethod
    async def bing_string_handle(input_string: str) -> str:
        """处理一下bing返回的字符串"""
        return re.sub(r'\[\^(\d+)\^]',  r'[\1]', input_string)

    # ================================================================================================

    @staticmethod
    async def text_to_img(text: str) -> bytes:
        """将文字转换为图片"""
        return await txt_to_img.txt_to_img(text)

# 创建一个工具实例
utils = Utils()



class TxtToImg:
    def __init__(self) -> None:
        self.LINE_CHAR_COUNT = 30 * 2
        self.CHAR_SIZE = 30
        self.TABLE_WIDTH = 4

    async def line_break(self, line: str) -> str:
        """将一行文本按照指定宽度进行换行"""
        ret: str = ""
        width = 0
        for c in line:
            if len(c.encode("utf8")) == 3:  # 中文
                if self.LINE_CHAR_COUNT == width + 1:  # 剩余位置不够一个汉字
                    width = 2
                    ret += "\n" + c
                else:  # 中文宽度加2，注意换行边界
                    width += 2
                    ret += c
            elif c == "\n":
                width = 0
                ret += c
            elif c == "\t":
                space_c: int = (
                    self.TABLE_WIDTH - width % self.TABLE_WIDTH
                )  # 已有长度对TABLE_WIDTH取余
                ret += " " * space_c
                width += space_c
            else:
                width += 1
                ret += c
            if width >= self.LINE_CHAR_COUNT:
                ret += "\n"
                width = 0
        return ret if ret.endswith("\n") else ret + "\n"

    async def txt_to_img(
        self, text: str, font_size=30, font_path="simsun.ttc"
    ) -> bytes:
        """将文本转换为图片"""
        text = await self.line_break(text)
        d_font = ImageFont.truetype(font_path, font_size)
        lines: int = text.count("\n")
        image: Image.Image = Image.new(
            "L",
            (self.LINE_CHAR_COUNT * font_size // 2 + 50, font_size * lines + 50),
            "white",
        )
        draw_table = ImageDraw.Draw(im=image)
        draw_table.text(xy=(25, 25), text=text, fill="#000000", font=d_font, spacing=4)
        new_img: Image.Image = image.convert("RGB")
        img_byte = BytesIO()
        new_img.save(img_byte, format="PNG")
        return img_byte.getvalue()

# 创建一个实例
txt_to_img = TxtToImg()