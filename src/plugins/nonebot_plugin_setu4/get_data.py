import asyncio
import os
import random
import sqlite3
from io import BytesIO
from pathlib import Path
import nonebot
from httpx import AsyncClient
from nonebot.log import logger
from PIL import Image
from .fetch_resources import DownloadPic
error = "Error:"

# save_path,可在env设置, 默认False, 类型bool或str
try:
    save_path = nonebot.get_driver().config.setu_save
    all_file_name = os.listdir(save_path)
except:
    save_path = False
    all_file_name = []
try:
    setu_proxy = nonebot.get_driver().config.setu_proxy
except:
    setu_proxy = 'px2.rainchan.win'



# 返回列表,内容为setu消息(列表套娃)
async def get_setu(keyword="", r18=False, num=1, quality=75) -> list:
    data = []
    # 连接数据库
    conn = sqlite3.connect(
        Path(os.path.join(os.path.dirname(__file__), "resource")) / "lolicon.db")
    cur = conn.cursor()
    # sql操作,根据keyword和r18进行查询拿到数据
    cursor = cur.execute(
        f"SELECT pid,title,author,r18,tags,urls from main where (tags like \'%{keyword}%\' or title like \'%{keyword}%\' or author like \'%{keyword}%\') and r18=\'{r18}\' order by random() limit {num}")
    db_data = cursor.fetchall()
    # 断开数据库连接
    conn.close()
    # 如果没有返回结果
    if db_data == []:
        data.append([error, f"图库中没有搜到关于{keyword}的图。", False])
        return data
    async with AsyncClient() as client:
        tasks=[]
        for setu in db_data:
            tasks.append(pic(setu, quality, client))
        data = await asyncio.gather(*tasks)
    return data


# 返回setu消息列表,内容 [图片, 信息, True/False, url]
async def pic(setu, quality, client):
    setu_pid = setu[0]                   # pid
    setu_title = setu[1]                 # 标题
    setu_author = setu[2]                # 作者
    setu_r18 = setu[3]                   # r18
    setu_tags = setu[4]                  # 标签
    setu_url = setu[5].replace('i.pixiv.re', setu_proxy)     # 图片url

    data = (
        "标题:"
        + setu_title
        + "\npid:"
        + str(setu_pid)
        + "\n画师:"
        + setu_author
    )

    logger.info("\n"+data+"\ntags:" +
                setu_tags+"\nR18:"+setu_r18)
    # 本地图片如果是用well404的脚本爬的话,就把下面的replace代码解除注释
    file_name = setu_url.split("/")[-1]  # .replace('p', "",1)

    # 判断文件是否本地存在
    if file_name in all_file_name:
        logger.info("图片本地存在")
        image = Image.open(save_path + "/" + file_name)
    # 如果没有就下载
    else:
        logger.info(f"图片本地不存在,正在去{setu_proxy}下载")
        content = await DownloadPic(setu_url, client)
        
        #  此次fix结束
        if type(content) == int:
            logger.error(f"图片下载失败, 状态码: {content}")
            return [error, f"图片下载失败, 状态码: {content}", False, setu_url]
        # 如果有本地保存路径则存储
        if save_path:
            file_name = setu_url.split("/")[-1]
            try:
                with open(f"{save_path}/{file_name}", "wb") as f:
                    f.write(content)
                all_file_name.append(file_name)
            except Exception as e:
                logger.error(f'图片存储失败: {e}')
        image = Image.open(BytesIO(content))
    pic = await change_pixel(image, quality)
    return [pic, data, True, setu_url]

# 图像镜像左右翻转
async def change_pixel(image:Image, quality):
    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    image = image.convert("RGB")
    image.load()[0, 0] = (random.randint(0, 255),
                          random.randint(0, 255), random.randint(0, 255))
    byte_data = BytesIO()
    image.save(byte_data, format="JPEG", quality=quality)
    # pic是的图片的bytes
    pic = byte_data.getvalue()
    return pic
