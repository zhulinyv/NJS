from pathlib import Path
from typing import Union

from .update import update_from_git

# from PIL import Image, ImageDraw


# from ..l4d2_image.image import convert_img
# from ..l4d2_image.image import get_color_bg
# from ..utils.genshin_fonts.genshin_fonts import genshin_font_origin

R_PATH = Path(__file__).parent
TEXT_PATH = R_PATH / "texture2d"

# gs_font_30 = genshin_font_origin(30)
black_color = (24, 24, 24)

log_config = {
    "key": "✨🐛🎨⚡🍱♻️",
    "num": 18,
}

log_map = {"✨": "feat", "🐛": "bug", "🍱": "bento", "⚡️": "zap", "🎨": "art"}


async def draw_update_log_img(
    level: int = 0,
    repo_path: Union[str, Path, None] = None,
    is_update: bool = True,
) -> Union[bytes, str]:
    log_list = await update_from_git(level, repo_path, log_config, is_update)
    if len(log_list) == 0:
        return (
            "更新失败!更多错误信息请查看控制台...\n"
            ">> 可以尝试使用\n"
            ">> [l4强制更新](危险)\n"
            ">> [l4强行强制更新](超级危险)!"
        )

    result = "L4D2Bot 更新记录\n\n"
    for log in log_list:
        result += f"- {log}\n"

    return result
