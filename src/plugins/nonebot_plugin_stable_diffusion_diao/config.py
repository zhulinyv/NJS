import json
from pathlib import Path
import aiohttp
import ast
import asyncio
import traceback

import aiofiles
from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseSettings, validator
from pydantic.fields import ModelField

jsonpath = Path("data/novelai/config.json").resolve()
lb_jsonpath = Path("data/novelai/load_balance.json").resolve()
redis_client = None
backend_emb, backend_lora = None, None

nickname = list(get_driver().config.nickname)[0] if len(
    get_driver().config.nickname) else "nonebot-plugin-stable-diffusion-diao"


class Config(BaseSettings):
    # 服务器设置
    lb_jsonpath
    novelai_steps: int = None  # 默认步数
    novelai_command_start: set = {"绘画", "咏唱", "召唤", "约稿", "aidraw", "画", "绘图", "AI绘图", "ai绘图"}
    novelai_scale: int = 7  # CFG Scale 请你自己设置, 每个模型都有适合的值
    novelai_retry: int = 4  # post失败后重试的次数
    novelai_token: str = ""  # 官网的token
    # novelai: dict = {"novelai":""}# 你的服务器地址（包含端口），不包含http头，例:127.0.0.1:6969
    novelai_mode: str = "sd"
    novelai_site: str = "la.iamdiao.lol:5938"
    # 后台设置
    novelai_save: int = 2  # 是否保存图片至本地,0为不保存，1保存，2同时保存追踪信息
    novelai_save_png: bool = False  # 是否保存为PNG格式
    novelai_paid: int = 3  # 0为禁用付费模式，1为点数制，2为不限制
    novelai_pure: bool = True  # 是否启用简洁返回模式（只返回图片，不返回tag等数据）
    novelai_limit: bool = False  # 是否开启限速
    novelai_daylimit: int = 24  # 每日次数限制，0为禁用
    novelai_h: int = 2  # 是否允许H, 0为不允许, 1为删除屏蔽词, 2允许
    novelai_htype: int = 3  # 1为发现H后私聊用户返回图片, 2为返回群消息但是只返回图片url并且主人直接私吞H图(, 3发送二维码(无论参数如何都会保存图片到本地)
    novelai_antireport: bool = True  # 玄学选项。开启后，合并消息内发送者将会显示为调用指令的人而不是bot
    novelai_max: int = 3  # 每次能够生成的最大数量
    # 允许生成的图片最大分辨率，对应(值)^2.默认为1024（即1024*1024）。如果服务器比较寄，建议改成640（640*640）或者根据能够承受的情况修改。naifu和novelai会分别限制最大长宽为1024
    # 可运行更改的设置
    novelai_tags: str = ""  # 内置的tag
    novelai_ntags: str = ""  # 内置的反tag
    novelai_cd: int = 60  # 默认的cd
    novelai_group_cd: int = 3  # 默认的群共享cd
    novelai_on: bool = True  # 是否全局开启
    novelai_revoke: int = 0  # 是否自动撤回，该值不为0时，则为撤回时间
    novelai_random_ratio: bool = True  # 是否开启随机比例
    novelai_random_sampler: bool = False  # 是否开启随机采样器
    novelai_random_scale: bool = False  # 是否开启随机CFG
    novelai_random_ratio_list: list = [("p", 0.35), ("s", 0.10), ("l", 0.35), ("uw", 0.1), ("uwp", 0.1)] # 随机图片比例
    novelai_random_sampler_list = [("Euler a", 0.35), ("DDIM", 0.3), ("DPM++ 2S a Karras", 0.05), ("DPM++ 2M Karras", 0.3)]
    novelai_random_scale_list = [(3, 0.05), (4, 0.2), (5, 0.05), (6, 0.4), (7, 0.1), (8, 0.18), (9, 0.02)]
    novelai_load_balance: bool = True  # 负载均衡, 使用前请先将队列限速关闭, 目前只支持stable-diffusion-webui, 所以目前只支持novelai_mode = "sd" 时可用, 目前已知问题, 很短很短时间内疯狂画图的话无法均匀分配任务
    novelai_load_balance_mode: int = 1  # 负载均衡模式, 1为随机, 2为加权随机选择
    novelai_load_balance_weight: list = []  # 设置列表, 列表长度为你的后端数量, 数值为随机权重, 例[0.2, 0.5, 0.3]
    novelai_backend_url_dict: dict = {"雕雕的后端": "la.iamdiao.lol:5938", "雕雕的后端2": "la.iamdiao.lol:1521"} # 你能用到的后端, 键为名称, 值为url, 例:backend_url_dict = {"NVIDIA P102-100": "192.168.5.197:7860","NVIDIA CMP 40HX": "127.0.0.1:7860"
    novelai_sampler: str = None  # 默认采样器,不写的话默认Euler a, Euler a系画人物可能比较好点, DDIM系, 如UniPC画出来的背景比较丰富, DPM系采样器一般速度较慢, 请你自己尝试(以上为个人感觉
    novelai_hr: bool = True  # 是否启动高清修复
    novelai_hr_scale: float = 1.5  # 高清修复放大比例
    novelai_hr_payload: dict = {
        "enable_hr": "true", 
        "denoising_strength": 0.55,  # 重绘幅度
        "hr_scale": novelai_hr_scale,  # 高清修复比例, 1.5为长宽分辨率各X1.5
        "hr_upscaler": "Lanczos",  # 超分模型, 使用前请先确认此模型是否可用, 推荐使用R-ESRGAN 4x+ Anime6B
        "hr_second_pass_steps": 7,  # 高清修复步数, 个人建议7是个不错的选择, 速度质量都不错
    } # 以上为个人推荐值
    novelai_SuperRes_MaxPixels: int = 2000  # 超分最大像素值, 对应(值)^2, 为了避免有人用超高分辨率的图来超分导致爆显存(
    novelai_SuperRes_generate: bool = False  # 图片生成后是否再次进行一次超分
    novelai_SuperRes_generate_payload: dict = {
        "upscaling_resize": 1.2,  # 超分倍率, 为长宽分辨率各X1.2
        "upscaler_1": "Lanczos",  # 第一次超分使用的方法
        "upscaler_2": "R-ESRGAN 4x+ Anime6B",  # 第二次超分使用的方法
        "extras_upscaler_2_visibility": 0.7  # 第二层upscaler力度
    } # 以上为个人推荐值
    novelai_ControlNet_post_method: int = 0
    novelai_size_org: int = 640  # 最大分辨率
    if novelai_hr:
        novelai_size: int = novelai_size_org
    else:
        novelai_size: int = novelai_size_org * novelai_hr_payload["hr_scale"]
    '''post方法有 0: /sdapi/v1/txt2img 和 1: /controlnet/txt2img 
    个人使用第一种方法post显卡占用率反复横跳TAT 
    tips:使用/controlnet/txt2img会提示warning: consider using the '/sdapi/v1/txt2img' route with the 'alwayson_scripts' json property instead''' 
    novelai_ControlNet_payload: list = [
        {
            "alwayson_scripts": {
            "controlnet": {
            "args": [
                {
                "input_image": "",
                "module": "scribble_hed",
                "model": "control_v11p_sd15_scribble [d4ba51ff]",
                "weight": 1,
                "lowvram": "false",
                "processor_res": novelai_size*1.5,
                "threshold_a": 100,
                "threshold_b": 250,
                }
            ]
                }
            }
        }, 
        {"controlnet_units": 
                [{"input_image": "", 
                "module": "scribble_hed", 
                "model": "control_v11p_sd15_scribble [d4ba51ff]", 
                "weight": 1, 
                "lowvram": "false", 
                "processor_res": novelai_size*1.5, 
                "threshold_a": 100,
                "threshold_b": 250}]
        }
    ]
    
    novelai_cndm: dict = {"controlnet_module": "canny", 
                          "controlnet_processor_res": novelai_size, 
                          "controlnet_threshold_a": 100, 
                          "controlnet_threshold_b": 250}
    
    novelai_picaudit: int = 4  # 1为百度云图片审核, 2为本地审核功能, 请去百度云免费领取 https://ai.baidu.com/tech/imagecensoring 3为关闭, 4为使用webui，api,地址为novelai_tagger_site设置的
    novelai_pic_audit_api_key: dict = {"SECRET_KEY": "",
                                       "API_KEY": ""}  # 你的百度云API Key
    openai_api_key: str = "" # 如果要使用ChatGPTprompt生成功能, 请填写你的OpenAI API Key
    novelai_auto_icon: bool = True  # 机器人自动换头像(没写呢！)
    novelai_extra_pic_audit = True  # 是否为二次元的我, chatgpt生成tag等功能添加审核功能
    # 翻译API设置
    bing_key: str = None  # bing的翻译key
    deepl_key: str = None  # deepL的翻译key
    baidu_translate_key: dict = None  # 例:{"SECRET_KEY": "", "API_KEY": ""} # https://console.bce.baidu.com/ai/?_=1685076516634#/ai/machinetranslation/overview/index
    novelai_todaygirl = 1  # 可选值 1 和 2 两种不同的方式
    novelai_tagger_site: str = "la.iamdiao.lol:25"  # 分析功能的地址 例如 127.0.0.1:7860
    vits_site: str = "la.iamdiao.lol:587"
    run_screenshot = False  # 获取服务器的屏幕截图
    is_redis_enable = True  # 是否启动redis, 启动redis以获得更多功能
    auto_match = True  # 是否自动匹配
    backend_name_list = []
    backend_site_list = []
    # 允许单群设置的设置
    def keys(cls):
        return ("novelai_cd", "novelai_tags", "novelai_on", "novelai_ntags", "novelai_revoke", "novelai_h", "novelai_htype", "novelai_picaudit", "novelai_pure", "novelai_site")

    def __getitem__(cls, item):
        return getattr(cls, item)

    @validator("novelai_cd", "novelai_max")
    def non_negative(cls, v: int, field: ModelField):
        if v < 1:
            return field.default
        return v

    @validator("novelai_paid")
    def paid(cls, v: int, field: ModelField):
        if v < 0:
            return field.default
        elif v > 3:
            return field.default
        return v

    class Config:
        extra = "ignore"

    async def set_enable(cls, group_id, enable):
        # 设置分群启用
        await cls.__init_json()
        now = await cls.get_value(group_id, "on")
        logger.debug(now)
        if now:
            if enable:
                return f"aidraw已经处于启动状态"
            else:
                if await cls.set_value(group_id, "on", "false"):
                    return f"aidraw已关闭"
        else:
            if enable:
                if await cls.set_value(group_id, "on", "true"):
                    return f"aidraw开始运行"
            else:
                return f"aidraw已经处于关闭状态"

    async def __init_json(cls):
        # 初始化设置文件
        if not jsonpath.exists():
            jsonpath.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(jsonpath, "w+") as f:
                await f.write("{}")

    async def get_value(cls, group_id, arg: str):
        # 获取设置值
        group_id = str(group_id)
        arg_ = arg if arg.startswith("novelai_") else "novelai_" + arg
        if arg_ in cls.keys():
            await cls.__init_json()
            async with aiofiles.open(jsonpath, "r") as f:
                jsonraw = await f.read()
                configdict: dict = json.loads(jsonraw)
                return configdict.get(group_id, {}).get(arg_, dict(cls)[arg_])
        else:
            return None

    async def get_groupconfig(cls, group_id):
        # 获取当群所有设置值
        group_id = str(group_id)
        await cls.__init_json()
        async with aiofiles.open(jsonpath, "r") as f:
            jsonraw = await f.read()
            configdict: dict = json.loads(jsonraw)
            baseconfig = {}
            for i in cls.keys():
                value = configdict.get(group_id, {}).get(
                    i, dict(cls)[i])
                baseconfig[i] = value
            logger.debug(baseconfig)
            return baseconfig

    async def set_value(cls, group_id, arg: str, value: str):
        """设置当群设置值"""
        # 将值转化为bool和int
        if value.isdigit():
            value: int = int(value)
        elif value.lower() == "false":
            value = False
        elif value.lower() == "true":
            value = True
        group_id = str(group_id)
        arg_ = arg if arg.startswith("novelai_") else "novelai_" + arg
        # 判断是否合法
        if arg_ in cls.keys() and isinstance(value, type(dict(cls)[arg_])):
            await cls.__init_json()
            # 读取文件
            async with aiofiles.open(jsonpath, "r") as f:
                jsonraw = await f.read()
                configdict: dict = json.loads(jsonraw)
            # 设置值
            groupdict = configdict.get(group_id, {})
            if value == "default":
                groupdict[arg_] = False
            else:
                groupdict[arg_] = value
            configdict[group_id] = groupdict
            # 写入文件
            async with aiofiles.open(jsonpath, "w") as f:
                jsonnew = json.dumps(configdict)
                await f.write(jsonnew)
            return True
        else:
            logger.debug(f"不正确的赋值,{arg_},{value},{type(value)}")
            return False


async def get_(site: str, end_point="/sdapi/v1/prompt-styles") -> dict or None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"http://{site}{end_point}") as resp:
                if resp.status in [200, 201]:
                    resp_json: list = await resp.json()
                    return resp_json
                else:
                    return None
    except Exception:
        return None


async def this_is_a_func(end_point_index):
    task_list = []
    end_point_list = ["/sdapi/v1/prompt-styles", "/sdapi/v1/embeddings", "/sdapi/v1/loras"]
    for site in config.backend_site_list:
        task_list.append(get_(site, end_point_list[end_point_index]))
    all_resp = await asyncio.gather(*task_list, return_exceptions=False)
    return all_resp

config = Config(**get_driver().config.dict())
config.backend_name_list = list(config.novelai_backend_url_dict.keys())
config.backend_site_list = list(config.novelai_backend_url_dict.values())

try:
    import tensorflow
except ImportError:
    logger.warning("未能成功导入tensorflow")
    logger.warning("novelai_picaudit为2时本地图片审核不可用")
if config.is_redis_enable:
    try:
        import redis
    except ImportError:
        logger.error("未找到redis库, 请先pip install redis")
    else:
        async def main():
            redis_client = []
            r1 = redis.Redis(host='localhost', port=6379, db=7)
            r2 = redis.Redis(host='localhost', port=6379, db=8)
            r3 = redis.Redis(host='localhost', port=6379, db=9)
            redis_client = [r1, r2, r3]
            resp = r1.ping()
            try:
                if resp:
                    logger.info("redis连接成功")
                    logger.info("开始读取webui的预设")
                    
                    all_style_list, all_emb_list, all_lora_list = [], [], []
                    backend_emb, backend_lora = {}, {}
                    all_resp_style = await this_is_a_func(0)
                    for backend_style in all_resp_style:
                        if backend_style is not None:
                            for style in backend_style:
                                all_style_list.append(json.dumps(style))
                    logger.info("读取webui的预设完成")
                    logger.info("开始读取webui的embs")
                    normal_backend_index = -1
                    all_emb_list = await this_is_a_func(1)
                    for back_emb in all_emb_list:
                        normal_backend_index += 1
                        if back_emb is not None:
                            emb_dict = {}
                            n = 0
                            for emb in list(back_emb["loaded"].keys()):
                                n += 1
                                emb_dict[n] = emb
                            backend_emb[config.backend_name_list[normal_backend_index]] = emb_dict
                        else:
                            backend_emb[config.backend_name_list[normal_backend_index]] = None
                    logger.info("开始读取webui的loras")
                    all_lora_list = await this_is_a_func(2)
                    normal_backend_index = -1
                    for back_lora in all_lora_list:
                        normal_backend_index += 1
                        if back_lora is not None:
                            lora_dict = {}
                            n = 0
                            for lora in back_lora:
                                lora_name = lora["name"]
                                n += 1
                                lora_dict[n] = lora_name
                            backend_lora[config.backend_name_list[normal_backend_index]] = lora_dict
                        else:
                            backend_lora[config.backend_name_list[normal_backend_index]] = None
                    logger.info("存入数据库...")
                    if r2.exists("emb"):
                        r2.delete(*["style", "emb", "lora"])
                    pipe = r2.pipeline()
                    pipe.rpush("style", *all_style_list)
                    pipe.set("emb", str(backend_emb))
                    pipe.set("lora", str(backend_lora))
                    pipe.execute()
                else:
                    logger.error("redis连接失败")
                    redis_client = None
            except Exception:
                logger.error(traceback.print_exc())
                logger.error("出现了意外错误, 已经暂停redis使用")
                redis_client = None
            return redis_client
        redis_client = asyncio.run(main())

logger.info(f"加载config完成" + str(config))
logger.info(f"后端数据加载完成, 共有{len(config.backend_name_list)}个后端被加载")

