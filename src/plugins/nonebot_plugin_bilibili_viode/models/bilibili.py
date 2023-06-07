import time

from httpx import AsyncClient
from pydantic import BaseModel
from ..utils import get_share_sort_url


class Owner(BaseModel):
    mid: int  # UP主ID
    name: str  # UP主名
    face: str  # UP主头像URL
    follower: int = 0  # UP主粉丝数

    async def get_follower(self):
        url = "https://api.bilibili.com/x/relation/stat"
        params = {"vmid": self.mid}
        async with AsyncClient() as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            self.follower = data["data"]["follower"]


class Stat(BaseModel):
    view: int  # 播放量
    danmaku: int  # 弹幕数
    favorite: int  # 收藏数
    like: int  # 点赞数
    coin: int  # 硬币数
    share: int  # 分享数


class VideoInfo(BaseModel):
    """
    视频信息
    """
    bvid: str = None  # 视频BV号
    aid: int = None  # 视频AV号
    title: str = None  # 视频标题
    desc: str = None  # 视频简介
    pic: str = None  # 视频封面URL
    pubdate: int = None  # 视频发布时间戳
    duration: int = None  # 视频时长
    owner: Owner = None  # UP主信息
    stat: Stat = None  # 视频统计信息
    share_url: str = None  # 视频分享链接

    def time_format(self) -> str:
        """
        格式化时间
        :return: 格式化后的时间
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.pubdate))

    @classmethod
    async def get(cls, aid: int = None, bvid: str = None):
        """
        获取视频信息
        :param aid: 视频AV号
        :param bvid: 视频BV号
        :return: 视频信息
        """
        if aid is None and bvid is None:
            raise ValueError("aid and bvid cannot be None at the same time")
        if bvid:
            params = {"bvid": bvid}
        else:
            params = {"aid": aid}
        async with AsyncClient() as client:
            url = "https://api.bilibili.com/x/web-interface/view"
            resp = await client.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data["code"] == 0:
                    result = cls(**data["data"])
                    await result.owner.get_follower()
                    result.share_url = await get_share_sort_url(result.aid)
                    return result
        raise ValueError("Get video info failed")
