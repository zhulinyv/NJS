from typing import Union
from nonebot import on_command, logger
from nonebot.internal.params import Arg
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment
from .data_source import ocr, get_rare_operators, build_image, process_word_tags
from nonebot.exception import ActionFailed

recruit = on_command("公招", aliases={"方舟公招", "公开招募"}, priority=5, block=True)


@recruit.handle()
async def _(state: T_State, matcher: Matcher, event: GroupMessageEvent):
    if event.reply:
        event.message = event.reply.message

    if event.message.get("image", None):  # 自带图片
        logger.info("发送公招截图")
        for img in event.message["image"]:
            img_url = img.data.get("url", "")
            state["recruit"] = "image"
            matcher.set_arg("rec", img_url)

    elif event.message.extract_plain_text().strip().replace("公招", ""):  # 文字tag
        tags = event.message.extract_plain_text().strip()
        logger.info("直接输入文字标签")
        state["recruit"] = "str"
        matcher.set_arg("rec", tags)


@recruit.got(key="rec", prompt="请发送公招截图:")
async def _(state: T_State, rec: Union[Message, str] = Arg()):

    if state.get("recruit", None) == "str":  # 文字输入
        tags = set(await process_word_tags(rec.split()))
    else:
        if isinstance(rec, Message):
            img_url = rec["image"][0].data.get("url", "")
        else:
            img_url = rec
        await recruit.send("识别中...")
        tags = ocr(image_url=img_url)

    if not tags:
        await recruit.finish("没有检测到符合要求的公招标签！", at_sender=True)
    logger.info(f"tags: {tags}")
    await recruit.send(f"检测到的公招标签：{', '.join(list(tags))}")
    recruit_list = get_rare_operators(tags)
    if not recruit_list:
        await recruit.finish("没有必出稀有干员的标签组合哦！", at_sender=True)
    image = build_image(recruit_list)
    img = MessageSegment.image(image)
    try:
        await recruit.finish(Message(img))
    except ActionFailed as e:
        await recruit.finish(f"图片发送失败：{e}")
