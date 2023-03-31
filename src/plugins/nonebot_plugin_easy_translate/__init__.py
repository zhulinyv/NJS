from httpx import AsyncClient
from nonebot import on_regex
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11.event import (
    GroupMessageEvent,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata
from .config import pc, var

__plugin_meta__ = PluginMetadata(
    name="简单翻译插件",
    description="免key翻译，使用谷歌翻译",
    usage=f"""插件命令如下：
翻译/x译x  # 试试就知道怎么用了
""",
)


async def message_check(event: MessageEvent, bot: Bot) -> bool:
    if isinstance(event, PrivateMessageEvent):
        return True
    elif isinstance(event, GroupMessageEvent):
        return bot == var.handle_bot
    else:
        return False


fanyi = on_regex(r"^(翻译|(.)译(.))\s*([\s\S]*)?", rule=message_check)


@fanyi.handle()
async def handle_fanyi(matchgroup=RegexGroup()):
    in_ = matchgroup[3]
    if not in_:
        await fanyi.finish("翻译/x译x [内容]\n直接翻译是自动识别，x是指定语言\nx支持：中（简中）、繁（繁中）、英、日、韩、法、俄、德")

    dd = {
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
        from_ = "auto"
        to_ = "auto"
    else:
        try:
            from_ = dd[matchgroup[1]]
            to_ = dd[matchgroup[2]]
        except KeyError:
            await fanyi.finish("不支持该语种")

    data = {"data": [in_, from_, to_]}
    async with AsyncClient(verify=False, follow_redirects=True) as c:
        resp = await c.post(
            "https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", json=data
        )
        if resp.status_code != 200:
            await fanyi.finish(f"翻译接口调用失败\n错误代码{resp.status_code},{resp.text}")

        result = resp.json()
        result = result["data"][0]

    await fanyi.finish(result)

    # 有道 免key翻译
    # params = {"q": in_mess, "from": ff, "to": tt}
    # async with AsyncClient(
    #     verify=False,
    # ) as client:
    #     res = await client.get(f"https://aidemo.youdao.com/trans", params=params)
