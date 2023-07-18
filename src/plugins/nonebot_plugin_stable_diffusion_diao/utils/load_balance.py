import aiohttp
import asyncio 
import random
from nonebot import logger
from ..config import config, redis_client
import time
from tqdm import tqdm
from datetime import datetime

import ast
import traceback
import aiofiles
import json
import os


async def get_progress(url):
    first_get = "http://" + url + "/sdapi/v1/memory" 
    api_url = "http://" + url + "/sdapi/v1/progress"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session1:
        async with session1.get(url=first_get) as resp1:
            resp_code2 = resp1.status
    async with aiohttp.ClientSession() as session:
        async with session.get(url=api_url) as resp:
            resp_json = await resp.json()
            return resp_json, resp.status, url, resp_code2


async def get_vram(ava_url):
    get_mem = "http://" + ava_url + "/sdapi/v1/memory"        
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session1:
            async with session1.get(url=get_mem) as resp2:
                all_memory_usage = await resp2.json()
                logger.debug(all_memory_usage)
                vram_total = int(all_memory_usage["cuda"]["system"]["total"]/1000000)
                vram_used = int(all_memory_usage["cuda"]["system"]["used"]/1000000)
                vram_usage = f"显存占用{vram_used}M/{vram_total}M"
    except Exception:
        vram_usage = ""
    return vram_usage


async def sd_LoadBalance():
    '''
    分别返回可用后端索引, 后端对应ip和名称(元组), 显存占用
    '''
    current_date = datetime.now().date()
    day: str = str(int(datetime.combine(current_date, datetime.min.time()).timestamp()))
    backend_url_dict = config.novelai_backend_url_dict
    reverse_dict = {value: key for key, value in backend_url_dict.items()}
    tasks = []
    is_avaiable = 0
    status_dict = {}
    ava_url = None
    n = -1
    e = -1
    defult_eta = 20
    normal_backend = None
    idle_backend = []
    for url in backend_url_dict.values():
        tasks.append(get_progress(url))
    # 获取api队列状态
    all_resp = await asyncio.gather(*tasks, return_exceptions=True)
    for resp_tuple in all_resp:
        e += 1 
        if isinstance(resp_tuple,
                      (aiohttp.ContentTypeError,
                       asyncio.exceptions.TimeoutError,
                       aiohttp.ClientTimeout,
                       Exception)
                       ):
            print(f"后端{list(config.novelai_backend_url_dict.keys())[e]}掉线")
        else:
            try:
                if resp_tuple[3] in [200, 201]:
                    n += 1
                    status_dict[resp_tuple[2]] = resp_tuple[0]["eta_relative"]
                    normal_backend = (list(status_dict.keys()))
                else:
                    raise RuntimeError
            except RuntimeError or TypeError:
                print(f"后端{list(config.novelai_backend_url_dict.keys())[e]}出错")
                continue
            else:
                # 更改判断逻辑
                if resp_tuple[0]["progress"] in [0, 0.01, 0.0]:
                        is_avaiable += 1
                        idle_backend.append(normal_backend[n])
                else:
                    pass
            total = 100
            progress = int(resp_tuple[0]["progress"]*100)
            show_str = f"{list(backend_url_dict.keys())[e]}"
            show_str = show_str.ljust(25, "-")
            with tqdm(total=total,
                      desc=show_str + "-->",
                      bar_format="{l_bar}{bar}|"
                      ) as pbar:
                pbar.update(progress)
                time.sleep(0.1)
    if config.novelai_load_balance_mode == 1:
        if is_avaiable == 0:
            n = -1
            y = 0
            normal_backend = list(status_dict.keys())
            logger.info("没有空闲后端")
            if len(normal_backend) == 0:
                raise RuntimeError("没有可用后端")
            else:
                eta_list = list(status_dict.values())
                for t, b in zip(eta_list, normal_backend):
                    if int(t) < defult_eta:
                        y += 1
                        ava_url = b
                        logger.info(f"已选择后端{reverse_dict[ava_url]}")
                        break
                    else:
                        y += 0
                if y == 0:
                    reverse_sta_dict = {value: key for key, value in status_dict.items()}
                    eta_list.sort()
                    ava_url = reverse_sta_dict[eta_list[0]]
        if len(idle_backend) >= 1:
            ava_url = random.choice(idle_backend)
    elif config.novelai_load_balance_mode == 2:
        list_tuple = []
        weight_list = config.novelai_load_balance_weight
        backend_url_list = list(config.novelai_backend_url_dict.values())
        weight_list_len = len(weight_list)
        backend_url_list_len = len(backend_url_list)
        normal_backend_len = len(normal_backend)
        if weight_list_len != backend_url_list_len:
            logger.warning("权重列表长度不一致, 请重新配置!")
            ava_url = random.choice(normal_backend)
        else:
            from ..backend import AIDRAW
            if weight_list_len != normal_backend_len:
                multi = weight_list_len / (weight_list_len - normal_backend_len)
                for weight, backend_site in zip(weight_list, backend_url_list):
                    if backend_site in normal_backend:
                        list_tuple.append((backend_site, weight*multi))
            else:
                for backend, weight in zip(normal_backend, weight_list):
                    list_tuple.append((backend, weight))
            print(list_tuple)
            fifo = AIDRAW()
            ava_url = fifo.weighted_choice(list_tuple)
    if redis_client:
        try:
            r = redis_client[2]
            if r.exists(day):
                backend_info = r.get(day)
                backend_info = backend_info.decode("utf-8")
                backend_info = ast.literal_eval(backend_info)
                if backend_info.get("gpu"):
                    backend_dict = backend_info.get("gpu")
                    backend_dict[reverse_dict[ava_url]] = backend_dict[reverse_dict[ava_url]] + 1
                    backend_info["gpu"] = backend_dict
                else:
                    backend_dict = {}
                    backend_info["gpu"] = {}
                    for i in list(config.novelai_backend_url_dict.keys()):
                        backend_dict[i] = 1
                        backend_info["gpu"] = backend_dict
                r.set(day, str(backend_info))
        except Exception:
            logger.warning("redis出错惹!不过问题不大")
            logger.info(traceback.print_exc())
    else:
        filename = "data/novelai/day_limit_data.json"
        if os.path.exists(filename):
            async with aiofiles.open(filename, "r") as f:
                json_ = await f.read()
                json_ = json.loads(json_)
            json_[day]["gpu"][reverse_dict[ava_url]] = json_[day]["gpu"][reverse_dict[ava_url]] + 1
            async with aiofiles.open(filename, "w") as f:
                await f.write(json.dumps(json_))
        else:
            pass
    logger.info(f"已选择后端{reverse_dict[ava_url]}")
    ava_url_index = list(backend_url_dict.values()).index(ava_url)
    ava_url_tuple = (ava_url, reverse_dict[ava_url], all_resp, len(normal_backend))
    return ava_url_index, ava_url_tuple, normal_backend