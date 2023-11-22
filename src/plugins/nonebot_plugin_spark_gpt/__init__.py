from __future__ import annotations
from nonebot import require

require("nonebot_plugin_htmlrender")
require("nonebot_plugin_templates")
require("nonebot_plugin_web_config")
require("nonebot_plugin_alconna")
require("nonebot_plugin_bind")

from . import nonebot  # noqa: F401, E402
from .chatbots import chatbots  # noqa: F401, E402
from .type_store import users  # noqa: F401, E402
