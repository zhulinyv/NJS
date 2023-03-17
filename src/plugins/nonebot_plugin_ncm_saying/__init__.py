import httpx
from nonebot import logger, on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

__help_version__ = '0.1.0'
__help_plugin_name__ = "网抑云"
__usage__ = """一开口就老网抑云了

指令：/网抑云|网易云热评：随机一条网易云热评"""

hitokoto_matcher = on_command("网抑云", aliases={"网易云热评"}, priority=60, block=True)

@hitokoto_matcher.handle()
async def hitokoto(matcher: Matcher, args: Message = CommandArg()):
    if args:
        return
    async with httpx.AsyncClient() as client:
        response = await client.get("https://v.api.aa1.cn/api/api-wenan-wangyiyunreping/index.php?aa1=json")
    if response.is_error:
        logger.error("获取网抑云失败")
        return
    data = response.json()
    await matcher.finish(data[0]["wangyiyunreping"])
