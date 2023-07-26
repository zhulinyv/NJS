from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    imagetools_zip_threshold: int = 20
    """
    输出图片数量大于该数目时，打包为zip以文件形式发送
    """
    max_forward_msg_num: int = 99
    """
    合并转发消息条数上限
    """


imagetools_config = Config.parse_obj(get_driver().config.dict())
