import pytest
from nonebug import App
from nonebot.adapters.onebot.v11 import MessageSegment
from .utils import make_fake_message, make_fake_event


@pytest.mark.asyncio
async def test_open_recruitment(app: App):
    from plugins.nonebot_plugin_arktools.src.tool_open_recruitment import recruit

    Message = make_fake_message()
    async with app.test_matcher(recruit) as ctx:
        bot = ctx.create_bot()
        msg = Message("/公招 高资")
        event = make_fake_event(_message=msg)()

        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "识别中...", True)
