import nonebot
import os
from nonebot import on_command
from pathlib import Path
from .utils import *
from nonebot.adapters.onebot.v11 import (Bot,GroupMessageEvent, 
                                        Message, MessageSegment,
                                        PrivateMessageEvent, Event)

NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]

help = on_command('脑积水帮助', aliases={'njs帮助', 'njs菜单', 'njs列表'}, priority=10, block=True)
@help.handle()
async def help_handle(event:Event, bot:Bot):
    if isinstance(event, PrivateMessageEvent):
        # 私聊直接发送
        await help.finish(help_reply)
    elif isinstance(event, GroupMessageEvent):
        # 群聊转发
        msgs = []
        message_list = []
        message_list.append(help_reply)
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

h1 = on_command('njs1', priority=10, block=True)
@h1.handle()
async def test_handle(event:Event):
    h1_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h1.jpg"
    await h1.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(h1_img))

h2 = on_command('njs2', priority=10, block=True)
@h2.handle()
async def test_handle(event:Event):
    await h2.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h2_r)

h3 = on_command('njs3', priority=10, block=True)
@h3.handle()
async def test_handle(event:Event):
    await h3.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h3_r)

h4 = on_command('njs4', priority=10, block=True)
@h4.handle()
async def test_handle(event:Event):
    await h4.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h4_r)

h5 = on_command('njs5', priority=10, block=True)
@h5.handle()
async def test_handle(event:Event):
    await h5.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h5_r)

h6 = on_command('njs6', priority=10, block=True)
@h6.handle()
async def test_handle(event:Event):
    await h6.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h6_r)

h7 = on_command('njs7', priority=10, block=True)
@h7.handle()
async def test_handle(event:Event):
    await h7.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h7_r)

h8 = on_command('njs8', priority=10, block=True)
@h8.handle()
async def test_handle(event:Event):
    await h8.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h8_r)

h9 = on_command('njs9', priority=10, block=True)
@h9.handle()
async def test_handle(event:Event):
    await h9.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h9_r)

h10 = on_command('njs10', priority=10, block=True)
@h10.handle()
async def test_handle(event:Event):
    await h10.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h10_r)

h11 = on_command('njs11', priority=10, block=True)
@h11.handle()
async def test_handle(event:Event):
    await h11.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h11_r)

h12 = on_command('njs12', priority=10, block=True)
@h12.handle()
async def test_handle(event:Event):
    await h12.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h12_r)

h13 = on_command('njs13', priority=10, block=True)
@h13.handle()
async def test_handle(event:Event):
    await h13.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h13_r)

h14 = on_command('njs14', priority=10, block=True)
@h14.handle()
async def test_handle(event:Event):
    await h14.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h14_r)

h15 = on_command('njs15', priority=10, block=True)
@h15.handle()
async def test_handle(event:Event):
    await h15.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h15_r)

h16 = on_command('njs16', priority=10, block=True)
@h16.handle()
async def test_handle(event:Event):
    await h16.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h16_r)

h17 = on_command('njs17', priority=10, block=True)
@h17.handle()
async def test_handle(event:Event):
    await h17.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h17_r)

h18 = on_command('njs18', priority=10, block=True)
@h18.handle()
async def test_handle(event:Event):
    await h18.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h18_r)

h19 = on_command('njs19', priority=10, block=True)
@h19.handle()
async def test_handle(event:Event):
    h19_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h19.jpg"
    await h19.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + MessageSegment.image(h19_img))

h20 = on_command('njs20', priority=10, block=True)
@h20.handle()
async def test_handle(event:Event):
    await h20.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h20_r)

h21 = on_command('njs21', priority=10, block=True)
@h21.handle()
async def test_handle(event:Event):
    await h21.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h21_r)

h22 = on_command('njs22', priority=10, block=True)
@h22.handle()
async def test_handle(event:Event):
    await h22.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h22_r)

h23 = on_command('njs23', priority=10, block=True)
@h23.handle()
async def test_handle(event:Event):
    await h23.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h23_r)

h24 = on_command('njs24', priority=10, block=True)
@h24.handle()
async def test_handle(event:Event):
    await h24.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h24_r)

h25 = on_command('njs25', priority=10, block=True)
@h25.handle()
async def test_handle(event:Event):
    await h25.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h25_r)

h26 = on_command('njs26', priority=10, block=True)
@h26.handle()
async def test_handle(event:Event):
    await h26.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h26_r)

h27 = on_command('njs27', priority=10, block=True)
@h27.handle()
async def test_handle(event:Event):
    await h27.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h27_r)

h28 = on_command('njs28', priority=10, block=True)
@h28.handle()
async def test_handle(event:Event):
    await h28.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h28_r)

h29 = on_command('njs29', priority=10, block=True)
@h29.handle()
async def test_handle(event:Event):
    await h29.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h29_r)

h30 = on_command('njs30', priority=10, block=True)
@h30.handle()
async def test_handle(event:Event):
    await h30.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h30_r)

h31 = on_command('njs31', priority=10, block=True)
@h31.handle()
async def test_handle(event:Event):
    await h31.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h31_r)

h32 = on_command('njs32', priority=10, block=True)
@h32.handle()
async def test_handle(event:Event):
    await h32.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h32_r)
h33 = on_command('njs33', priority=10, block=True)
@h33.handle()
async def test_handle(event:Event):
    await h33.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h33_r)

h34 = on_command('njs34', priority=10, block=True)
@h34.handle()
async def test_handle(event:Event):
    await h34.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h34_r)

h35 = on_command('njs35', priority=10, block=True)
@h35.handle()
async def test_handle(event:Event):
    await h35.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h35_r)

h36 = on_command('njs36', priority=10, block=True)
@h36.handle()
async def test_handle(event:Event):
    await h36.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h36_r)

h37 = on_command('njs37', priority=10, block=True)
@h37.handle()
async def test_handle(event:Event):
    await h37.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h37_r)

h38 = on_command('njs38', priority=10, block=True)
@h38.handle()
async def test_handle(event:Event):
    await h38.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h38_r)

h39 = on_command('njs39', priority=10, block=True)
@h39.handle()
async def test_handle(event:Event):
    await h39.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h39_r)

h40 = on_command('njs40', priority=10, block=True)
@h40.handle()
async def test_handle(event:Event):
    await h40.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h40_r)

h41 = on_command('njs41', priority=10, block=True)
@h41.handle()
async def test_handle(event:Event):
    await h41.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h41_r)

h42 = on_command('njs42', priority=10, block=True)
@h42.handle()
async def test_handle(event:Event):
    await h42.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h42_r)

h43 = on_command('njs43', priority=10, block=True)
@h43.handle()
async def test_handle(event:Event):
    await h43.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h43_r)

h44 = on_command('njs44', priority=10, block=True)
@h44.handle()
async def test_handle(event:Event):
    await h44.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h44_r)

h45 = on_command('njs45', priority=10, block=True)
@h45.handle()
async def test_handle(event:Event):
    await h45.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h45_r)

h46 = on_command('njs46', priority=10, block=True)
@h46.handle()
async def test_handle(event:Event):
    await h46.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h46_r)

h47 = on_command('njs47', priority=10, block=True)
@h47.handle()
async def test_handle(event:Event):
    await h47.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h47_r)

h48 = on_command('njs48', priority=10, block=True)
@h48.handle()
async def test_handle(event:Event):
    await h48.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h48_r)

h49 = on_command('njs49', priority=10, block=True)
@h49.handle()
async def test_handle(event:Event):
    await h49.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h49_r)

h50 = on_command('njs50', priority=10, block=True)
@h50.handle()
async def test_handle(event:Event):
    await h50.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h50_r)

h51 = on_command('njs51', priority=10, block=True)
@h51.handle()
async def test_handle(event:Event):
    await h51.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h51_r)

h52 = on_command('njs52', priority=10, block=True)
@h52.handle()
async def test_handle(event:Event):
    await h52.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h52_r)

h53 = on_command('njs53', priority=10, block=True)
@h53.handle()
async def test_handle(event:Event):
    await h53.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h53_r)

h54 = on_command('njs54', priority=10, block=True)
@h54.handle()
async def test_handle(event:Event):
    await h54.finish(Message(f"[CQ:at,qq={event.get_user_id()}]") + h54_r)