# import httpx
# from typing import List,Union
# from nonebot.log import logger

# async def seach_map(msg:Union[list,str],qq:str,key:str,mode:str = 'zh'):
#     url = ""
#     json = {
#         "mode":mode,
#         "map_name":msg,
#         "qq":qq,
#         "key":key
#     }
#     file = httpx.post(url=url,json=json)
#     if mode == 'zh':
#         if file.status_code == 200:
#             return file.json()
#         elif file.status_code == 204:
#             return "没有结果"
#         elif file.status_code == 406:
#             return "参数错误"
#         elif file.status_code == 401:
#             return file.json()
#     elif mode == 'ip':
#         rep:dict = file.json()
#         try:
#             logger.error(rep['error_'])
#         except:
#             pass
#         print(file.json())
#         return file.json()
#     elif mode == 'first':
#         ip_tag:list = file.json()
#         return ip_tag


# async def map_dict_to_str(data:List[dict]):
#     msg = ""
#     for key,value in data[0].items():
#         if key == "url":
#             continue
#         msg += f"{key}:{value}\n"
#     return msg
