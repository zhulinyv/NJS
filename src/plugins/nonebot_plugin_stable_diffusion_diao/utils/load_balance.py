import aiohttp, asyncio, random
from nonebot import logger
from ..config import config
import json
import time
import aiofiles
import traceback


async def calc_avage_time(state_dict_: list):
    spend_time_list = []
    for date_time in state_dict_["info"]["history"]:
        spend_time_list.append(list(date_time.values())[0])
    spend_time_list.pop(0)
    spend_time_list.sort()
    spend_time_list.pop() and spend_time_list.pop(0)
    return int(sum(spend_time_list) / (len(spend_time_list)) - 3)


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


async def chose_backend(state_dict, normal_backend, task_type):
    backend_processtime: dict = {}
    ava_url_dict: dict = {}
    # n = -1
    #         y = 0
    #         normal_backend = list(status_dict.keys())
    #         logger.info("没有空闲后端")
    #         if len(normal_backend) == 0:
    #             raise RuntimeError("没有可用后端")
    #         else:
    #             eta_list = list(status_dict.values())
    #             for t, b in zip(eta_list, normal_backend):
    #                 if int(t) < defult_eta:
    #                     y += 1
    #                     ava_url = b
    #                     logger.info(f"已选择后端{reverse_dict[ava_url]}")
    #                     break
    #                 else:
    #                     y +=0
    #             if y == 0:
    #                 reverse_sta_dict = {value: key for key, value in status_dict.items()}
    #                 eta_list.sort()
    #                 ava_url = reverse_sta_dict[eta_list[0]]
    for i in normal_backend:
        cur_state_dict = state_dict[i][task_type]
        history_info_list: list = cur_state_dict["info"]
        logger.debug(history_info_list)
        if len(history_info_list["history"]) > 20: # 需要至少20次生成来确定此后端的平均工作时间
            ava_time = (await calc_avage_time(cur_state_dict) if 
                        history_info_list["history_avage_time"] is None 
                        else i["history_avage_time"])
        elif len(history_info_list["history"]) > 100:
            # 重新计算平均时间, 并清空时间列表
            pass
        else: 
            ava_time = cur_state_dict["info"]["eta_time"]
        count = cur_state_dict["info"]["tasks_count"]
        total_process_time = count * ava_time
        backend_processtime.update({total_process_time: i})
    # process_time_rev = {value: key for key, value in backend_process_time}
    backend_process_time = list(backend_processtime.keys())
    backend_process_time.sort()
    logger.debug(backend_processtime[backend_process_time[0]])
    logger.error(backend_processtime)
    return backend_processtime[backend_process_time[0]]


async def sd_LoadBalance(addtional_site=None, task_counts=None, task_type=None, state_dict=None):
    '''
    分别返回可用后端索引, 后端对应ip和名称(元组), 显存占用
    '''
    backend_url_dict = config.novelai_backend_url_dict
    if state_dict is None:
        with open("data/novelai/load_balance.json", "r", encoding="utf-8") as f:
            content = f.read()
            state_dict = json.loads(content)
    else:
        pass
    if addtional_site:
        backend_url_dict.update({"群专属后端": f"{addtional_site}"})
    reverse_dict = {value: key for key, value in backend_url_dict.items()}
    tasks = []
    is_avaiable = 0
    status_dict = {}
    ava_url = None
    n = -1
    e = -1
    normal_backend = None
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
            logger.info(f"后端{list(config.novelai_backend_url_dict.keys())[e]}掉线")
        else:
            try:
                if resp_tuple[3] in [200, 201]:
                    n += 1
                    status_dict[resp_tuple[2]] = resp_tuple[0]["eta_relative"]
                    normal_backend = (list(status_dict.keys()))
                else:
                    raise RuntimeError
            except RuntimeError or TypeError:
                logger.error(f"后端{list(config.novelai_backend_url_dict.keys())[e]}出错")
                continue
            else:
                # 更改判断逻辑
                if resp_tuple[0]["progress"] in [0, 0.01, 0.0]:
                        logger.info("后端空闲")
                        is_avaiable += 1
                        ava_url = normal_backend[n]
                else:
                    # if state_dict[resp_tuple[2]]["status"] == "idle":
                    #     logger.info("后端空闲")
                    #     is_avaiable += 1
                    #     ava_url = normal_backend[n]
                    #     break
                    logger.info("后端忙")
    if normal_backend is None:
        normal_backend_name = config.novelai_site or "127.0.0.1:7860"
        normal_backend = [config.novelai_site, "127.0.0.1:7860"]
    else:
        normal_backend_name = [i for i in normal_backend]
    logger.info(f"正常后端:{normal_backend_name}")
    if is_avaiable == 0:
        logger.debug("进入后端选择")
        ava_url = await chose_backend(state_dict, normal_backend, task_type)

    logger.info(f"已选择后端{ava_url}")
    tc = int(state_dict[ava_url][task_type]["info"]["tasks_count"])
    tc += 1
    state_dict[ava_url]["status"] = task_type
    state_dict[ava_url]["start_time"] = time.time()
    state_dict[ava_url][task_type]["info"]["tasks_count"] = tc
    with open("data/novelai/load_balance.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(state_dict))
    ava_url_index = list(backend_url_dict.values()).index(ava_url)
    ava_url_tuple = (ava_url, reverse_dict[ava_url], all_resp, len(normal_backend))
    return ava_url_index, ava_url_tuple, normal_backend, state_dict