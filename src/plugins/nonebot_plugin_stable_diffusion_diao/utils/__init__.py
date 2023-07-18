from io import BytesIO
from PIL import Image
import re
import aiohttp
import base64
import random
from nonebot import logger
from ..config import config


async def check_last_version(package: str):
    # 检查包的最新版本
    async with aiohttp.ClientSession() as session:
        async with session.get("https://pypi.org/simple/"+package) as resp:
            text = await resp.text()
            pattern = re.compile("-(\d.*?).tar.gz")
            pypiversion = re.findall(pattern, text)[-1]
    return pypiversion


async def compare_version(old: str, new: str):
    # 比较两个版本哪个最新
    oldlist = old.split(".")
    newlist = new.split(".")
    for i in range(len(oldlist)):
        if int(newlist[i]) > int(oldlist[i]):
            return True
    return False


async def sendtosuperuser(message):
    # 将消息发送给superuser
    from nonebot import get_bot, get_driver
    import asyncio
    superusers = get_driver().config.superusers
    bot = get_bot()
    for superuser in superusers:
        message_data = await bot.call_api('send_msg', **{
            'message': message,
            'user_id': superuser,
        })
        await asyncio.sleep(5)
        return message_data


async def png2jpg(raw: bytes):
    raw:BytesIO = BytesIO(base64.b64decode(raw))
    img_PIL = Image.open(raw).convert("RGB")
    image_new = BytesIO()
    img_PIL.save(image_new, format="JPEG", quality=95)
    image_new=image_new.getvalue()
    return image_new


async def unload_and_reload(backend_index: int=None, backend_site=None):
    if backend_index is not None and isinstance(backend_index, int):
        backend_site = config.backend_site_list[backend_index]
    async with aiohttp.ClientSession() as session:
        async with session.post(url=f"http://{backend_site}/sdapi/v1/unload-checkpoint") as resp:
            if resp.status not in [200, 201]:
                logger.error(f"释放模型失败，可能是webui版本太旧，未支持此API，错误:{await resp.text()}")
    async with aiohttp.ClientSession() as session:
        async with session.post(url=f"http://{backend_site}/sdapi/v1/reload-checkpoint") as resp:
            if resp.status not in [200, 201]:
                logger.error(f"重载模型失败，错误:{await resp.text()}")
            logger.info("重载模型成功")
            
            
async def pic_audit_standalone(img_base64, is_return_tags=False, audit=False):
    
    payload = {"image": img_base64, "model": "wd14-vit-v2-git", "threshold": 0.35 }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=f"http://{config.novelai_tagger_site}/tagger/v1/interrogate", json=payload) as resp:
            if resp.status not in [200, 201]:
                resp_text = await resp.text()
                logger.error(f"API失败，错误信息:{resp.status, resp_text}")
                return None
            else:
                resp_dict = await resp.json()
                tags = resp_dict["caption"]
                replace_list =  ["general", "sensitive", "questionable", "explicit"]
                to_user_list = ["这张图很安全!", "较为安全", "色情", "泰色辣!"]
                possibilities = {}
                to_user_dict = {}
                message = "这是审核结果:\n"
                for i, to_user in zip(replace_list, to_user_list):
                    possibilities[i]=tags[i]
                    percent = f":{tags[i]*100:.2f}".rjust(6)
                    message += f"[{to_user}{percent}%]\n"
                    to_user_dict[to_user] = tags[i]
                value = list(to_user_dict.values())
                value.sort(reverse=True)
                reverse_dict = {value: key for key, value in to_user_dict.items()}
                message += (f"最终结果为:{reverse_dict[value[0]].rjust(5)}")
    if is_return_tags:
        return message, tags
    if audit:
        return possibilities, message
    return message


def tags_to_list(tags: str) -> list:
    separators = ['，', '。', ","]
    for separator in separators:
        tags = tags.replace(separator, separators[0])
    tag_list = tags.split(separators[0])
    tag_list = [tag.strip() for tag in tag_list if tag.strip()]
    tag_list = list(filter(None, tag_list))
    return tag_list