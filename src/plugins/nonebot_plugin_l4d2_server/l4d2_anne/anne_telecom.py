# from ..l4d2_image.steam import url_to_byte
# from bs4 import BeautifulSoup
# from typing import List

# 暂时废弃
# class ANNE_API:

#     async def __init__(
#         self,
#         STEAMID:str,
#         tag:str
#     ):
#         self.STEAMID = STEAMID
#         if tag == '中':
#             msg1 = await self.anne_msg()
#         elif tag == '长':
#             msg1 = await self.anne_msg()
#             msg1.update(await self.anne_map())


#     async def anne_msg(self):
#         """个人资料表"""
#         data_bytes = await url_to_byte('https://sb.trygek.com/l4d_stats/ranking/player.php?steamid={self.STEAMID}')
#         data_bs = BeautifulSoup(data_bytes, 'html.parser')
#         data_fom = data_bs.find_all('table')
#         n = 0
#         data_dict = {}
#         while n < 2:
#             data_list:List[dict] = []
#             detail2 = data_fom[n]
#             tr = detail2.find_all('tr')
#             for i in tr:
#                 title = i.find('td', {'class': 'w-50'})
#                 value = title.find_next_sibling('td')
#                 new_dict = {title.text:value.text}
#                 data_dict.update(new_dict)
#             data_list.append(data_dict)
#             n += 1
#         # 获取头像
#         element:str = data_fom.find_all(attrs={"style": "cursor:pointer"})[0].get("onclick")
#         player_url = element.split("'")[1]
#         data_list[0].update({"个人资料":player_url})
#         # 获取一言
#         message = data_fom.select("html body div.content.text-center.text-md-left div.container.text-left div.col-md-12.h-100 div.card-body.worldmap.d-flex.flex-column.justify-content-center.text-center span")
#         msg_list = []
#         for i in message:
#             msg_list.append(i.text)
#         data_list[0].update({"一言":msg_list})
#         return data_list

#     async def anne_map(self):
#         """个人地图表"""
#         data_dict = {}
#         data_bytes = await url_to_byte('https://sb.trygek.com/l4d_stats/ranking/timedmaps.php?steamid={self.STEAMID}')
#         data_bs = BeautifulSoup(data_bytes, 'html.parser')
#         tbody = data_bs.select('tbody')
#         for tr in tbody:
#             tds = tr.select('td')
#             n = 0
#             for td in tds:
#                 n += 1
#                 title:str = td['data-title'][:-1]
#                 data_text = td.text
#                 if title == '特感数量':
#                     special_amount = data_text
#                 elif title == '刷新间隔':
#                     refresh_interval = data_text
#                 else:
#                     if title in data_dict:
#                         data_dict[title].append(data_text)
#                     else:
#                         data_dict[title] = [data_text]
#             if special_amount and refresh_interval:
#                 data_dict['刷特时间'] = special_amount + refresh_interval

#         return data_dict
