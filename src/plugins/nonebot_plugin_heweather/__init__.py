from typing import Tuple

from nonebot import on_regex, get_driver
from nonebot.log import logger
from nonebot.params import RegexGroup
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import Config
from .render_pic import render
from .weather_data import Weather, ConfigError, CityNotFoundError

plugin_config = Config.parse_obj(get_driver().config.dict())

if plugin_config.qweather_apikey and plugin_config.qweather_apitype:
    api_key = plugin_config.qweather_apikey
    api_type = int(plugin_config.qweather_apitype)
else:
    raise ConfigError("请设置 qweather_apikey 和 qweather_apitype")


if plugin_config.debug:
    DEBUG = True
    logger.debug("将会保存图片到 weather.png")
else:
    DEBUG = False

weather = on_regex(r".*?(.*)天气(.*).*?", priority=1)


@weather.handle()
async def _(matcher: Matcher, args: Tuple[str, ...] = RegexGroup()):
    city = args[0].strip() or args[1].strip()
    await weather.send("少女观星中...", at_sender=True)
    if not city:
        await weather.finish("地点是...空气吗?? >_<")

    w_data = Weather(city_name=city, api_key=api_key, api_type=api_type)
    try:
        await w_data.load_data()
    except CityNotFoundError:
        matcher.block = False
        await weather.finish(f"未查询到{city}的天气哦~")

    img = await render(w_data)

    if DEBUG:
        debug_save_img(img)

    await weather.finish(MessageSegment.image(img))


def debug_save_img(img: bytes) -> None:
    from io import BytesIO

    from PIL import Image

    logger.debug("保存图片到 weather.png")
    a = Image.open(BytesIO(img))
    a.save("weather.png", format="PNG")
