from nonebot import on_regex
from nonebot.params import RegexGroup

from langdetect import detect
from langdetect import DetectorFactory
DetectorFactory.seed = 0

from .translation import translate


fanyi = on_regex(r"^(翻译|(.)译(.))\s*([\s\S]*)?", priority=50, block=True)

@fanyi.handle()
async def _(matchgroup=RegexGroup()):
    # txt_msg = msg.extract_plain_text()
    # en = await translate(txt_msg, "en")
    # await risk_control(bot=bot, event=event, message=[en])
    # print(">>>>>", repr(matchgroup), matchgroup)

    text = matchgroup[3]
    if not text:
        await fanyi.finish("翻译/x译x [内容]\n直接翻译是自动识别，x是指定语言\nx支持：中（简中）、繁（繁中）、英、日、韩、法、俄、德", at_sender=True)

    lang = {
        "中": "zh-CN",
        "繁": "zh-TW",
        "英": "en",
        "日": "ja",
        "韩": "ko",
        "法": "fr",
        "俄": "ru",
        "德": "de",
    }

    if matchgroup[0] == "翻译":
        from_lang = detect(text)
        if from_lang == "zh-cn":
            new_text = await translate("zh", text, "en")
        else:
            new_text = await translate(from_lang, text, "zh")
    else:
        try:
            from_ = lang[matchgroup[1]]
            to_ = lang[matchgroup[2]]
            new_text = await translate(from_, text, to_)
        except KeyError:
            await fanyi.finish("不支持该语种", at_sender=True)
    await fanyi.finish(new_text, at_sender=True)