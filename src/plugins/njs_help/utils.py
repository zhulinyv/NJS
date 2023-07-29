import io
import os
import nonebot
import ujson as json

from PIL import Image
from pathlib import Path
from nonebot import require

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import md_to_pic
require("nonebot_plugin_imageutils")
from nonebot_plugin_imageutils import text2image


try:
    NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]
except Exception:
    NICKNAME: str = "脑积水"


if not os.path.exists("./data/njs_help_new/"):
    # 不存在就创建文件
    os.makedirs("./data/njs_help_new/")
    help_data = {
        "帮助说明":{
            "插件名": "插件的名字, 可以随便起",
            "导包名": "插件加载的名字, 这个后续会和 nonebot_plugin_manager 对接",
            "显示颜色": "[绿色/蓝色/红色]三选一, 后续可能会支持自定义 RGB , 但感觉不是很必要",
            "帮助文字": "直接填写, 换行等请使用转义字符 \n 等, 转义字符参考: https://zhuanlan.zhihu.com/p/598923346",
            "帮助图片": "填写相对于 bot.py 的*相对路径*, 开头可省略 ./ , 例如: ./data/.../*.png --> data/.../*.png , 不可以填绝对路径",
            "帮助文档": "填写相对于 bot.py 的*相对路径*, 支持大部分 Markdown 语法, 其它要求请见: https://github.com/kexue-z/nonebot-plugin-htmlrender/blob/master/docs/example.md",
            "BBcode": "格式请见: https://github.com/noneplugin/nonebot-plugin-imageutils#%E4%BD%BF%E7%94%A8%E7%A4%BA%E4%BE%8B", 
            "其它说明": "不需要的插件帮助请直接删除, 额外添加的插件帮助请按照上述内容或仿照其它插件帮助填写, 各种格式的文档没必要都写, 不需要的直接留空即可, 但请不要删除" 
        },
        "插件列表": [
            {
                "插件名": "",
                "导包名": "",
                "显示颜色": "",
                "帮助文字": "",
                "帮助图片": "",
                "帮助文档": "",
                "BBcode": ""
            }
        ]
    }
    with open("./data/njs_help_new/help.json", "w", encoding="utf-8") as f:
        json.dump(help_data, f, indent=4, ensure_ascii=False)


head_msg = """以下仅为功能名称, 并非指令！
发送"njs+对应序号或名称"查看指令捏~
发送"njs+对应序号或名称"查看指令捏~
发送"njs+对应序号或名称"查看指令捏~
(重要的事情说三遍！！！)"""


foot_msg = """文档地址: 《脑积水使用手册》
优先: zhulinyv.github.io/NJS
仓库: github.com/zhulinyv/NJS/wiki
备用: cnblogs.com/xytpz/p/NJS.html"""


# 当前路径
path = Path(__file__).parent


# BBcode 帮助绘制
async def bbcode(bbcode):
    bbcode_img = text2image(bbcode)
    bbcode_img.save(path / "bbcode_img.png")


# Markdown 帮助绘制
async def md(md):
    with open(md, "r", encoding="utf-8") as markdown:
        markdown = markdown.read()
    markdown_img = await md_to_pic(md=markdown)
    img = Image.open(io.BytesIO(markdown_img))
    img.save(path / "markdown_img.png")