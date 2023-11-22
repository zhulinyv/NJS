from nonebot import on_message, Bot
from nonebot.params import Event

from nonebot_plugin_saa_cx import MessageFactory, Text
from ..type_store import common_config
from ..type_store.msgs_link import msg_links
from ..utils.extractor import extract_image, QCU

chat_consumer = on_message(block=False)


@chat_consumer.handle()
async def __(q_c: QCU, event: Event, bot: Bot):
    question, chat, user = q_c
    toev_receipt = None
    receipt = None
    if not chat.able:
        await MessageFactory(Text("该会话的模型引擎已被禁用,目前无法使用.")).finish(at_sender=True)

    if not question.replace(" ", "").replace("\n", ""):
        receipt = await MessageFactory(Text("你没有输入问题,请重新询问并在命令后或回复中加上问题.")).finish(
            at_sender=True
        )

    if len(question) < 7 and question.replace(" ", "").replace("\n", "").replace(
        "\r", ""
    ) in ["刷新对话", "清除历史", "遗忘"]:
        if common_config().wait_msg_able:
            toev_receipt = await MessageFactory(Text("正在刷新,请稍等~~")).send(at_sender=True)
        try:
            await chat.refresh()
            receipt = await MessageFactory("刷新成功").send(at_sender=True)
            msg_links.add_msglink(user.user_id, receipt.message_id, chat)
        except Exception as e:
            if receipt:
                await receipt.revoke()
            receipt = await MessageFactory(Text(f"在刷新过程中出错: {str(e)[:200]}")).send(
                at_sender=True
            )
            msg_links.add_msglink(user.user_id, receipt.message_id, chat)
            raise e
    else:
        try:
            if common_config().wait_msg_able:
                toev_receipt = await MessageFactory(Text("正在思考,请稍等~~")).send(
                    at_sender=True
                )
            if chat.model == "Bing":
                image = await extract_image(event, bot)
                if chat.stream:
                    await chat.ask_stream(question, image=image)
                else:
                    await chat.ask_plain(question, image)
            else:
                if chat.stream:
                    await chat.ask_stream(question)
                else:
                    await chat.ask_plain(question)
        except Exception as e:
            if receipt:
                await receipt.revoke()
            receipt = await MessageFactory(Text(f"在聊天过程中出错: {str(e)[:200]}")).send(
                at_sender=True
            )
            msg_links.add_msglink(user.user_id, receipt.message_id, chat)
            raise e
    if toev_receipt:
        await toev_receipt.revoke()
