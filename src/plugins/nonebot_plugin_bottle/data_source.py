try:
    import ujson as json
except:
    import json

import re
import time
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

import httpx
import aiofiles
from nonebot.log import logger
from pydantic import parse_obj_as
from sqlalchemy import func, text, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_datastore.db import get_engine, post_db_init, create_session

from .model import Bottle, Report, Comment
from .config import api_key, secret_key, local_storage

data_dir = Path("data/bottle")
if local_storage:
    cache_dir = data_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)


# https://github.com/noneplugin/nonebot-plugin-chatrecorder
async def cache_file(msg: Message):
    async with httpx.AsyncClient() as client:
        await asyncio.gather(
            *[cache_image_url(seg, client) for seg in msg if seg.type == "image"]
        )


async def cache_image_url(seg: MessageSegment, client: httpx.AsyncClient):
    if url := seg.data.get("url"):
        try:
            r = await client.get(url)
            data = r.content
        except httpx.TimeoutException:
            return
        seg.type = "cached_image"
        seg.data.clear()
    else:
        return
    hash = hashlib.md5(data).hexdigest()
    filename = f"{hash}.cache"
    cache_file_path = cache_dir / filename
    cache_files = [f.name for f in cache_dir.iterdir() if f.is_file()]
    if filename not in cache_files:
        async with aiofiles.open(cache_file_path, "wb") as f:
            await f.write(data)
    seg.data = {"file": filename}


async def serialize_message(message: Message) -> List[Dict[str, Any]]:
    if local_storage:
        await cache_file(message)
    return [seg.__dict__ for seg in message]


def deserialize_message(message: List[Dict[str, Any]]) -> Message:
    for seg in message:
        if seg["type"] == "cached_image":
            seg["type"] = "image"
            seg["data"]["file"] = (cache_dir / seg["data"]["file"]).resolve().as_uri()
    return parse_obj_as(Message, message)


def get_content_preview(bottle: Bottle) -> str:
    message_parts = deserialize_message(bottle.content)
    content_preview = ""
    for part in message_parts:
        if part.type == "text":
            # 文字截取
            text = part.data["text"]
            content_preview += text[:20] + "..." if len(text) > 20 else text
        elif part.type == "image":
            # 图片处理
            content_preview += "[图片]"
    return content_preview


@post_db_init
async def _():
    old_data = data_dir / "data.json"
    if old_data.exists():
        logger.info("开始迁移旧漂流瓶数据")
        with open(old_data, "r", encoding="utf-8") as f:
            data = json.load(f)
        async with create_session() as session:
            offset = (await session.scalar(func.max(Bottle.id))) or 0 + 1
            for idx, i in enumerate(data):
                # 旧版json兼容 - 评论
                isOldVersion = False
                commentnew = []
                for index, value in enumerate(i["comment"]):
                    if isinstance(value, str):
                        isOldVersion = True
                        commentnew.append([0, value])
                if isOldVersion:
                    i["comment"] = commentnew

                # 旧版json兼容 - 时间time、举报者
                i.setdefault("time", time.strftime("%Y-%m-%d %H:%M:%S"))
                if i["time"] == "0000-00-00 00:00:00":
                    i["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                i.setdefault("reported", [])
                bottle = Bottle(
                    user_id=i["user"],
                    group_id=i["group"],
                    user_name=i["user_name"],
                    group_name=i["group_name"],
                    content=await serialize_message(Message(i["text"])),
                    report=i["report"],
                    picked=i["picked"],
                    is_del=i["del"],
                    time=datetime.strptime(i["time"], "%Y-%m-%d %H:%M:%S"),
                )
                session.add(bottle)
                for comment in i.get("comment", []):
                    new_comment = Comment(
                        user_id=comment[0],
                        user_name=re.split("[:：]", comment[1])[0],
                        content=re.split("[:：]", comment[1])[1],
                        bottle_id=idx + offset,
                    )
                    session.add(new_comment)
                for report in i.get("reported", []):
                    new_report = Report(user_id=report, bottle_id=idx + offset)
                    session.add(new_report)
            await session.commit()
            old_data.rename(data_dir / "data.json.old")
            logger.info("旧漂流瓶数据迁移完成")


class BottleManager:
    def __init__(self) -> None:
        pass

    async def get_bottle(
        self, index: int, session: AsyncSession, include_del: bool = False
    ) -> Optional["Bottle"]:
        """获取一个瓶子

        Args:
            index (int): 瓶子序号
            session (AsyncSession): 会话
            include_del (bool) : 是否包括被删除的瓶子
        """
        if not include_del:
            return await session.scalar(
                select(Bottle).where(Bottle.id == index, Bottle.is_del == False)
            )
        else:
            return await session.scalar(select(Bottle).where(Bottle.id == index))

    async def add_bottle(
        self,
        user_id: int,
        group_id: int,
        content: List[Dict[str, Any]],
        user_name: str,
        group_name: str,
        session: AsyncSession,
    ) -> int:
        """添加漂流瓶

        Args:
            user_id (int): 用户id
            group_id (int): 群id
            content (str): 内容
            user_name (str): 用户名
            group_name (str): 群名
            session (AsyncSession): 会话

        Returns:
            int: 漂流瓶id
        """
        bottles = await session.scalars(
            select(Bottle).where(Bottle.user_id == user_id, Bottle.group_id == group_id)
        )
        for bottle in bottles:
            if bottle.content == content:
                logger.warning("添加失败！")
                return 0
        else:
            bottle = Bottle(
                user_id=user_id,
                group_id=group_id,
                content=content,
                user_name=user_name,
                group_name=group_name,
            )
            session.add(bottle)
            await session.commit()
            await session.refresh(bottle)
            return bottle.id

    async def select(self, session: AsyncSession) -> Optional[Bottle]:
        """随机选择一个漂流瓶

        Args:
            session (AsyncSession): 会话

        Returns:
            Optional[Bottle]: 随机一个瓶子
        """
        bottle = await session.scalar(
            select(Bottle)
            .where(Bottle.is_del == False)
            .order_by(func.random())
            .limit(1)
        )
        if bottle:
            bottle.picked += 1
        return bottle

    async def clear(self, session: AsyncSession) -> None:
        """清空漂流瓶

        Args:
            session (AsyncSession): 会话
        """
        engine = get_engine()
        for table in [
            "nonebot_plugin_bottle_bottle",
            "nonebot_plugin_bottle_comment",
            "nonebot_plugin_bottle_report",
        ]:
            if engine.name == "sqlite":
                await session.execute(text(f"DELETE FROM {table}"))
            elif engine.name == "postgresql":
                await session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY"))
            else:
                await session.execute(text(f"TRUNCATE TABLE {table}"))

    async def report(
        self, bottle: Bottle, user_id: int, session: AsyncSession, times_max: int = 5
    ) -> int:
        """
        举报漂流瓶
        `index`: 漂流瓶编号
        `timesMax`: 到达此数值自动处理

        返回
        0 举报失败
        1 举报成功
        2 举报成功并且已经自动处理
        3 已经删除
        """
        if await session.scalar(
            select(Report).where(
                Report.user_id == user_id, Report.bottle_id == bottle.id
            )
        ):
            return 0
        if bottle.is_del:
            return 3
        bottle.report += 1
        if bottle.report >= times_max:
            bottle.is_del = True
            return 2
        else:
            new_report = Report(user_id=user_id, bottle_id=bottle.id)
            session.add(new_report)
            return 1

    def comment(
        self,
        bottle: Bottle,
        user_id: int,
        user_name: str,
        content: str,
        session: AsyncSession,
    ) -> None:
        """评论漂流瓶

        Args:
            bottle (Bottle): 瓶子
            user_id (int): 用户id
            user_name (str): 用户名
            content (str): 内容
            session (AsyncSession): 会话
        """
        new_comment = Comment(
            user_id=user_id, user_name=user_name, content=content, bottle_id=bottle.id
        )
        session.add(new_comment)

    async def get_comment(
        self,
        bottle: Bottle,
        session: AsyncSession,
        limit: Optional[int] = 3,
    ) -> Sequence[Comment]:
        """获取评论

        Args:
            bottle (Bottle): 瓶子
            session (AsyncSession): 会话
            limit (Optional[int], optional): 评论个数. Defaults to 3.

        Returns:
            Sequence[Comment]: 评论们
        """
        return (
            await session.scalars(
                statement=select(Comment)
                .where(Comment.bottle_id == bottle.id)
                .order_by(Comment.time.desc())
                .limit(limit)
            )
        ).all()

    async def del_comment(self, bottle: Bottle, user_id: int, session: AsyncSession):
        """删除瓶子中用户id的所有评论

        Args:
            bottle (Bottle): 瓶子
            user_id (int): 用户id
            session (AsyncSession): 会话
        """
        comments = await session.scalars(
            statement=select(Comment).where(
                Comment.bottle_id == bottle.id, Comment.user_id == user_id
            )
        )
        for comment in comments:
            await session.delete(comment)

    async def list_bottles(
        self, user_id: int, session: AsyncSession, include_del: bool = False
    ) -> Sequence[Bottle]:
        """获取用户扔出的所有漂流瓶

        Args:
            user_id (int): 用户ID
            session (AsyncSession): 数据库会话
            include_del (bool) : 是否包括被删除的瓶子

        Returns:
            Sequence[Bottle]: 用户扔出的所有漂流瓶
        """
        whereclause = [Bottle.user_id == user_id]
        if not include_del:
            whereclause.append(Bottle.is_del == False)
        return (
            await session.scalars(
                select(Bottle).where(*whereclause).order_by(Bottle.id)
            )
        ).all()


bottle_manager = BottleManager()


class Audit(object):
    bannedMessage = ""

    def __init__(self) -> None:
        self.data_path = Path("data/bottle/permissionsList.json").absolute()
        self.data_dir = Path("data/bottle").absolute()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.__data = {
            "enableCooldown": True,
            "cooldownTime": 30,
            "bannedMessage": "",
            "user": [],
            "group": [],
            "cooldown": {},
            "disreportable": [],
            "whiteUser": [],
            "whiteGroup": [],
        }
        self.__load()

    def __load(self):
        try:
            with self.data_path.open("r+", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            with self.data_path.open("w+", encoding="utf-8") as f:
                json.dump(self.__data, f)
            logger.success(f"在 {self.data_path} 成功创建漂流瓶黑名单数据库")
        else:
            self.__data.update(data)
            self.bannedMessage = self.__data["bannedMessage"]

    def __save(self) -> None:
        with self.data_path.open("w+", encoding="utf-8") as f:
            f.write(json.dumps(self.__data, ensure_ascii=False, indent=4))

    def add(self, mode, num):
        """
        添加权限
        `mode`:
            `group`: 群号
            `user`: QQ号
            `cooldown`: 暂时冷却QQ号
            `whiteUser`: 白名单QQ号
            `whiteGroup`: 白名单群号
        `num`: QQ/QQ群号
        """
        num = str(num)
        try:
            if mode != "cooldown" and num not in self.__data[mode]:
                self.__data[mode].append(num)
            elif (
                not (self.checkWhite("whiteUser", num) or self.check("whiteGroup", num))
                and self.__data["enableCooldown"]
                and mode == "cooldown"
            ):
                self.__data["cooldown"][num] = (
                    int(time.time()) + self.__data["cooldownTime"]
                )
            else:
                return False
            self.__save()
            return True
        except Exception as e:
            logger.warning(e)
            return False

    def remove(self, mode, num):
        """
        移除黑名单
        `mode`:
            `group`: 群号
            `user`: QQ号
            `whiteUser`: 白名单QQ号
            `whiteGroup`: 白名单群号
        `num`: QQ/QQ群号
        """
        num = str(num)
        try:
            self.__data[mode].remove(num)
            self.__save()
            return True
        except:
            return False

    def verify(self, user, group):
        """
        返回是否通过验证(白名单优先)
        `user`: QQ号
        `group`: 群号

        返回：
            `True`: 通过
            `False`: 未通过
        """
        if not (
            self.checkWhite("whiteUser", user) or self.checkWhite("whiteGroup", group)
        ):
            if (
                self.check("user", user)
                or self.check("group", group)
                or self.check("cooldown", user)
            ):
                return False
        return True

    def verifyReport(self, qq):
        """
        检查是否有举报权限

        返回：
            `True`: 具有权限
            `False`： 不具有权限
        """
        if str(qq) in self.__data["disreportable"]:
            return False
        else:
            return True

    def check(self, mode, num):
        """
        查找是否处于黑名单
        `mode`:
            `group`: 群号
            `user`: QQ号
            `cooldown`: 暂时冷却QQ号
        `num`: QQ/QQ群号
        """
        num = str(num)
        if mode in ["group", "user"]:
            if num in self.__data[mode]:
                return True
        else:
            if num in self.__data[mode]:
                if time.time() <= self.__data[mode][num]:
                    return True
        return False

    def checkWhite(self, mode, num: str):
        """
        检查是否为白名单
        `mode`:
            `whiteUser`: 白名单QQ号
            `whiteGroup`: 白名单群号
        `num`: QQ/QQ群号
        """
        num = str(num)
        if mode == "whiteUser" and num in self.__data["whiteUser"]:
            return True
        elif mode == "whiteGroup" and num in self.__data["whiteGroup"]:
            return True
        else:
            return False

    def banreport(self, qq):
        """
        删除/恢复某人的举报权限
        `qq`: QQ号
        返回:
            `0`: 成功解封
            `1`: 成功封禁
            `e`: 错误信息
        """
        try:
            if qq not in self.__data["disreportable"]:
                self.__data["disreportable"].append(qq)
                self.__save()
                return 1
            else:
                self.__data["disreportable"].remove(qq)
                self.__save()
                return 0
        except Exception as e:
            return e


ba = Audit()

cursepath = Path("data/bottle/curse.json").absolute()


async def text_audit(text: str, ak=api_key, sk=secret_key):
    """
    文本审核(百度智能云)
    `text`: 待审核文本
    `ak`: api_key
    `sk`: secret_key
    """
    if (not api_key) or (not secret_key):
        # 未配置key 进行简单违禁词审核
        try:
            async with aiofiles.open(cursepath, "r", encoding="utf-8") as f:
                for i in json.loads(await f.read()):
                    if i in text:
                        return {"conclusion": "不合规", "data": [{"msg": f"触发违禁词 {i}"}]}
                return "pass"
        except:
            if not cursepath.exists():
                with cursepath.open("w+", encoding="utf-8") as f:
                    f.write("[]")
                return "pass"
            else:
                return "Error"
    # access_token 获取
    host = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}"
    async with httpx.AsyncClient() as client:
        response = await client.get(host)
        if response:
            access_token = response.json()["access_token"]
        else:
            # 未返回access_token 返回错误
            return "Error"

        request_url = (
            "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined"
        )
        params = {"text": text}
        request_url = request_url + "?access_token=" + access_token
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = await client.post(request_url, data=params, headers=headers)
        if response:
            return response.json()
        else:
            # 调用审核API失败
            return "Error"
