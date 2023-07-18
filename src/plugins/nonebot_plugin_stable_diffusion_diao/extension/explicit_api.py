from ..config import config, nickname
from ..utils.save import save_img
from ..utils import sendtosuperuser, pic_audit_standalone
from io import BytesIO
import base64
import aiohttp, aiofiles
import nonebot
import os
import urllib
import re
import qrcode
import time
import asyncio
from PIL import Image
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, GroupMessageEvent, ActionFailed, PrivateMessageEvent
from nonebot.log import logger
from ..config import config 


async def send_qr_code(bot, fifo, img_url):
    img_id = time.time()
    img = qrcode.make(img_url[0])
    file_name = f"qr_code_{img_id}.png"
    img.save(file_name)
    with open(file_name, 'rb') as f:
        bytes_img = f.read()
    await bot.send_group_msg(group_id=fifo.group_id, message=MessageSegment.image(bytes_img))
    os.remove(file_name)


async def check_safe_method(fifo, 
                            img_bytes, 
                            message: list, 
                            bot_id=None, 
                            save_img_=True, 
                            extra_lable="",
                            ) -> list:
    try:
        bot = nonebot.get_bot(bot_id)
    except:
        bot = nonebot.get_bot()
    raw_message = f"\n{nickname}已经"
    label = ""
    # 判读是否进行图片审核
    h = await config.get_value(fifo.group_id, "h")
    nsfw_count = 0
    for i in img_bytes:
        # try:
        if isinstance(fifo.event, PrivateMessageEvent):
            if config.novelai_SuperRes_generate:
                try:
                    from ..extension.sd_extra_api_func import super_res_api_func
                    resp_tuple = await super_res_api_func(i, 3)
                    i = resp_tuple[0]
                except:
                    logger.debug("超分API失效")
            if save_img_:
                await save_img(fifo, i, fifo.group_id)
            message.append(MessageSegment.image(i))
            return message
        if await config.get_value(fifo.group_id, "picaudit") in [1, 2, 4] or config.novelai_picaudit in [1, 2, 4]:
            try:
                label, h_value, fifo.audit_info = await check_safe(i, fifo)
            except RuntimeError as e:
                logger.error(f"NSFWAPI调用失败，错误代码为{e.args}")
                label = "unknown"
            if label in ["safe", "general", "sensitive"]:
                label = "_safe"
                if config.novelai_SuperRes_generate:
                    try:
                        from ..extension.sd_extra_api_func import super_res_api_func
                        resp_tuple = await super_res_api_func(i, 3)
                        for i in resp_tuple:
                            i = resp_tuple[0]
                    except:
                        pass
                message.append(MessageSegment.image(i))
            else:
                label = "_explicit"
                message.append(f"\n太涩了,让我先看, 这张图涩度{h_value:.1f}%")
                nsfw_count += 1
                htype = await config.get_value(fifo.group_id, "htype") or config.novelai_htype
                message_data = await sendtosuperuser(f"让我看看谁又画色图了{MessageSegment.image(i)}, 来自群{fifo.group_id}")
                message_id = message_data["message_id"]
                message_all = await bot.get_msg(message_id=message_id)
                url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                img_url = re.findall(url_regex, str(message_all["message"]))
                if htype in [1, 2]:
                    if htype == 1:
                        try:
                            await bot.send_private_msg(user_id=fifo.user_id, 
                                                       message=f"悄悄给你看哦{MessageSegment.image(i)}\n{fifo.img_hash}"
                                                       )
                        except ActionFailed:
                            await bot.send_group_msg(group_id=fifo.group_id, 
                                                     message=f"请先加机器人好友捏, 才能私聊要涩图捏\n{fifo.img_hash}"
                                                     )
                    elif htype == 2:
                        try:
                            await bot.send_group_msg(group_id=fifo.group_id, 
                                                     message=f"这是图片的url捏,{img_url[0]}\n{fifo.img_hash}"
                                                     )
                        except ActionFailed:
                            try:
                                await bot.send_private_msg(user_id=fifo.user_id, 
                                                           message=f"悄悄给你看哦{MessageSegment.image(i)}\n{fifo.img_hash}"
                                                           )
                            except ActionFailed:
                                try:
                                    await bot.send_group_msg(group_id=fifo.group_id, 
                                                             message=f"URL发送失败, 私聊消息发送失败, 请先加好友\n{fifo.img_hash}"
                                                             )
                                except ActionFailed:
                                    await send_qr_code(bot, fifo, img_url)
                elif htype == 3:
                    await send_qr_code(bot, fifo, img_url)
        else:
            if config.novelai_SuperRes_generate:
                try:
                    from ..extension.sd_extra_api_func import super_res_api_func
                    resp_tuple = await super_res_api_func(i, 3)
                    i = resp_tuple[0]
                except:
                    logger.debug("超分API失效")
            if save_img_:
                await save_img(fifo, i, fifo.group_id+extra_lable)
            message.append(MessageSegment.image(i))
            return message
        if save_img_:
            await save_img(fifo, i, fifo.group_id+extra_lable+label)
    if nsfw_count:
        message.append(f",有{nsfw_count}张图片太涩了，{raw_message}帮你吃掉了")
    return message


async def check_safe(img_bytes: BytesIO, fifo, is_check=False):

    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
}
    picaudit = await config.get_value(fifo.group_id, "picaudit")
    if picaudit == 2 or config.novelai_picaudit == 2:
        if os.path.isfile("rainchan-image-porn-detection/lite_model.tflite"):
            pass
        else:
            os.system("git lfs install && git clone https://huggingface.co/spaces/mayhug/rainchan-image-porn-detection")
        try:
            import tensorflow as tf
        except:
            os.system("pip install tensorflow==2.9")
            import tensorflow as tf
        from typing import IO
        from io import BytesIO

        def process_data(content, SIZE):
            img = tf.io.decode_jpeg(content, channels=3)
            img = tf.image.resize_with_pad(img, SIZE, SIZE, method="nearest")
            img = tf.image.resize(img, (SIZE, SIZE), method="nearest")
            img = img / 255
            return img

        def main(file: IO[bytes]):
            SIZE = 224
            inter = tf.lite.Interpreter("rainchan-image-porn-detection/lite_model.tflite", num_threads=12)
            inter.allocate_tensors()
            in_tensor, *_ = inter.get_input_details()
            out_tensor, *_ = inter.get_output_details()
            data = process_data(file.read(), SIZE)
            data = tf.expand_dims(data, 0)
            inter.set_tensor(in_tensor["index"], data)
            inter.invoke()
            result, *_ = inter.get_tensor(out_tensor["index"])
            safe, questionable, explicit = map(float, result)
            possibilities = {"safe": safe, "questionable": questionable, "explicit": explicit}
            logger.info(f"审核结果:{possibilities}")
            return possibilities

        file_obj = BytesIO(img_bytes)
        possibilities = await asyncio.get_event_loop().run_in_executor(None, main, file_obj)
        value = list(possibilities.values())
        value.sort(reverse=True)
        reverse_dict = {value: key for key, value in possibilities.items()}
        if is_check:
            return possibilities
        return reverse_dict[value[0]], value[0] * 100, ""
    
    elif picaudit == 4 or config.novelai_picaudit == 4:
        img_base64 = base64.b64encode(img_bytes).decode()
        possibilities, message = await pic_audit_standalone(img_base64, False, True)
        value = list(possibilities.values())
        value.sort(reverse=True)
        reverse_dict = {value: key for key, value in possibilities.items()}
        logger.info(message)
        if is_check:
            return possibilities
        return "explicit" if reverse_dict[value[0]] == "questionable" else reverse_dict[value[0]], value[0] * 100, message

    async def get_file_content_as_base64(path, urlencoded=False):
        # 不知道为啥, 不用这个函数处理的话API会报错图片格式不正确, 试过不少方法了,还是不行(
        """
        获取文件base64编码
        :param path: 文件路径
        :param urlencoded: 是否对结果进行urlencoded 
        :return: base64编码信息
        """
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf8")
            if urlencoded:
                content = urllib.parse.quote_plus(content)
        return content

    async def get_access_token():
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", 
                "client_id": config.novelai_pic_audit_api_key["API_KEY"], 
                "client_secret": config.novelai_pic_audit_api_key["SECRET_KEY"]}
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, params=params) as resp:
                json = await resp.json()
                return json["access_token"]

    async with aiofiles.open("image.jpg", "wb") as f:
        await f.write(img_bytes)
    base64_pic = await get_file_content_as_base64("image.jpg", True)
    payload = 'image=' + base64_pic
    token = await get_access_token()
    baidu_api = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined?access_token=" + token
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(baidu_api, data=payload) as resp:
            result = await resp.json()
            logger.info(f"审核结果:{result}")
            if is_check:
                return result
            if result['conclusionType'] == 1:
                return "safe", result['data'][0]['probability'] * 100, ""
            else:
                return "", result['data'][0]['probability'] * 100
            
