import os
import random
import asyncio
import sqlite3
import nonebot
from PIL import Image
from io import BytesIO
from pathlib import Path
from httpx import AsyncClient
from nonebot.log import logger
from .fetch_resources import DownloadPic


error: str = "Error:"
# save_path,可在env设置, 默认False, 类型bool或str
try:
    save_path: str = nonebot.get_driver().config.setu_save
    all_file_name: list = os.listdir(save_path)
except:
    save_path: bool = False
    all_file_name: list = []
try:
    setu_proxy: str = nonebot.get_driver().config.setu_proxy
except:
    setu_proxy: str = 'sex.nyan.xyz'


# 返回列表,内容为setu消息(列表套娃)
async def get_setu(keywords: list = [], r18: bool = False, num: int = 1, quality: int = 75) -> list:
    data = []
    # 连接数据库
    conn = sqlite3.connect(
        Path(os.path.join(os.path.dirname(__file__), "resource")) / "lolicon.db")
    cur = conn.cursor()
    # sql操作,根据keyword和r18进行查询拿到数据
    if keywords == []:   # 如果传入的keywords是空列表, 那么where只限定r18='{r18}'
        sql = f"SELECT pid,title,author,r18,tags,urls from main where r18='{r18}' order by random() limit {num}"
    # 如果keywords列表只有一个, 那么从tags, title, author找有内容是keywords[0]的
    elif len(keywords) == 1:
        sql = f"SELECT pid,title,author,r18,tags,urls from main where (tags like '%{keywords[0]}%' or title like '%{keywords[0]}%' or author like '%{keywords[0]}%') and r18='{r18}' order by random() limit {num}"
    else:                   # 多tag的情况下的sql语句
        tagSql = ""
        for i in keywords:
            tagSql += f"tags like '%{i}%'" if i == keywords[-1] else f"tags like '%{i}%' and "
        sql = f"SELECT pid,title,author,r18,tags,urls from main where (({tagSql}) and r18='{r18}') order by random() limit {num}"
    cursor = cur.execute(sql)
    db_data = cursor.fetchall()
    # 断开数据库连接
    conn.close()
    # 如果没有返回结果
    if db_data == []:
        data.append([error, f"图库中没有搜到关于{keywords}的图。", False])
        return data
    async with AsyncClient() as client:
        tasks = []
        for setu in db_data:
            tasks.append(pic(setu, quality, client))
        data = await asyncio.gather(*tasks)
    return data


# 返回setu消息列表,内容 [图片, 信息, True/False, url]
async def pic(setu: list, quality: int, client: AsyncClient) -> list:
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
    file_name = setu_url.split("/")[-1]

    # 判断文件是否本地存在
    isInAllFileName = file_name in all_file_name
    if isInAllFileName:
        logger.info("图片本地存在")
        image = Image.open(save_path + "/" + file_name)
    # 如果没有就下载
    else:
        logger.info(f"图片本地不存在,正在去{setu_proxy}下载")
        content = await DownloadPic(setu_url, client)
        if type(content) == int:
            logger.error(f"图片下载失败, 状态码: {content}")
            return [error, f"图片下载失败, 状态码: {content}", False, setu_url]
        # 错误处理, 如果content是空bytes, 那么Image.open会报错, 跳到except, 直到change_pixel成功了, 图片应该不成问题,
        try:
            image = Image.open(BytesIO(content))
        except Exception as e:
            return [error, f"图片打开失败, 错误信息: {e}", False, setu_url]
        # 保存图片, 如果save_path不为空, 以及图片不在all_file_name中, 那么就保存图片
        if save_path and not isInAllFileName:
            try:
                with open(f"{save_path}/{file_name}", "wb") as f:
                    f.write(content)
                all_file_name.append(file_name)
            except Exception as e:
                logger.error(f'图片存储失败: {e}')
    try:
        pic = await change_pixel(image, quality)
        return [pic, data, True, setu_url]
    except Exception as e:
        return [error, f"图片处理失败: {e}", False, setu_url]


# 图像镜像左右翻转
async def change_pixel(image: Image, quality: int) -> bytes:
    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    image = image.convert("RGB")
    image.load()[0, 0] = (random.randint(0, 255),
                          random.randint(0, 255), random.randint(0, 255))
    byte_data = BytesIO()
    image.save(byte_data, format="JPEG", quality=quality)
    # pic是的图片的bytes
    pic = byte_data.getvalue()
    return pic
