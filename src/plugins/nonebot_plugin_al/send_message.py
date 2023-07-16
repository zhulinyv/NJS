import traceback
import shutil

from nonebot.adapters.onebot.v11 import (Bot, GroupMessageEvent, Message,
                                         MessageSegment,Event)
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.log import logger
from nonebot_plugin_htmlrender import html_to_pic

from .api import *
from .utils import *
from .draw import *
from .name import *



async def send_random_gallery(
    matcher:Matcher,
    event:Event,
    bot:Bot
    ):
    SAVE_PATH = Path().cwd().joinpath('data/al/ship_html/images/gallery/',get_random_gallery())
    msg = MessageSegment.image("file:///" + str(SAVE_PATH))
    await bot.send(event=event,message=msg, at_sender=True)


async def send_blhx_help(
    matcher:Matcher,
    event:Event,
    bot:Bot
    ):
    msg = """
1.查询舰船信息命令：blhx [无需和谐的中文船名]
2.查询舰船皮肤命令：blhx [无需和谐的中文船名] [皮肤名] 皮肤名为"原皮"则查询原皮，为"婚纱"则查询婚纱，如果皮肤名有空格则用_替代
3.查询加载时的过场动画：blhx 过场
4.查询强度榜：blhx 强度榜
5.设置(移除)备注：blhx (移除)备注 原名 昵称
6.查看备注：blhx 查看备注 原名"""
    await bot.send(event=event,message=msg,at_sender=True)


async def send_pve_recommendation(        
    matcher:Matcher,
    event:Event,
    bot:Bot
    ):
    div_list = await get_pve_recommendation()
    # div_text = ["认知觉醒推荐榜(主线)\n", "认知觉醒推荐榜(大世界)\n", "装备榜\n", "萌新入坑舰船推荐榜\n", "萌新初期装备榜\n",
    #             "兵装推荐榜\n", "专武推荐榜\n", "兑换装备推荐榜\n", "研发装备推荐榜\n", "改造推荐榜\n", "跨队舰船推荐榜\n",
    #             "氪金榜\n" , "打捞主线榜\n","打捞作战榜'\n"]
    msg = "仅代表个人观点，完全不等于绝对客观，可能存在各种主观评判或者真爱加成，不过目标是努力去进行符合环境需求的客观评定\n"
    msg_list = []
    if len(div_list) != 0:
        for i in range(0, len(div_list)):
            msg += Message(str(div_list[i].find('img')['alt']) + MessageSegment.image(file=str(div_list[i].find('img')['src'])) + "\n")
        msg_list.append(msg)
        forward_msg = render_forward_msg(msg_list,bot=bot)
        if isinstance(event,GroupMessageEvent):
            await bot.call_api('send_group_forward_msg',group_id=event.group_id, messages=forward_msg)
            return
    else:
        await bot.send(event=event,message='暂无信息', at_sender=True)


async def force_update(        
    matcher:Matcher,
    event:Event,
    bot:Bot,
    arg:Message = CommandArg()
    ):

    logger.info("命令确认，正在删除")
    try:
        await bot.send(event=event,message='正在更新，首先请确保网络能访问github的文件中心，否则容易出现翻车风险！', at_sender=True)
        await force_update_offline()
        os.rename(PATH, BACK_PATH)  # 备份源文件省得出意外翻车
        await force_update_offline()  # 再更新
        shutil.rmtree(BACK_PATH)  # 更新完成再删除备份
        version_info = await get_local_version()
        version = str(version_info['version-number'])
        await UpdateName()
        await bot.send(event=event,message='强制更新完成.强制更新内容仅在离线模式下有效，当前版本V'+version, at_sender=True)
    except:
        # 出问题赶紧回滚
        traceback.print_exc()
        await bot.send(event=event,message='更新失败！尝试回滚...', at_sender=True)
        try:
            os.rename(BACK_PATH, PATH)
            await bot.send(event=event,message='回滚成功，差点您就没了。', at_sender=True)
        except:
            await bot.send(event=event,message=f'回滚失败！', at_sender=True)


async def get_recently_event(        
    matcher:Matcher,
    event:Event,
    bot:Bot
    ):
    msg = await get_recent_event()
    if msg is None:
        await bot.send(event=event,message='程序开小差了~', at_sender=True)
    else:
        await bot.send(event=event,message='详情请看' + str(msg), at_sender=True)

async def set_nickname(bot: Bot, event: Event, msg: Message = CommandArg()):
    # 获取纯文本信息
    message = msg.extract_plain_text().strip()
    # 将字符串转换为列表
    variable_list = message.split(' ')
    variable_list = [word.strip() for word in variable_list if word.strip()]    # 去除空字符串元素
    try:
        if len(variable_list) == 2:
            origin_name = str(variable_list[0])
            nick_name = str(variable_list[1])

            result = await get_ship_data_by_name(origin_name)

            await AddName(str(result['id']),nick_name)

            if not result:
                msg = "查无此船，请输入正确的舰船名称"
            else:
                    with open(Path(__file__).absolute().parent / "data" / "ship.json", mode='r', encoding="utf-8") as f:
                        load_dict = json.load(f)
                    load_dict[f"{origin_name}"].append(nick_name)
                    with open(Path(__file__).absolute().parent / "data" / "ship.json", mode='w', encoding="utf-8") as f:
                        json.dump(load_dict, f, indent=4, ensure_ascii=False)
                    await AddName(str(result['id']),nick_name)
                    msg = '成功为'+origin_name+'添加一个新昵称：'+nick_name
            await bot.send(event=event,message=str(msg), at_sender=True)
        else:
            msg = "参数错误，命令需形如: blhx 备注 正式船名 昵称"
            await bot.send(event=event,message=str(msg), at_sender=True)
        return
    except:
        msg = '处理出错，请看日志'
        traceback.print_exc()
        await bot.send(event=event, message=str(msg), at_sender=True)
        return


async def remove_nickname(bot: Bot, event: Event, msg: Message = CommandArg()):
    # 获取纯文本信息
    message = msg.extract_plain_text().strip()
    # 将字符串转换为列表
    variable_list = message.split(' ')
    variable_list = [word.strip() for word in variable_list if word.strip()]    # 去除空字符串元素
    try:
        if len(variable_list) == 2:
            origin_name = str(variable_list[0])
            nick_name = str(variable_list[1])

            result = await get_ship_data_by_name(origin_name)

            if not result:
                msg = "此船无此昵称"
            else:
                try:
                    with open(Path(__file__).absolute().parent / "data" / "ship.json", mode='r', encoding="utf-8") as f:
                        load_dict = json.load(f)
                    load_dict[f"{origin_name}"].remove(nick_name)
                    with open(Path(__file__).absolute().parent / "data" / "ship.json", mode='w', encoding="utf-8") as f:
                        json.dump(load_dict, f, indent=4, ensure_ascii=False)
                    await DelName(str(result['id']), nick_name)
                    msg = '成功为'+origin_name+'移除一个昵称：'+nick_name
                except Exception as error:
                    msg = f'移除昵称失败:\n{error}'
            await bot.send(event=event,message=str(msg), at_sender=True)
        else:
            msg = "参数错误，命令需形如: blhx 移除备注 正式船名 昵称"
            await bot.send(event=event,message=str(msg), at_sender=True)
        return
    except:
        msg = '处理出错，请看日志'
        traceback.print_exc()
        await bot.send(event=event, message=str(msg), at_sender=True)
        return


async def view_nickname(bot: Bot, event: Event, msg: Message = CommandArg()):
    # 获取纯文本信息
    message = msg.extract_plain_text().strip()
    with open(Path(__file__).absolute().parent / "data" / "ship.json", mode='r', encoding="utf-8") as f:
        load_dict = json.load(f)
    try:
        data = load_dict[f"{message}"]
        names = ""
        for name in data:
            names += f"{name}、"
    except:
        names = "查询失败, 请确保输入为舰船原名!"
    await bot.send(event=event, message=f"{names}", at_sender=True)


async def building(        
    matcher:Matcher,
    event:Event,
    bot:Bot,
    arg:Message = CommandArg()
    ):
    try:
        args = arg.extract_plain_text().split()
        if len(args) == 1:
            if str(args[0]) == '轻型':
                data = await gacha_light_10()
                img = GachaImage(data)
                cq = await img.Make()
                await bot.send(event=event,message=cq,at_sender=True)
            if str(args[0]) == '重型':
                data = await gacha_heavy_10()
                img = GachaImage(data)
                cq = await img.Make()
                await bot.send(event=event,message=cq, at_sender=True)
            if str(args[0]) == '特型':
                data = await gacha_special_10()
                img = GachaImage(data)
                cq = await img.Make()
                await bot.send(event=event,message=cq, at_sender=True)
        else:
            await bot.send(event=event,message='指令错误 发送blhx大建 轻型/重型/特型 进行大建模拟', at_sender=True)
            return
    except :
        msg = '处理出错，请看日志'
        traceback.print_exc()
        await bot.send(event=event,message=str(msg), at_sender=True)
        return