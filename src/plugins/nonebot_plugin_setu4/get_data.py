import asyncio
import os
import random
import sqlite3
from io import BytesIO
from pathlib import Path
from typing import List, Union

from httpx import AsyncClient
from nonebot.log import logger
from nonebot.matcher import Matcher
from PIL import Image

from .config import config
from .fetch_resources import download_pic
from .permission_manager import pm


class GetData:
    def __init__(self) -> None:
        """初始化保存图片的路径以及该路径下的所有文件名"""
        if config.setu_save:
            self.save_path: Union[bool, str] = config.setu_save
            self.all_file_name: List[str] = os.listdir(self.save_path)
        else:
            self.save_path: Union[bool, str] = False
            self.all_file_name: List[str] = []
        self.database_path: Path = Path(__file__).parent / "resource/lolicon.db"

    @staticmethod
    async def change_pixel(image, quality: int) -> bytes:
        """图像镜像左右翻转, 并且随机修改左上角一个像素点"""
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        image = image.convert("RGB")
        image.load()[0, 0] = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        byte_data = BytesIO()
        image.save(byte_data, format="JPEG", quality=quality)
        return byte_data.getvalue()

    async def update_status_unavailable(self, urls: str) -> None:
        """更新数据库中的图片状态为unavailable"""
        conn = sqlite3.connect(self.database_path)
        cur = conn.cursor()
        sql = f"UPDATE main set status='unavailable' where urls='{urls}'"  # 手搓sql语句
        cur.execute(sql)  # 执行
        conn.commit()  # 提交事务
        conn.close()  # 关闭连接

    async def get_setu(
        self,
        matcher: Matcher,
        keywords: List[str],
        num: int = 1,
        r18: bool = False,
        quality: int = 75,
    ) -> List[list]:
        """
        返回列表,内容为setu消息(列表套娃)
        [
            [图片(bytes), data(图片信息), True(是否拿到了图), setu_url],
            [Error(错误), message(错误信息), False(是否拿到了图), setu_url]
        ]
        """
        data = []
        conn = sqlite3.connect(self.database_path)  # 连接数据库
        cur = conn.cursor()
        # sql操作,根据keyword和r18进行查询拿到数据
        if not keywords:
            sql = f"SELECT pid,title,author,r18,tags,urls from main where r18='{r18}' and status!='unavailable' order by random() limit {num}"
        elif len(keywords) == 1:
            sql = f"SELECT pid,title,author,r18,tags,urls from main where (tags like '%{keywords[0]}%' or title like '%{keywords[0]}%' or author like '%{keywords[0]}%') and r18='{r18}' and status!='unavailable' order by random() limit {num}"
        else:  # 多tag的情况下的sql语句
            tag_sql = "".join(
                f"tags like '%{i}%'" if i == keywords[-1] else f"tags like '%{i}%' and "
                for i in keywords
            )
            sql = f"SELECT pid,title,author,r18,tags,urls from main where (({tag_sql}) and r18='{r18}' and status!='unavailable') order by random() limit {num}"
        db_data = cur.execute(sql).fetchall()
        # 断开数据库连接
        conn.close()
        # 如果没有返回结果
        if db_data == []:
            await matcher.finish(f"图库中没有搜到关于{keywords}的图。")
        # 并发下载图片
        async with AsyncClient() as client:
            tasks = [
                self.pic(setu, quality, client, pm.read_proxy()) for setu in db_data
            ]
            data = await asyncio.gather(*tasks)
        return data

    async def pic(
        self, setu: list, quality: int, client: AsyncClient, setu_proxy: str
    ) -> list:
        """
        返回setu消息列表
        [Error(错误), message(错误信息), False(是否拿到了图), setu_url]
        或者
        [图片(bytes), data(图片信息), True(是否拿到了图), setu_url]
        """
        setu_pid = setu[0]  # pid
        setu_title = setu[1]  # 标题
        setu_author = setu[2]  # 作者
        setu_r18 = setu[3]  # r18
        setu_tags: str = setu[4]  # 标签
        setu_url: str = setu[5].replace("i.pixiv.re", setu_proxy)  # 图片url

        data = f"标题:{setu_title}" + "\npid:" + str(setu_pid) + "\n画师:" + setu_author

        logger.info("\n" + data + "\ntags:" + setu_tags + "\nR18:" + setu_r18)  # 打印信息
        file_name = setu_url.split("/")[-1]  # 获取文件名

        # 判断文件是否本地存在
        is_in_all_file_name = file_name in self.all_file_name
        if is_in_all_file_name:
            logger.info("图片本地存在")
            try:
                image = Image.open(f"{self.save_path}/{file_name}")  # 尝试打开图片
            except Exception as e:
                return [
                    "Error",
                    f"本地图片打开失败, 错误信息: {repr(e)}\nfile_name:{file_name}",
                    False,
                    setu_url,
                ]
        else:
            logger.info(f"图片本地不存在,正在去{setu_proxy}下载")
            content: Union[bytes, int] = await download_pic(setu_url, client)
            if isinstance(content, int):  # 如果返回的是int, 那么就是状态码, 表示下载失败
                if (
                    content == 404
                ):  # 如果是404, 404表示文件不存在, 说明作者删除了图片, 那么就把这个url的status改为unavailable, 下次sql操作的时候就不会再拿到这个url了
                    await self.update_status_unavailable(
                        setu[5]
                    )  # setu[5]是原始url, 不能拿换过代理的url
                logger.error(f"图片下载失败, 状态码: {content}")  # 返回错误信息
                return ["Error", f"图片下载失败, 状态码: {content}", False, setu_url]
            # 错误处理, 如果content是空bytes, 那么Image.open会报错, 跳到except, 如果能打开图片, 图片应该不成问题,
            try:
                image = Image.open(BytesIO(content))  # 打开图片
            except Exception as e:
                return ["Error", f"图片打开失败, 错误信息: {repr(e)}", False, setu_url]
            # 保存图片, 如果save_path不为空, 以及图片不在all_file_name中, 那么就保存图片
            if self.save_path:
                try:
                    with open(f"{self.save_path}/{file_name}", "wb") as f:
                        f.write(content)
                    self.all_file_name.append(file_name)
                except Exception as e:
                    logger.error(f"图片存储失败: {repr(e)}")
        try:
            # 尝试修改图片
            pic = await self.change_pixel(image, quality)
            return [pic, data, True, setu_url]
        except Exception as e:
            return ["Error", f"图片处理失败: {repr(e)}", False, setu_url]


# 实例化
get_data = GetData()
