import io
import os
import time as t
import nonebot
from pathlib import Path
from nonebot import on_command
from nonebot_plugin_imageutils import text2image
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    MessageSegment,
    GroupMessageEvent,
    PrivateMessageEvent
    )

from .utils import *

try:
    NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]
except Exception:
    NICKNAME: str = "脑积水"



help = on_command('njs help', aliases={'njs帮助', 'njs菜单', 'njs列表', 'njshelp'}, priority=1, block=True)
@help.handle()
async def help_handle(event:Event, bot:Bot):
    # 转为图片发送
    img = text2image(help_reply_body)
    output = io.BytesIO()
    img.save(output, format="png")
    image = MessageSegment.image(output)
    # 私聊直接发送
    if isinstance(event, PrivateMessageEvent):
        await help.send(help_reply_head)
        t.sleep(0.5)
        await help.send(image)
        t.sleep(0.5)
        await help.send(help_reply_foot)
    # 群聊转发
    elif isinstance(event, GroupMessageEvent):
        msgs = []
        message_list = []
        message_list.append(help_reply_head)
        message_list.append(image)
        message_list.append(help_reply_foot)
        for msg in message_list:
            msgs.append({
                'type': 'node',
                'data': {
                    'name': f"{NICKNAME}",
                    'uin': bot.self_id,
                    'content': msg
                }
            })
        await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)

h1 = on_command('njs1', priority=2, block=True)
@h1.handle()
async def test_handle(event:Event):
    h1_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h1.jpg"
    if isinstance(event, GroupMessageEvent):
        await h1.finish('\n' + MessageSegment.image(h1_img), at_sender=True)
    else:
        await h1.finish(MessageSegment.image(h1_img))

h2 = on_command('njs2', priority=2, block=True)
@h2.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h2.finish('\n' + h2_r, at_sender=True)
    else:
        await h2.finish(h2_r)

h3 = on_command('njs3', priority=2, block=True)
@h3.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h3.finish('\n' + h3_r, at_sender=True)
    else:
        await h3.finish(h3_r)

h4 = on_command('njs4', priority=2, block=True)
@h4.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h4.finish('\n' + h4_r, at_sender=True)
    else:
        await h4.finish(h4_r)

h5 = on_command('njs5', priority=2, block=True)
@h5.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h5.finish('\n' + h5_r, at_sender=True)
    else:
        await h5.finish(h5_r)

h6 = on_command('njs6', priority=2, block=True)
@h6.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h6.finish('\n' + h6_r, at_sender=True)
    else:
        await h6.finish(h6_r)

h7 = on_command('njs7', priority=2, block=True)
@h7.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h7.finish('\n' + h7_r, at_sender=True)
    else:
        await h7.finish(h7_r)

h8 = on_command('njs8', priority=2, block=True)
@h8.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h8.finish('\n' + h8_r, at_sender=True)
    else:
        await h8.finish(h8_r)

h9 = on_command('njs9', priority=2, block=True)
@h9.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h9.finish('\n' + h9_r, at_sender=True)
    else:
        await h9.finish(h9_r)

h10 = on_command('njs10', priority=2, block=True)
@h10.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h10.finish('\n' + h10_r, at_sender=True)
    else:
        await h10.finish(h10_r)

h11 = on_command('njs11', priority=2, block=True)
@h11.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h11.finish('\n' + h11_r, at_sender=True)
    else:
        await h11.finish(h11_r)

h12 = on_command('njs12', priority=2, block=True)
@h12.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h12.finish('\n' + h12_r, at_sender=True)
    else:
        await h12.finish(h12_r)

h13 = on_command('njs13', priority=2, block=True)
@h13.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h13.finish('\n' + h13_r, at_sender=True)
    else:
        await h13.finish(h13_r)

h14 = on_command('njs14', priority=2, block=True)
@h14.handle()
async def test_handle(event:Event):
    h14_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h14.jpg"
    if isinstance(event, GroupMessageEvent):
        await h14.finish('\n' + MessageSegment.image(h14_img), at_sender=True)
    else:
        await h14.finish(MessageSegment.image(h14_img))

h15 = on_command('njs15', priority=2, block=True)
@h15.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h15.finish('\n' + h15_r, at_sender=True)
    else:
        await h15.finish(h15_r)

h16 = on_command('njs16', priority=2, block=True)
@h16.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h16.finish('\n' + h16_r, at_sender=True)
    else:
        await h16.finish(h16_r)

h17 = on_command('njs17', priority=2, block=True)
@h17.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h17.finish('\n' + h17_r, at_sender=True)
    else:
        await h17.finish(h17_r)

h18 = on_command('njs18', priority=2, block=True)
@h18.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h18.finish('\n' + h18_r, at_sender=True)
    else:
        await h18.finish(h18_r)

h19 = on_command('njs19', priority=2, block=True)
@h19.handle()
async def test_handle(event:Event):
    h19_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h19.png"
    if isinstance(event, GroupMessageEvent):
        await h19.finish('\n' + MessageSegment.image(h19_img), at_sender=True)
    else:
        await h19.finish(MessageSegment.image(h19_img))

h20 = on_command('njs20', priority=2, block=True)
@h20.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h20.finish('\n' + h20_r, at_sender=True)
    else:
        await h20.finish(h20_r)

h21 = on_command('njs21', priority=2, block=True)
@h21.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h21.finish('\n' + h21_r, at_sender=True)
    else:
        await h21.finish(h21_r)

h22 = on_command('njs22', priority=2, block=True)
@h22.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h22.finish('\n' + h22_r, at_sender=True)
    else:
        await h22.finish(h22_r)

h23 = on_command('njs23', priority=2, block=True)
@h23.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h23.finish('\n' + h23_r, at_sender=True)
    else:
        await h23.finish(h23_r)

h24 = on_command('njs24', priority=2, block=True)
@h24.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h24.finish('\n' + h24_r, at_sender=True)
    else:
        await h24.finish(h24_r)

h25 = on_command('njs25', priority=2, block=True)
@h25.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h25.finish('\n' + h25_r, at_sender=True)
    else:
        await h25.finish(h25_r)

h26 = on_command('njs26', priority=2, block=True)
@h26.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h26.finish('\n' + h26_r, at_sender=True)
    else:
        await h26.finish(h26_r)

h27 = on_command('njs27', priority=2, block=True)
@h27.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h27.finish('\n' + h27_r, at_sender=True)
    else:
        await h27.finish(h27_r)

h28 = on_command('njs28', priority=2, block=True)
@h28.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h28.finish('\n' + h28_r, at_sender=True)
    else:
        await h28.finish(h28_r)

h29 = on_command('njs29', priority=2, block=True)
@h29.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h29.finish('\n' + h29_r, at_sender=True)
    else:
        await h29.finish(h29_r)

h30 = on_command('njs30', priority=2, block=True)
@h30.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h30.finish('\n' + h30_r, at_sender=True)
    else:
        await h30.finish(h30_r)

h31 = on_command('njs31', priority=2, block=True)
@h31.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h31.finish('\n' + h31_r, at_sender=True)
    else:
        await h31.finish(h31_r)

h32 = on_command('njs32', priority=2, block=True)
@h32.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h32.finish('\n' + h32_r, at_sender=True)
    else:
        await h32.finish(h32_r)

h33 = on_command('njs33', priority=2, block=True)
@h33.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h33.finish('\n' + h33_r, at_sender=True)
    else:
        await h33.finish(h33_r)

h34 = on_command('njs34', priority=2, block=True)
@h34.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h34.finish('\n' + h34_r, at_sender=True)
    else:
        await h34.finish(h34_r)

h35 = on_command('njs35', priority=2, block=True)
@h35.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h35.finish('\n' + h35_r, at_sender=True)
    else:
        await h35.finish(h35_r)

h36 = on_command('njs36', priority=2, block=True)
@h36.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h36.finish('\n' + h36_r, at_sender=True)
    else:
        await h36.finish(h36_r)

h37 = on_command('njs37', priority=2, block=True)
@h37.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h37.finish('\n' + h37_r, at_sender=True)
    else:
        await h37.finish(h37_r)

h38 = on_command('njs38', priority=2, block=True)
@h38.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h38.finish('\n' + h38_r, at_sender=True)
    else:
        await h38.finish(h38_r)

h39 = on_command('njs39', priority=2, block=True)
@h39.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h39.finish('\n' + h39_r, at_sender=True)
    else:
        await h39.finish(h39_r)

h40 = on_command('njs40', priority=2, block=True)
@h40.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h40.finish('\n' + h40_r, at_sender=True)
    else:
        await h40.finish(h40_r)

h41 = on_command('njs41', priority=2, block=True)
@h41.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h41.finish('\n' + h41_r, at_sender=True)
    else:
        await h41.finish(h41_r)

h42 = on_command('njs42', priority=2, block=True)
@h42.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h42.finish('\n' + h42_r, at_sender=True)
    else:
        await h42.finish(h42_r)

h43 = on_command('njs43', priority=2, block=True)
@h43.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h43.finish('\n' + h43_r, at_sender=True)
    else:
        await h43.finish(h43_r)

h44 = on_command('njs44', priority=2, block=True)
@h44.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h44.finish('\n' + h44_r, at_sender=True)
    else:
        await h44.finish(h44_r)

h45 = on_command('njs45', priority=2, block=True)
@h45.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h45.finish('\n' + h45_r, at_sender=True)
    else:
        await h45.finish(h45_r)

h46 = on_command('njs46', priority=2, block=True)
@h46.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h46.finish('\n' + h46_r, at_sender=True)
    else:
        await h46.finish(h46_r)

h47 = on_command('njs47', priority=2, block=True)
@h47.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h47.finish('\n' + h47_r, at_sender=True)
    else:
        await h47.finish(h47_r)

h48 = on_command('njs48', priority=2, block=True)
@h48.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h48.finish('\n' + h48_r, at_sender=True)
    else:
        await h48.finish(h48_r)

h49 = on_command('njs49', priority=2, block=True)
@h49.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h49.finish('\n' + h49_r, at_sender=True)
    else:
        await h49.finish(h49_r)

h50 = on_command('njs50', priority=2, block=True)
@h50.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h50.finish('\n' + h50_r, at_sender=True)
    else:
        await h50.finish(h50_r)

h51 = on_command('njs51', priority=2, block=True)
@h51.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h51.finish('\n' + h51_r, at_sender=True)
    else:
        await h51.finish(h51_r)

h52 = on_command('njs52', priority=2, block=True)
@h52.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h52.finish('\n' + h52_r, at_sender=True)
    else:
        await h52.finish(h52_r)

h53 = on_command('njs53', priority=2, block=True)
@h53.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h53.finish('\n' + h53_r, at_sender=True)
    else:
        await h53.finish(h53_r)

h54 = on_command('njs54', priority=2, block=True)
@h54.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h54.finish('\n' + h54_r, at_sender=True)
    else:
        await h54.finish(h54_r)

h55 = on_command('njs55', priority=2, block=True)
@h55.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h55.finish('\n' + h55_r, at_sender=True)
    else:
        await h55.finish(h55_r)

h56 = on_command('njs56', priority=2, block=True)
@h56.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h56.finish('\n' + h56_r, at_sender=True)
    else:
        await h56.finish(h56_r)

h57 = on_command('njs57', priority=2, block=True)
@h57.handle()
async def test_handle(event:Event):
    h57_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h57.png"
    if isinstance(event, GroupMessageEvent):
        await h57.finish('\n' + MessageSegment.image(h57_img), at_sender=True)
    else:
        await h57.finish(MessageSegment.image(h57_img))

h58 = on_command('njs58', priority=2, block=True)
@h58.handle()
async def test_handle(event:Event):
    h58_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h58.jpg"
    if isinstance(event, GroupMessageEvent):
        await h58.finish('\n' + MessageSegment.image(h58_img), at_sender=True)
    else:
        await h58.finish(MessageSegment.image(h58_img))

h59 = on_command('njs59', priority=2, block=True)
@h59.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h59.finish('\n' + h59_r, at_sender=True)
    else:
        await h59.finish(h59_r)

h60 = on_command('njs60', priority=2, block=True)
@h60.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h60.finish('\n' + h60_r, at_sender=True)
    else:
        await h60.finish(h60_r)

h61 = on_command('njs61', priority=2, block=True)
@h61.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h61.finish('\n' + h61_r, at_sender=True)
    else:
        await h61.finish(h61_r)

h62 = on_command('njs62', priority=2, block=True)
@h62.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h62.finish('\n' + h62_r, at_sender=True)
    else:
        await h62.finish(h62_r)

h63 = on_command('njs63', priority=2, block=True)
@h63.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h63.finish('\n' + h63_r, at_sender=True)
    else:
        await h63.finish(h63_r)

h64 = on_command('njs64', priority=2, block=True)
@h64.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h64.finish('\n' + h64_r, at_sender=True)
    else:
        await h64.finish(h64_r)

h65 = on_command('njs65', priority=2, block=True)
@h65.handle()
async def test_handle(event:Event):
    h65_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h65.png"
    if isinstance(event, GroupMessageEvent):
        await h65.finish('\n' + MessageSegment.image(h65_img), at_sender=True)
    else:
        await h65.finish(MessageSegment.image(h65_img))

h66 = on_command('njs66', priority=2, block=True)
@h66.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h66.finish('\n' + h66_r, at_sender=True)
    else:
        await h66.finish(h66_r)

h67 = on_command('njs67', priority=2, block=True)
@h67.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h67.finish('\n' + h67_r, at_sender=True)
    else:
        await h67.finish(h67_r)

h68 = on_command('njs68', priority=2, block=True)
@h68.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h68.finish('\n' + h68_r, at_sender=True)
    else:
        await h68.finish(h68_r)

h69 = on_command('njs69', priority=2, block=True)
@h69.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h69.finish('\n' + h69_r, at_sender=True)
    else:
        await h69.finish(h69_r)

h70 = on_command('njs70', priority=2, block=True)
@h70.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h70.finish('\n' + h70_r, at_sender=True)
    else:
        await h70.finish(h70_r)

h71 = on_command('njs71', priority=2, block=True)
@h71.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h71.finish('\n' + h71_r, at_sender=True)
    else:
        await h71.finish(h71_r)

h72 = on_command('njs72', priority=2, block=True)
@h72.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h72.finish('\n' + h72_r, at_sender=True)
    else:
        await h72.finish(h72_r)

h73 = on_command('njs73', priority=2, block=True)
@h73.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h73.finish('\n' + h73_r, at_sender=True)
    else:
        await h73.finish(h73_r)

h74 = on_command('njs74', priority=2, block=True)
@h74.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h74.finish('\n' + h74_r, at_sender=True)
    else:
        await h74.finish(h74_r)

h75 = on_command('njs75', priority=2, block=True)
@h75.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h75.finish('\n' + h75_r, at_sender=True)
    else:
        await h75.finish(h75_r)

h76 = on_command('njs76', priority=2, block=True)
@h76.handle()
async def test_handle(event:Event):
    h76_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h76.jpg"
    if isinstance(event, GroupMessageEvent):
        await h76.finish('\n' + MessageSegment.image(h76_img), at_sender=True)
    else:
        await h76.finish(MessageSegment.image(h76_img))

h77 = on_command('njs77', priority=2, block=True)
@h77.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h77.finish('\n' + h77_r, at_sender=True)
    else:
        await h77.finish(h77_r)

h78 = on_command('njs78', priority=2, block=True)
@h78.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h78.finish('\n' + h78_r, at_sender=True)
    else:
        await h78.finish(h78_r)

h79 = on_command('njs79', priority=2, block=True)
@h79.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h79.finish('\n' + h79_r, at_sender=True)
    else:
        await h79.finish(h79_r)

h80 = on_command('njs80', priority=2, block=True)
@h80.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h80.finish('\n' + h80_r, at_sender=True)
    else:
        await h80.finish(h80_r)

h81 = on_command('njs81', priority=2, block=True)
@h81.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h81.finish('\n' + h81_r, at_sender=True)
    else:
        await h81.finish(h81_r)

h82 = on_command('njs82', priority=2, block=True)
@h82.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h82.finish('\n' + h82_r, at_sender=True)
    else:
        await h82.finish(h82_r)

h83 = on_command('njs83', priority=2, block=True)
@h83.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h83.finish('\n' + h83_r, at_sender=True)
    else:
        await h83.finish(h83_r)

h84 = on_command('njs84', priority=2, block=True)
@h84.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h84.finish('\n' + h84_r, at_sender=True)
    else:
        await h84.finish(h84_r)

h85 = on_command('njs85', priority=2, block=True)
@h85.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h85.finish('\n' + h85_r, at_sender=True)
    else:
        await h85.finish(h85_r)

h86 = on_command('njs86', priority=2, block=True)
@h86.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h86.finish('\n' + h86_r, at_sender=True)
    else:
        await h86.finish(h86_r)

h87 = on_command('njs87', priority=2, block=True)
@h87.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h87.finish('\n' + h87_r, at_sender=True)
    else:
        await h87.finish(h87_r)

h88 = on_command('njs88', priority=2, block=True)
@h88.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h88.finish('\n' + h88_r, at_sender=True)
    else:
        await h88.finish(h88_r)

h89 = on_command('njs89', priority=2, block=True)
@h89.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h89.finish('\n' + h89_r, at_sender=True)
    else:
        await h89.finish(h89_r)

h90 = on_command('njs90', priority=2, block=True)
@h90.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h90.finish('\n' + h90_r, at_sender=True)
    else:
        await h90.finish(h90_r)

h91 = on_command('njs91', priority=2, block=True)
@h91.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h91.finish('\n' + h91_r, at_sender=True)
    else:
        await h91.finish(h91_r)

h92 = on_command('njs92', priority=2, block=True)
@h92.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h92.finish('\n' + h92_r, at_sender=True)
    else:
        await h92.finish(h92_r)

h93 = on_command('njs93', priority=2, block=True)
@h93.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h93.finish('\n' + h93_r, at_sender=True)
    else:
        await h93.finish(h93_r)

h94 = on_command('njs94', priority=2, block=True)
@h94.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h94.finish('\n' + h94_r, at_sender=True)
    else:
        await h94.finish(h94_r)

h95 = on_command('njs95', priority=2, block=True)
@h95.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h95.finish('\n' + h95_r, at_sender=True)
    else:
        await h95.finish(h95_r)

h96 = on_command('njs96', priority=2, block=True)
@h96.handle()
async def test_handle(event:Event):
    if isinstance(event, GroupMessageEvent):
        await h96.finish('\n' + h96_r, at_sender=True)
    else:
        await h96.finish(h96_r)

