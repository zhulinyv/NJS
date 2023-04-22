# UP主信息类
class UpInfo(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Stat(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# 视频信息类
class VideoInfo:
    def __init__(
        self,
        title: str,
        pictureUrl: str,
        desc: str,
        pubdate: int,
        upInfo: dict,
        stat: dict,
        shareUrl: str,
    ) -> None:
        self.title = title
        self.pic = pictureUrl
        self.desc = desc
        self.pubdate = pubdate
        self.upInfo = UpInfo(**upInfo)
        self.shareUrl = shareUrl
        self.stat = Stat(**stat)
