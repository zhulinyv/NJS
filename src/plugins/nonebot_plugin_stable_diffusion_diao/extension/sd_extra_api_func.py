from typing import Tuple
from PIL import Image
from io import BytesIO
from argparse import Namespace
import json, aiohttp, time, base64
import base64
import time
import io
import re
import asyncio
import aiofiles
import datetime
import os
import traceback
import random

from ..config import config
from ..extension.translation import translate
from ..extension.explicit_api import check_safe_method
from .translation import translate
from ..backend import AIDRAW
from ..utils.data import lowQuality, basetag
from ..utils.load_balance import sd_LoadBalance
from .safe_method import send_forward_msg, risk_control
from ..extension.daylimit import count

from nonebot import on_command, on_shell_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment, ActionFailed, PrivateMessageEvent
from nonebot.params import CommandArg, Arg, ArgPlainText, ShellCommandArgs
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.permission import SUPERUSER
from nonebot import logger
from collections import Counter


async def func_init(event):
    '''
    获取当前群的后端设置
    '''
    global site, reverse_dict
    if isinstance(event, PrivateMessageEvent):
        site = config.novelai_site
    else:
        site = await config.get_value(event.group_id, "site") or config.novelai_site
    reverse_dict = {value: key for key, value in config.novelai_backend_url_dict.items()}
    return site, reverse_dict
    

header = {
    "content-type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54"
}

get_models = on_command(
    "模型目录",
    aliases={"获取模型", "查看模型", "模型列表"},
    priority=5,
    block=True
)

change_models = on_command("更换模型", priority=1, block=True)
control_net = on_command("以图绘图", aliases={"以图生图"})
control_net_list = on_command("controlnet", aliases={"控制网"})
super_res = on_command("图片修复", aliases={"图片超分", "超分"})
get_backend_status = on_command("后端", aliases={"查看后端"})
get_emb = on_command("emb", aliases={"embs"})
get_lora = on_command("lora", aliases={"loras"})
get_sampler = on_command("采样器", aliases={"获取采样器"})
translate_ = on_command("翻译")
hr_fix = on_command("高清修复") # 欸，还没写呢，就是玩
random_tags = on_command("随机tag")
find_pic = on_command("找图片")
word_frequency_count = on_command("词频统计", aliases={"tag统计"})

more_func_parser = ArgumentParser()
more_func_parser.add_argument("-i", "--index", type=int, help="设置索引", dest="index")
more_func_parser.add_argument("-v", "--value", type=str, help="设置值", dest="value")
more_func_parser.add_argument("-s", "--search", type=str, help="搜索设置名", dest="search")

set_sd_config = on_shell_command(
    "config",
    aliases={"设置"},
    parser=more_func_parser,
    priority=5
)


async def download_img(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            img_bytes = await resp.read()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            return img_base64, img_bytes


async def super_res_api_func(img_bytes, size: int = 0):
    '''
    sd超分extra API, size,1为
    '''
    upsale = None
    max_res = config.novelai_SuperRes_MaxPixels
    if size == 0:
        upsale = 2
    elif size == 1:
        upsale = 3
    new_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    old_res = new_img.width * new_img.height
    width = new_img.width
    height = new_img.height
    ai_draw_instance = AIDRAW()
    if old_res > pow(max_res, 2):
        new_width, new_height = ai_draw_instance.shape_set(width, height, max_res) # 借用一下shape_set函数
        new_img = new_img.resize((round(new_width), round(new_height)))
        msg = f"原图已经自动压缩至{int(new_width)}*{int(new_height)}"
    else:
        msg = ''

    img_bytes =  io.BytesIO()
    new_img.save(img_bytes, format="JPEG")
    img_bytes = img_bytes.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
# "data:image/jpeg;base64," + 
    payload = {"image": img_base64}
    payload.update(config.novelai_SuperRes_generate_payload)
    if upsale:
        payload["upscaling_resize"] = upsale
    resp_tuple = await sd_LoadBalance(task_type="txt2img")
    async with aiohttp.ClientSession() as session:
        api_url = "http://" + resp_tuple[1][0] + "/sdapi/v1/extra-single-image"
        async with session.post(url=api_url, json=payload) as resp:
            if resp.status not in [200, 201]:
                raise RuntimeError
            else:
                resp_json = await resp.json()
                resp_img = resp_json["image"]
                bytes_img = base64.b64decode(resp_img)
                return bytes_img, msg, resp.status


async def sd(backend_site_index):
    site = list(config.novelai_backend_url_dict.values())[int(backend_site_index)]
    dict_model = {}
    message = []
    message1 = []
    n = 1
    resp_ = await aiohttp_func("get", "http://"+site+"/sdapi/v1/options")
    currents_model = resp_[0]["sd_model_checkpoint"]
    message1.append("当前使用模型:" + currents_model + ",\t\n\n")
    models_info_dict = await aiohttp_func("get", "http://"+site+"/sdapi/v1/sd-models")
    for x in models_info_dict[0]:
        models_info_dict = x['title']
        dict_model[n] = models_info_dict
        num = str(n) + ". "
        message.append(num + models_info_dict + ",\t\n")
        n = n + 1
    message.append("总计%d个模型" % int(n - 1))
    message_all = message1 + message
    with open("data/novelai/models.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(dict_model, indent=4))
    return message_all


async def set_config(data, backend_site):
    payload = {"sd_model_checkpoint": data}
    url = "http://" + backend_site + "/sdapi/v1/options"
    resp_ = await aiohttp_func("post", url, payload)
    end = time.time()
    return resp_[1], end


async def extract_tags_from_file(file_path, get_full_content=True) -> str:
    separators = ['，', '。', ","]
    separator_pattern = '|'.join(map(re.escape, separators))
    async with aiofiles.open(file_path, 'r', encoding="utf-8") as file:
        content = await file.read()
        if get_full_content:
            return content
    lines = content.split('\n')  # 将内容按行分割成列表
    words = []
    for line in lines:
        if line.startswith('tags='):
            tags_list_ = line.split('tags=')[1].strip()
            words = re.split(separator_pattern, tags_list_.strip())
            words = [re.sub(r'\s+', ' ', word.strip()) for word in words if word.strip()]
            words += words
    return words


async def get_tags_list(is_uni=True):
    filenames = await get_all_filenames("data/novelai/output", ".txt")
    all_tags_list = []
    for path in list(filenames.values()):
        tags_list = await extract_tags_from_file(path, False)
        for tags in tags_list:
            all_tags_list.append(tags)
    if is_uni:
        unique_strings = []
        for string in all_tags_list:
            if string not in unique_strings and string != "":
                unique_strings.append(string)
        return unique_strings
    else:
        return all_tags_list


async def get_all_filenames(directory, fileType=None) -> dict:
    file_path_dict = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fileType and not file.endswith(fileType):
                continue
            filepath = os.path.join(root, file)
            file_path_dict[file] = filepath
    return file_path_dict


async def change_model(event: MessageEvent, 
                    bot: Bot,
                    model_index, 
                    backend_site_index
                    ):
    
    backend_site = list(config.novelai_backend_url_dict.values())[int(backend_site_index)]
    await func_init(event)
    try:
        site_ = reverse_dict[backend_site]
    except:
        site_ = await config(event.group_id, "site") or config.novelai_site
    try:
        site_index = list(config.novelai_backend_url_dict.keys()).index(site_)
    except:
        site_index = ""
    async with aiofiles.open("data/novelai/models.json", "r", encoding="utf-8") as f:
        content = await f.read()
        models_dict = json.loads(content)
    try:
        data = models_dict[model_index]
        await bot.send(event=event, message=f"收到指令，为后端{site_}更换模型中，后端索引-sd {site_index}，请等待,期间无法出图", at_sender=True)
        start = time.time()
        code, end = await set_config(data, backend_site)
        spend_time = end - start
        spend_time_msg = str(',更换模型共耗时%.3f秒' % spend_time)
        if code in [200, 201]:
            await bot.send(event=event, message="更换模型%s成功" % str(data) + spend_time_msg , at_sender=True) 
        else:
            await bot.send(event=event, message="更换模型失败，错误代码%s" % str(code), at_sender=True)
    except KeyError:
        await get_models.finish("输入错误,索引错误")


async def aiohttp_func(way, url, payload=""):
    
    if way == "post":
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=payload) as resp:
                resp_data = await resp.json()
                return resp_data, resp.status
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                resp_data = await resp.json()
                return resp_data, resp.status


@set_sd_config.handle()
async def _(event: MessageEvent, bot: Bot, args: Namespace = ShellCommandArgs()):
    await func_init(event)
    msg_list = ["Stable-Diffusion-WebUI设置\ntips: 可以使用 -s 来搜索设置项, 例如 设置 -s model\n"]
    n = 0
    get_config_site = "http://" + site + "/sdapi/v1/options"
    resp_dict = await aiohttp_func("get", get_config_site)
    index_list = list(resp_dict[0].keys())
    value_list = list(resp_dict[0].values())
    for i, v in zip(index_list, value_list):
        n += 1 
        if args.search:
            pattern = re.compile(f".*{args.search}.*", re.IGNORECASE)
            if pattern.match(i):
                msg_list.append(f"{n}.设置项: {i},设置值: {v}" + "\n")
        else:
            msg_list.append(f"{n}.设置项: {i},设置值: {v}" + "\n")
    if args.index == None and args.value == None:
        await risk_control(bot, event, msg_list, True)
    elif args.index == None:
        await set_sd_config.finish("你要设置啥啊!")
    elif args.value == None:
        await set_sd_config.finish("你的设置值捏?")
    else:
        payload = {
            index_list[args.index - 1]: args.value
        }
        try:
            await aiohttp_func("post", get_config_site, payload)
        except Exception as e:
            await set_sd_config.finish(f"出现错误,{str(e)}")
        else:
            await bot.send(event=event, message=f"设置完成{payload}")


@get_emb.handle()
async def _(event: MessageEvent, bot: Bot, msg: Message = CommandArg()):
    index = None
    text_msg = msg.extract_plain_text().strip()
    if msg:
        list_len = len(list(config.novelai_backend_url_dict.values()))
        try:
            int(text_msg)
        except:
            pass
        else:
            index = int(text_msg)
            if 0 <= index < list_len:
                pass
            else:
                index = None
    if index is not None and isinstance(index, int):
        site = list(config.novelai_backend_url_dict.values())[index]
        msg = None
    else:
         site, rev = await func_init(event)
    try:
        site_ = reverse_dict[site]
    except:
        site_ = await config.get_value(event.group_id, "site") or config.novelai_site
    embs_list = [f"这是来自webui:{site_}的embeddings,\t\n注:直接把emb加到tags里即可使用\t\n中文emb可以使用 -nt 来排除, 例如 -nt 雕雕\n"]
    n = 0
    emb_dict = {}
    get_emb_site = "http://" + site + "/sdapi/v1/embeddings"
    resp_json = await aiohttp_func("get", get_emb_site)
    all_embs = list(resp_json[0]["loaded"].keys())
    pattern = re.compile(f".*{text_msg}.*", re.IGNORECASE)
    for i in all_embs:
        n += 1
        emb_dict[n] = i
        if msg:
            if pattern.match(i):
                embs_list.append(f"{n}.{i}\t\n")
        else:
            embs_list.append(f"{n}.{i}\t\n")
    async with aiofiles.open("data/novelai/embs.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(emb_dict))
    await risk_control(bot, event, embs_list, True)


@get_lora.handle()
async def _(event: MessageEvent, bot: Bot, msg: Message = CommandArg()):
    index = None
    text_msg = msg.extract_plain_text().strip()
    try:
        site_ = reverse_dict[site]
    except:
        site_ = await config.get_value(event.group_id, "site") or config.novelai_site
    if msg:
        list_len = len(list(config.novelai_backend_url_dict.values()))
        try:
            int(text_msg)
        except:
            pass
        else:
            index = int(text_msg)
            if 0 <= index < list_len:
                pass
            else:
                index = None
    loras_list = [f"这是来自webui:{site_}的lora,\t\n注使用例<lora:xxx:0.8>\t\n或者可以使用 -lora 数字索引 , 例如 -lora 1\n"]
    n = 0
    lora_dict = {}
    if index is not None and isinstance(index, int):
        site = list(config.novelai_backend_url_dict.values())[index]
        msg = None
    else:
         site, rev = await func_init(event)
    get_lora_site = "http://" + site + "/sdapi/v1/loras"
    resp_json = await aiohttp_func("get", get_lora_site)
    pattern = re.compile(f".*{text_msg}.*", re.IGNORECASE)
    for item in resp_json[0]:
        i = item["name"]
        n += 1
        lora_dict[n] = i
        if msg:
            if pattern.match(i):
                loras_list.append(f"{n}.{i}\t\n")
        else:
            loras_list.append(f"{n}.{i}\t\n")
    async with aiofiles.open("data/novelai/loras.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(lora_dict))
    await risk_control(bot, event, loras_list, True)


@super_res.handle()
async def pic_fix(state: T_State, super_res: Message = CommandArg()):
    if super_res:
        state['super_res'] = super_res
    pass    


@super_res.got("super_res", "请发送你要修复的图片")
async def abc(event: MessageEvent, bot: Bot, msg: Message = Arg("super_res")):
    img_url_list = []
    img_base64_list = []

    if msg[0].type == "image":
        if len(msg) > 1:
            for i in msg:
                img_url_list.append(i.data["url"])
                upsale = 0
        else:
            img_url_list.append(msg[0].data["url"])
            upsale = 1
            
        for i in img_url_list:
            qq_img = await download_img(i)
            qq_img, text_msg, status_code = await super_res_api_func(qq_img[1], upsale)
            if status_code not in [200, 201]:
                await super_res.finish(f"出错了,错误代码{status_code},请检查服务器")
            img_base64_list.append(qq_img)
        if len(img_base64_list) == 1:
                img_mes = MessageSegment.image(img_base64_list[0])
                await bot.send(event=event, 
                               message=img_mes+text_msg, 
                               at_sender=True, 
                               reply_message=True
                               ) 
        else:
            img_list = []
            for i in img_base64_list:
                img_list.append(f"{MessageSegment.image(i)}\n{text_msg}")
            await send_forward_msg(bot, 
                                   event, 
                                   event.sender.nickname, 
                                   event.user_id, 
                                   img_list
                                   )
                                        
    else:
        await super_res.reject("请重新发送图片")


@control_net.handle()
async def c_net(state: T_State, net: Message = CommandArg()):
    if net:
        if len(net) > 1:
            state["tag"] = net
            state["net"] = net
        elif net[0].type == "image":
            state["net"] = net
            state["tag"] = net
    else:
        state["tag"] = net

@control_net.got('tag', "请输入绘画的关键词")
async def __():
    pass

@control_net.got("net", "你的图图呢？")
async def _(event: MessageEvent, bot: Bot, tag: str = ArgPlainText("tag"), msg: Message = Arg("net")):
    if config.novelai_daylimit and not await SUPERUSER(bot, event):
        left = await count(str(event.user_id), 2)
        if left == -1:
            await control_net.finish(f"今天你的次数不够了哦，明天再来找我玩吧")
    await func_init(event)
    start = time.time()
    tags_en = None
    reply= event.reply
    await bot.send(event=event, message=f"control_net以图生图中")
    if msg[0].type == "image":
            img_url = msg[0].data["url"]
    else:
        tag = msg[0].data["text"]
        img_url = msg[1].data["url"]
        tags_en = await translate(tag, "en")
    if tags_en is None:
        tags_en = ""
    if reply:
        for seg in reply.message['image']:
            img_url = seg.data["url"]
        for seg in event.message['image']:
            img_url = seg.data["url"]
    img = await download_img(img_url)
    img_bytes = base64.b64decode(img[0])
    tags = basetag + tags_en
    try:
        fifo = AIDRAW(user_id=str(event.user_id), 
                      tags=tags,
                      ntags=lowQuality,
                      event=event
                      )
        
        await fifo.load_balance_init()
        fifo.add_image(image=img_bytes, control_net=True)
        await fifo.post()
        processed_pic = fifo.result[0]
        message_ = await check_safe_method(fifo, [processed_pic], [""], None, True, "_controlnet")
    except Exception as e:
        logger.error(traceback.print_exc())
        await control_net.finish(f"出现错误{e}")
    if isinstance(message_[1], MessageSegment):
        message = MessageSegment.image(processed_pic) + f"\n耗时{fifo.spend_time}\n" + fifo.img_hash
        await bot.send(event=event, message=message)
    else:
        pass


@get_models.handle()
async def get_sd_models(event: MessageEvent, 
                        bot: Bot, 
                        msg: Message = CommandArg()
                    ):  
    if msg:
        backend_site_index = msg.extract_plain_text()
    else:
        backend_site_index = 0
    final_message = await sd(backend_site_index)
    await risk_control(bot, event, final_message, False, True)


@change_models.handle()
async def _(event: MessageEvent, 
            bot: Bot, 
            msg: Message = CommandArg()
):
    try:
        user_command = msg.extract_plain_text()
        backend_index = user_command.split("_")[0]
        index = user_command.split("_")[1]
    except:
        await get_models.finish("输入错误，请按照以下格式输入 更换模型1_2 (1为后端索引,从0开始，2为模型序号)")
    await change_model(event, bot, index, backend_index)


@get_sampler.handle()
async def _(event: MessageEvent, bot: Bot):
    await func_init(event)
    sampler_list = []
    url = "http://" + site + "/sdapi/v1/samplers"
    resp_ = await aiohttp_func("get", url)
    for i in resp_[0]:
        sampler = i["name"]
        sampler_list.append(f"{sampler}\t\n")
    await risk_control(bot, event, sampler_list)


@get_backend_status.handle()
async def _(event: MessageEvent, bot: Bot):
    async with aiofiles.open("data/novelai/load_balance.json", "r", encoding="utf-8") as f:
        content = await f.read()
        backend_info: dict = json.loads(content)
    backend_info_task_type = ["txt2img", "img2img", "controlnet"]
    n = -1
    backend_list = list(config.novelai_backend_url_dict.keys())
    backend_site = list(config.novelai_backend_url_dict.values())
    message = []
    task_list = []
    fifo = AIDRAW(event=event)
    all_tuple = await fifo.load_balance_init()
    for i in backend_site:
        task_list.append(fifo.get_webui_config(i))
    resp_config = await asyncio.gather(*task_list, return_exceptions=True)
    resp_tuple = all_tuple[1][2]
    today = str(datetime.date.today())
    for i, m in zip(resp_tuple, resp_config):
        work_history_list = []
        today_task = 0
        n += 1
        if isinstance(i, (aiohttp.ContentTypeError, 
                          TypeError,
                          asyncio.exceptions.TimeoutError,
                          Exception)
                          ):
            message.append(f"{n+1}.后端{backend_list[n]}掉线😭\t\n")
        else:
            if i[3] in [200, 201]:
                text_message = ''
                try:
                    model = m["sd_model_checkpoint"]
                except:
                    model = ""
                text_message += f"{n+1}.后端{backend_list[n]}正常,\t\n模型:{os.path.basename(model)}\n"
                if i[0]["progress"] in [0, 0.01, 0.0]:
                    text_message += f"后端空闲中\t\n"
                else:
                    eta = i[0]["eta_relative"]
                    text_message += f"后端繁忙捏,还需要{eta:.2f}秒完成任务\t\n"
                message.append(text_message)
            else:
                message.append(f"{n+1}.后端{backend_list[n]}掉线😭\t\n")
        for t in backend_info_task_type:
            history_list: list[dict] = backend_info[backend_site[n]][t]["info"]["history"]
            for task in history_list:
                work_history_list.append(list(task.keys()))
        today = str(datetime.date.today())
        for ts in work_history_list:
            if ts[0] == "null":
                continue
            if time.strftime("%Y-%m-%d", time.localtime(float(ts[0]))) == today:
                today_task += 1
        message.append(f"今日此后端已画{today_task}张图\t\n")

    await risk_control(bot, event, message, True)


@control_net_list.handle()
async def _(event: MessageEvent, bot: Bot, msg: Message = CommandArg()):
    await func_init(event)
    message_model = "可用的controlnet模型\t\n"
    message_module = "可用的controlnet模块\t\n"
    if msg:
        if msg[0].type == "image":
            img_url = msg[0].data["url"]
            img_tuple = await download_img(img_url)
            base64_img = img_tuple[0]
            payload = {"controlnet_input_images": [base64_img]}
            config.novelai_cndm.update(payload)
            resp_ = await aiohttp_func("post", "http://" + site + "/controlnet/detect", config.novelai_cndm)
            if resp_[1] == 404:
                await control_net_list.finish("出错了, 是不是没有安装controlnet插件捏?")
            image = resp_[0]["images"][0]
            image = base64.b64decode(image)
            await control_net_list.finish(message=MessageSegment.image(image))

    resp_1 = await aiohttp_func("get", "http://" + site + "/controlnet/model_list")
    resp_2 = await aiohttp_func("get", "http://" + site + "/controlnet/module_list")
    if resp_1[1] == 404:
        await control_net_list.finish("出错了, 是不是没有安装controlnet插件捏?")
    if resp_2[1] == 404:
        model_list = resp_1[0]["model_list"]
        for a in model_list:
            message_model += f"{a}\t\n"
        await bot.send(event=event, message=message_model)
        await control_net_list.finish("获取control模块失败, 可能是controlnet版本太老, 不支持获取模块列表捏")
    model_list = resp_1[0]["model_list"]
    module_list = resp_2[0]["module_list"]
    await risk_control(bot, event, model_list+module_list, True)


@translate_.handle()
async def _(event: MessageEvent, bot: Bot, msg: Message = CommandArg()):
    txt_msg = msg.extract_plain_text()
    en = await translate(txt_msg, "en")
    await risk_control(bot=bot, event=event, message=[en])


@random_tags.handle()
async def _(event: MessageEvent, bot: Bot, msg: Message = CommandArg()):
    all_tags_list = await get_tags_list()
    chose_tags_list = random.sample(all_tags_list, 12)
    chose_tags = ', '.join(chose_tags_list)

    fifo = AIDRAW(user_id=event.user_id, 
                  tags=chose_tags, 
                  ntags=lowQuality, 
                  event=event
                  )
    
    await risk_control(bot, event, [chose_tags], True)
    await fifo.load_balance_init()
    await fifo.post()
    if config.novelai_extra_pic_audit:
        message_ = await check_safe_method(fifo, [fifo.result[0]], [""], None, True, "_random_tags")
        if isinstance(message_[1], MessageSegment):
            await bot.send(event, 
                           message=MessageSegment.image(fifo.result[0])+fifo.img_hash,
                           at_sender=True, 
                           reply_message=True)
        else:
            pass
    else:
        await bot.send(event, 
                       message=MessageSegment.image(fifo.result[0])+fifo.img_hash,
                       at_sender=True, 
                       reply_message=True)


@find_pic.handle()
async def _(event: MessageEvent, bot: Bot, msg: Message = CommandArg()):
    hash_id = msg.extract_plain_text()
    directory_path = "data/novelai/output"  # 指定目录路径
    filenames = await get_all_filenames(directory_path)
    txt_file_name, img_file_name = f"{hash_id}.txt", f"{hash_id}.jpg"
    if txt_file_name in list(filenames.keys()):
        txt_content = await extract_tags_from_file(filenames[txt_file_name])
        img_file_path = filenames[img_file_name]
        img_file_path = img_file_path if os.path.exists(img_file_path) else filenames[f"{hash_id}.png"]
        async with aiofiles.open(img_file_path, "rb") as f:
            content = await f.read()
        msg_list = [f"这是你要找的{hash_id}的图\n", txt_content, MessageSegment.image(content)]

        if config.novelai_extra_pic_audit:
            fifo = AIDRAW(user_id=event.get_user_id,
                          event=event 
                        )
            
            await fifo.load_balance_init()
            message_ = await check_safe_method(fifo, [content], [""], None, False)
            if isinstance(message_[1], MessageSegment):
                try:
                    await send_forward_msg(bot, event, event.sender.nickname, str(event.user_id), msg_list)
                except ActionFailed:
                    await risk_control(bot, event, msg_list, True)
            else:
                await bot.send(event, message="哼！想看涩图，自己看私聊去！")
        else:
            try:
                await send_forward_msg(bot, event, event.sender.nickname, str(event.user_id), msg_list)
            except ActionFailed:
                await risk_control(bot, event, msg_list, True)


@word_frequency_count.handle()
async def _(event: MessageEvent, bot: Bot, msg: Message = CommandArg()):
    msg_list = []

    async def count_word_frequency(word_list):
        word_frequency = Counter(word_list)
        return word_frequency

    async def sort_word_frequency(word_frequency):
        sorted_frequency = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)
        return sorted_frequency

    word_list = await get_tags_list(False)
    word_frequency = await count_word_frequency(word_list)
    sorted_frequency = await sort_word_frequency(word_frequency)
    for word, frequency in sorted_frequency[0:240] if len(sorted_frequency) >= 240 else sorted_frequency:
        msg_list.append(f"prompt:{word},出现次数:{frequency}\t\n")
    await risk_control(bot, event, msg_list, True)
        