from pathlib import Path

import aiofiles
import markdown
from jinja2 import Environment, FileSystemLoader
from nonebot_plugin_htmlrender import html_to_pic
from nonebot_plugin_templates.templates_render import Font_Path

TEMPLATES_PATH = Path(__file__).parent / "templates"
env = Environment(
    extensions=["jinja2.ext.loopcontrols"],
    loader=FileSystemLoader(str(TEMPLATES_PATH)),
    enable_async=True,
)
text_template = env.get_template("markdown.html")


async def read_file(path: str) -> str:
    async with aiofiles.open(path, mode="r") as f:
        return await f.read()


async def read_tpl(path: str) -> str:
    return await read_file(f"{TEMPLATES_PATH}/{path}")


async def md_to_pic(md: str, width: int = 600, font_path: str = Font_Path):
    md = md.replace("\n", "  \n")
    if md.count("```") % 2 == 1:
        md += "  \n```"
    md = markdown.markdown(
        md,
        extensions=[
            "pymdownx.tasklist",
            "tables",
            "fenced_code",
            "codehilite",
            "mdx_math",
            "pymdownx.tilde",
        ],
        extension_configs={"mdx_math": {"enable_dollar_delimiter": True}},
    )

    extra = ""
    if "math/tex" in md:
        katex_css = await read_tpl("katex/katex.min.b64_fonts.css")
        katex_js = await read_tpl("katex/katex.min.js")
        mathtex_js = await read_tpl("katex/mathtex-script-type.min.js")
        extra = (
            f'<style type="text/css">{katex_css}</style>'
            f"<script defer>{katex_js}</script>"
            f"<script defer>{mathtex_js}</script>"
        )

    css = await read_tpl("markdown.css") + await read_tpl("pygments-default.css")
    html = await text_template.render_async(
        md=md, font_path=font_path, css=css, extra=extra
    )
    # with open(Path() / "temp.html", "w") as f:
    #     f.write(html)
    return await html_to_pic(
        html=html,
        viewport={"width": width, "height": 10},
    )
