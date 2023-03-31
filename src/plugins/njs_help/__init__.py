import io
import os
import nonebot
from pathlib import Path
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot_plugin_imageutils import text2image
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageSegment,
    GroupMessageEvent,
    PrivateMessageEvent
    )

from .utils import *

try:
    NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]
except Exception:
    NICKNAME: str = "脑积水"



njs_help = on_command("njs", aliases={"NJS", "脑积水"}, priority=2, block=True)
@njs_help.handle()
async def _(bot: Bot, event: Event, msg: Message = CommandArg()):
    number = msg.extract_plain_text().strip()
    if number in ["帮助", "菜单", "列表", "help", "Help" ,"HELP"]:
        # 转为图片发送
        img = text2image(help_reply_body)
        output = io.BytesIO()
        img.save(output, format="png")
        image = MessageSegment.image(output)
        # 私聊直接发送
        if isinstance(event, PrivateMessageEvent):
            await njs_help.send(help_reply_head)
            await njs_help.send(image)
            await njs_help.send(help_reply_foot)
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
    elif number == "1":
        h1_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h1.jpg"
        await njs_help.finish('指令如下: \n' + MessageSegment.image(h1_img), at_sender=True)
    elif number == "2":
        await njs_help.finish('指令如下: \n' + h2_r, at_sender=True)
    elif number == "3":
        await njs_help.finish('指令如下: \n' + h3_r, at_sender=True)
    elif number == "4":
        await njs_help.finish('指令如下: \n' + h4_r, at_sender=True)
    elif number == "5":
        await njs_help.finish('指令如下: \n' + h5_r, at_sender=True)
    elif number == "6":
        await njs_help.finish('指令如下: \n' + h6_r, at_sender=True)
    elif number == "7":
        await njs_help.finish('指令如下: \n' + h7_r, at_sender=True)
    elif number == "8":
        await njs_help.finish('指令如下: \n' + h8_r, at_sender=True)
    elif number == "9":
        await njs_help.finish('指令如下: \n' + h9_r, at_sender=True)
    elif number == "10":
        await njs_help.finish('指令如下: \n' + h10_r, at_sender=True)
    elif number == "11":
        await njs_help.finish('指令如下: \n' + h11_r, at_sender=True)
    elif number == "12":
        await njs_help.finish('指令如下: \n' + h12_r, at_sender=True)
    elif number == "13":
        await njs_help.finish('指令如下: \n' + h13_r, at_sender=True)
    elif number == "14":
        h14_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h14.jpg"
        await njs_help.finish('指令如下\n' + MessageSegment.image(h14_img), at_sender=True)
    elif number == "15":
        await njs_help.finish('指令如下: \n' + h15_r, at_sender=True)
    elif number == "16":
        await njs_help.finish('指令如下: \n' + h16_r, at_sender=True)
    elif number == "17":
        await njs_help.finish('指令如下: \n' + h17_r, at_sender=True)
    elif number == "18":
        await njs_help.finish('指令如下: \n' + h18_r, at_sender=True)
    elif number == "19":
        h19_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h19.png"
        await njs_help.finish('指令如下\n' + MessageSegment.image(h19_img), at_sender=True)
    elif number == "20":
        await njs_help.finish('指令如下: \n' + h20_r, at_sender=True)
    elif number == "21":
        await njs_help.finish('指令如下: \n' + h21_r, at_sender=True)
    elif number == "22":
        await njs_help.finish('指令如下: \n' + h22_r, at_sender=True)
    elif number == "23":
        await njs_help.finish('指令如下: \n' + h23_r, at_sender=True)
    elif number == "24":
        await njs_help.finish('指令如下: \n' + h24_r, at_sender=True)
    elif number == "25":
        await njs_help.finish('指令如下: \n' + h25_r, at_sender=True)
    elif number == "26":
        await njs_help.finish('指令如下: \n' + h26_r, at_sender=True)
    elif number == "27":
        await njs_help.finish('指令如下: \n' + h27_r, at_sender=True)
    elif number == "28":
        await njs_help.finish('指令如下: \n' + h28_r, at_sender=True)
    elif number == "29":
        await njs_help.finish('指令如下: \n' + h29_r, at_sender=True)
    elif number == "30":
        await njs_help.finish('指令如下: \n' + h30_r, at_sender=True)
    elif number == "31":
        await njs_help.finish('指令如下: \n' + h31_r, at_sender=True)
    elif number == "32":
        await njs_help.finish('指令如下: \n' + h32_r, at_sender=True)
    elif number == "33":
        await njs_help.finish('指令如下: \n' + h33_r, at_sender=True)
    elif number == "34":
        await njs_help.finish('指令如下: \n' + h34_r, at_sender=True)
    elif number == "35":
        await njs_help.finish('指令如下: \n' + h35_r, at_sender=True)
    elif number == "36":
        await njs_help.finish('指令如下: \n' + h36_r, at_sender=True)
    elif number == "37":
        await njs_help.finish('指令如下: \n' + h37_r, at_sender=True)
    elif number == "38":
        await njs_help.finish('指令如下: \n' + h38_r, at_sender=True)
    elif number == "39":
        await njs_help.finish('指令如下: \n' + h39_r, at_sender=True)
    elif number == "40":
        await njs_help.finish('指令如下: \n' + h40_r, at_sender=True)
    elif number == "41":
        await njs_help.finish('指令如下: \n' + h41_r, at_sender=True)
    elif number == "42":
        await njs_help.finish('指令如下: \n' + h42_r, at_sender=True)
    elif number == "43":
        await njs_help.finish('指令如下: \n' + h43_r, at_sender=True)
    elif number == "44":
        await njs_help.finish('指令如下: \n' + h44_r, at_sender=True)
    elif number == "45":
        await njs_help.finish('指令如下: \n' + h45_r, at_sender=True)
    elif number == "46":
        await njs_help.finish('指令如下: \n' + h46_r, at_sender=True)
    elif number == "47":
        await njs_help.finish('指令如下: \n' + h47_r, at_sender=True)
    elif number == "48":
        await njs_help.finish('指令如下: \n' + h48_r, at_sender=True)
    elif number == "49":
        await njs_help.finish('指令如下: \n' + h49_r, at_sender=True)
    elif number == "50":
        await njs_help.finish('指令如下: \n' + h50_r, at_sender=True)
    elif number == "51":
        await njs_help.finish('指令如下: \n' + h51_r, at_sender=True)
    elif number == "52":
        await njs_help.finish('指令如下: \n' + h52_r, at_sender=True)
    elif number == "53":
        await njs_help.finish('指令如下: \n' + h53_r, at_sender=True)
    elif number == "54":
        await njs_help.finish('指令如下: \n' + h54_r, at_sender=True)
    elif number == "55":
        await njs_help.finish('指令如下: \n' + h55_r, at_sender=True)
    elif number == "56":
        await njs_help.finish('指令如下: \n' + h56_r, at_sender=True)
    elif number == "57":
        h57_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h57.png"
        await njs_help.finish('指令如下\n' + MessageSegment.image(h57_img), at_sender=True)
    elif number == "58":
        h58_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h58.jpg"
        await njs_help.finish('指令如下\n' + MessageSegment.image(h58_img), at_sender=True)
    elif number == "59":
        await njs_help.finish('指令如下: \n' + h59_r, at_sender=True)
    elif number == "60":
        await njs_help.finish('指令如下: \n' + h60_r, at_sender=True)
    elif number == "61":
        await njs_help.finish('指令如下: \n' + h61_r, at_sender=True)
    elif number == "62":
        await njs_help.finish('指令如下: \n' + h62_r, at_sender=True)
    elif number == "63":
        await njs_help.finish('指令如下: \n' + h63_r, at_sender=True)
    elif number == "64":
        await njs_help.finish('指令如下: \n' + h64_r, at_sender=True)
    elif number == "65":
        h65_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h65.png"
        await njs_help.finish('指令如下\n' + MessageSegment.image(h65_img), at_sender=True)
    elif number == "66":
        await njs_help.finish('指令如下: \n' + h66_r, at_sender=True)
    elif number == "67":
        await njs_help.finish('指令如下: \n' + h67_r, at_sender=True)
    elif number == "68":
        await njs_help.finish('指令如下: \n' + h68_r, at_sender=True)
    elif number == "69":
        await njs_help.finish('指令如下: \n' + h69_r, at_sender=True)
    elif number == "70":
        await njs_help.finish('指令如下: \n' + h70_r, at_sender=True)
    elif number == "71":
        await njs_help.finish('指令如下: \n' + h71_r, at_sender=True)
    elif number == "72":
        await njs_help.finish('指令如下: \n' + h72_r, at_sender=True)
    elif number == "73":
        await njs_help.finish('指令如下: \n' + h73_r, at_sender=True)
    elif number == "74":
        await njs_help.finish('指令如下: \n' + h74_r, at_sender=True)
    elif number == "75":
        await njs_help.finish('指令如下: \n' + h75_r, at_sender=True)
    elif number == "76":
        h76_img = Path(os.path.join(os.path.dirname(__file__), "resource")) / "h76.jpg"
        await njs_help.finish('指令如下\n' + MessageSegment.image(h76_img), at_sender=True)
    elif number == "77":
        await njs_help.finish('指令如下: \n' + h77_r, at_sender=True)
    elif number == "78":
        await njs_help.finish('指令如下: \n' + h78_r, at_sender=True)
    elif number == "79":
        await njs_help.finish('指令如下: \n' + h79_r, at_sender=True)
    elif number == "80":
        await njs_help.finish('指令如下: \n' + h80_r, at_sender=True)
    elif number == "81":
        await njs_help.finish('指令如下: \n' + h81_r, at_sender=True)
    elif number == "82":
        await njs_help.finish('指令如下: \n' + h82_r, at_sender=True)
    elif number == "83":
        await njs_help.finish('指令如下: \n' + h83_r, at_sender=True)
    elif number == "84":
        await njs_help.finish('指令如下: \n' + h84_r, at_sender=True)
    elif number == "85":
        await njs_help.finish('指令如下: \n' + h85_r, at_sender=True)
    elif number == "86":
        await njs_help.finish('指令如下: \n' + h86_r, at_sender=True)
    elif number == "87":
        await njs_help.finish('指令如下: \n' + h87_r, at_sender=True)
    elif number == "88":
        await njs_help.finish('指令如下: \n' + h88_r, at_sender=True)
    elif number == "89":
        await njs_help.finish('指令如下: \n' + h89_r, at_sender=True)
    elif number == "90":
        await njs_help.finish('指令如下: \n' + h90_r, at_sender=True)
    elif number == "91":
        await njs_help.finish('指令如下: \n' + h91_r, at_sender=True)
    elif number == "92":
        await njs_help.finish('指令如下: \n' + h92_r, at_sender=True)
    elif number == "93":
        await njs_help.finish('指令如下: \n' + h93_r, at_sender=True)
    elif number == "94":
        await njs_help.finish('指令如下: \n' + h94_r, at_sender=True)
    elif number == "95":
        await njs_help.finish('指令如下: \n' + h95_r, at_sender=True)
    elif number == "96":
        await njs_help.finish('指令如下: \n' + h96_r, at_sender=True)
    elif number == "97":
        await njs_help.finish('指令如下: \n' + h97_r, at_sender=True)
    elif number == "98":
        await njs_help.finish('指令如下: \n' + h98_r, at_sender=True)
    else:
        await njs_help.finish('功能扩建中...', at_sender=True)