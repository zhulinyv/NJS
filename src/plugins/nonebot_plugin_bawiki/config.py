import json
from pathlib import Path
from typing import Optional

from nonebot import get_available_plugin_names, get_driver, logger
from pil_utils.fonts import get_proper_font
from pydantic import BaseModel, validator


class Cfg(BaseModel):
    ba_proxy: Optional[str] = None
    ba_gacha_cool_down: int = 0

    ba_gamekee_url = "https://ba.gamekee.com/"
    ba_schale_url = "https://schale.lgc.cyberczy.xyz/"
    ba_schale_mirror_url = "https://schale.lgc.cyberczy.xyz/"
    ba_bawiki_db_url = "https://bawiki.lgc.cyberczy.xyz/"

    @validator("ba_gamekee_url", allow_reuse=True)  # type: ignore
    @validator("ba_schale_url", allow_reuse=True)  # type: ignore
    @validator("ba_schale_mirror_url", allow_reuse=True)  # type: ignore
    @validator("ba_bawiki_db_url", allow_reuse=True)  # type: ignore
    def _(cls, val: str):  # noqa: N805
        if not ((val.startswith(("https://", "http://"))) and val.endswith("/")):
            raise ValueError('自定义的 URL 请以 "http(s)://" 开头，以 "/" 结尾')


config = Cfg.parse_obj(get_driver().config.dict())


# 给 PicMenu 用户上个默认字体
def set_pic_menu_font():
    pic_menu_dir = Path.cwd() / "menu_config"
    pic_menu_config = pic_menu_dir / "config.json"

    if not pic_menu_dir.exists():
        pic_menu_dir.mkdir(parents=True)

    if (not pic_menu_config.exists()) or (
        json.loads(pic_menu_config.read_text(encoding="u8")).get("default")
        == "font_path"
    ):
        path = str(get_proper_font("国").path.resolve())
        pic_menu_config.write_text(json.dumps({"default": path}), encoding="u8")
        logger.info("检测到 PicMenu 已加载并且未配置字体，已自动帮您配置系统字体")


if "nonebot_plugin_PicMenu" in get_available_plugin_names():
    try:
        set_pic_menu_font()
    except:
        logger.exception("配置 PicMenu 字体失败")
