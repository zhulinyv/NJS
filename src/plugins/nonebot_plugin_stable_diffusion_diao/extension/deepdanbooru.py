import aiohttp
import base64
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, ActionFailed, Bot
from nonebot.log import logger
from .translation import translate
from .safe_method import send_forward_msg, risk_control
from ..config import config

deepdanbooru = on_command(".gettag", aliases={"鉴赏", "查书", "分析"})


@deepdanbooru.handle()
async def deepdanbooru_handle(event: MessageEvent, bot: Bot):
    h_ = None
    url = ""
    reply = event.reply
    if reply:
        for seg in reply.message['image']:
            url = seg.data["url"]
    for seg in event.message['image']:
        url = seg.data["url"]
    if url:
        async with aiohttp.ClientSession() as session:
            logger.info(f"正在获取图片")
            async with session.get(url) as resp:
                bytes = await resp.read()
        str_img = str(base64.b64encode(bytes), "utf-8")
        message = ""
        start = "data:image/jpeg;base64,"
        str0 = start+str_img
        if config.novelai_tagger_site:
            site = config.novelai_tagger_site
            payload = {"image": str0, "model": "wd14-vit-v2-git", "threshold": 0.35 }
            async with aiohttp.ClientSession() as session:
                async with session.post(url=f"http://{site}/tagger/v1/interrogate", json=payload) as resp:
                    if resp.status not in [200, 201]:
                        resp_text = await resp.text()
                        logger.error(f"API失败，错误信息:{resp.status, resp_text}")
                        await deepdanbooru.finish(f"识别失败，错误代码为{resp.status}")
                    else:
                        resp_dict = await resp.json()
                        tags = resp_dict["caption"]
                        replace_list =  ["general", "sensitive", "questionable", "explicit"]
                        possibilities = {}
                        for i in replace_list:
                            possibilities[i]=tags[i]
                            del tags[i]
                        value = list(possibilities.values())
                        value.sort(reverse=True)
                        h_ = f"这张图涩度{value[0] * 100}%"
                        tags = ", ".join(list(tags.keys()))

        else:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://mayhug-rainchan-anime-image-label.hf.space/api/predict/', json={"data": [str0, 0.6,"ResNet101"]}) as resp:
                    if resp.status != 200:
                        await deepdanbooru.finish(f"识别失败，错误代码为{resp.status}")
                    jsonresult = await resp.json()
                    data = jsonresult['data'][0]
                logger.info(f"TAG查询完毕")
                tags = ""
                for label in data['confidences']:
                    tags = tags+label["label"]+","
        
        tags_ch = await translate(tags.replace("_", " "), "zh")
        message_list = [MessageSegment.image(bytes), tags, f"\n机翻结果:" + tags_ch]
        if h_:
            message_list = message_list + [h_]
        try: 
            await send_forward_msg(bot, 
                               event, 
                               event.sender.nickname, 
                               str(event.get_user_id()), 
                               message_list
                               )  
        except ActionFailed:
            message_list = message_list.pop(0)
            await risk_control(bot, event, message_list, False, True)
    else:
        await deepdanbooru.finish(f"未找到图片")
