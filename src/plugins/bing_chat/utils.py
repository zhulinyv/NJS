from typing import Any, Dict

from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .utils import utils


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
