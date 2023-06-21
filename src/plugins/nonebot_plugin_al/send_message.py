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


class BLHX_BASE:
    def __init__(self) -> None:
        ...

    async def send_ship_skin_or_info(
        matcher:Matcher,
        event:Event,
        bot:Bot,
        arg:Message = CommandArg()
        ):
        SAVE_PATH = Path().cwd().joinpath('data/al/ship_html')
        try:
            args = arg.extract_plain_text().split()
            if len(args) == 2:
                ship_name = str(args[0])
                skin_name = str(args[1]).replace("_", (" "))
                ship_nickname_data = await GetIDByNickname(ship_name)
                if ship_nickname_data == -1 :
                    msg = "该昵称下查不到舰船信息，请核对输入，如果想为她新增昵称请发送： blhx备注 正式船名 昵称"
                    await bot.send(event=event,message=msg, at_sender=True)
                else:
                    ship_id = ship_nickname_data['id']

                flag = await get_ship_skin_by_id(str(ship_id), skin_name)
                if flag == 4:
                    msg = "她没有这个皮肤！"
                    await bot.send(event=event,message=msg, at_sender=True)
                if flag == 0:
                    # print_img_skin()
                    await save_img_ship('skin',temp=False)
                    msg = MessageSegment.image("file:///" + str(SAVE_PATH.joinpath("images/ship_skin.png")))
                    await bot.send(event=event,message=msg, at_sender=True)
                if flag == 1:
                    msg = "她只有原皮！"
                    await bot.send(event=event,message=msg, at_sender=True)
            if len(args) == 1:
                nickname_list = ''
                ship_name = str(args[0])
                ship_nickname_data = await GetIDByNickname(ship_name)
                ship_nickname_list = await GetAllNickname(ship_nickname_data['id'])
                for string in ship_nickname_list:
                    nickname_list+=(str(string)+"\n")

                index = await format_data_into_html(await get_ship_data_by_id(ship_nickname_data['id']))
                await get_ship_weapon_by_ship_name(ship_nickname_data['standred_name'])
                
                # print_img_ship()
                # print_img_ship_weapon()

                await save_img_ship()
                await save_img_ship('weapon')
                img_process_ship_info()
                img_process_ship_weapon()
                
                if index == 0:
                    msg = "舰船信息\n" + MessageSegment.image("file:///" + str(SAVE_PATH.joinpath("images/ship_info.png"))) \
                        + "\n推荐出装\n" + MessageSegment.image("file:///" + str(SAVE_PATH.joinpath("images/ship_weapon.png")))+ "\n此船备注昵称有：\n"+nickname_list
                else:
                    print_img_ship_retrofit()
                    img_process_ship_retrofit()
                    msg = "舰船信息\n" + MessageSegment.image("file:///" + str(SAVE_PATH.joinpath("images/ship_info.png"))) \
                        + "\n此船可改\n" + MessageSegment.image("file:///" + str(SAVE_PATH.joinpath("images/ship_retrofit.png"))) \
                        + "\n推荐出装\n" + MessageSegment.image("file:///" + str(SAVE_PATH.joinpath("images/ship_weapon.png")))\
                        + "\n此船备注昵称有：\n"+nickname_list

                msg_list = []
                msg_list.append(msg)
                forward_msg = render_forward_msg(msg_list,bot=bot)
                if isinstance(event,GroupMessageEvent):
                    await bot.call_api('send_group_forward_msg',group_id=event.group_id, messages=forward_msg)
                    return
            if len(args) == 0:
                await bot.send(event=event,message='请在命令之后提供精确舰船名称和皮肤昵称哦~', at_sender=True)
        except Exception as e:
            traceback.print_exc()
            await bot.send(event=event,message=f"查询出错,{e}", at_sender=True)

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
        1.查询舰船信息命令：”blhx [无需和谐的中文船名]
        2.查询舰船皮肤命令：”blhx [无需和谐的中文船名] [皮肤名]“ 皮肤名为”原皮”则查询原皮，为“婚纱”则查询婚纱，如果皮肤名有空格则用_替代
        3.查询加载时的过场动画：“blhx过场
        4.查询强度榜：“blhx强度榜"""
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

    async def set_nickname(        
        matcher:Matcher,
        event:Event,
        bot:Bot,
        arg:Message = CommandArg()
        ):
        msg = ''
        try:
            args = arg.message.extract_plain_text().split()
            if len(args) == 2:
                origin_name = str(args[0])
                nick_name = str(args[1])

                result = await get_ship_data_by_name(origin_name)

                flag = await AddName(str(result['id']),nick_name)
                if flag != 0:
                    msg = "查无此船，请输入正确的舰船名称"
                else:
                    msg = '成功为'+origin_name+'添加一个新昵称：'+nick_name
                await bot.send(event=event,message=str(msg), at_sender=True)
            else:
                msg = "参数错误，命令需形如: blhx备注 正式船名 昵称"
                await bot.send(event=event,message=str(msg), at_sender=True)
            return
        except:
            msg = '处理出错，请看日志'
            traceback.print_exc()
            await bot.send(event=event,message=str(msg), at_sender=True)
            return


    async def remove_nickname(        
        matcher:Matcher,
        event:Event,
        bot:Bot,
        arg:Message = CommandArg()
        ):
        msg = ''
        try:
            args = arg.message.extract_plain_text().split()
            if len(args) == 2:
                origin_name = str(args[0])
                nick_name = str(args[1])

                result = await get_ship_data_by_name(origin_name)

                flag = await DelName(str(result['id']), nick_name)

                if flag != 0:
                    msg = "此船无此昵称"
                else:
                    msg = '成功为'+origin_name+'移除一个昵称：'+nick_name
                await bot.send(event=event,message=str(msg), at_sender=True)
            else:
                msg = "参数错误，命令需形如: blhx移除备注 正式船名 昵称"
                await bot.send(event=event,message=str(msg), at_sender=True)
            return
        except:
            msg = '处理出错，请看日志'
            traceback.print_exc()
            await bot.send(event=event,message=str(msg), at_sender=True)
            return


    async def quick_search_skin(        
        matcher:Matcher,
        event:Event,
        bot:Bot,
        arg:Message = CommandArg()
        ):
        try:
            args = arg.message.extract_plain_text().split()
            if len(args) == 2:
                skin_index = int(args[1])
                ship_name = str(args[0])
                ship_nickname_data = await GetIDByNickname(ship_name)
                if ship_nickname_data == -1:
                    msg = "该昵称下查不到舰船信息，请核对输入，如果想为她新增昵称请发送： blhx备注 正式船名 昵称"
                    await bot.send(event=event,message=msg, at_sender=True)
                    return
                else:
                    ship_id = ship_nickname_data['id']

                flag = await get_ship_skin_by_id_with_index(str(ship_id), skin_index)
                if flag == -1:
                    msg = "她没有这个皮肤！"
                    await bot.send(event=event,message=msg, at_sender=True)
                    return
                if flag == 0:
                    print_img_skin()
                    msg = MessageSegment.image("file:///" + str(SAVE_PATH.joinpath("images/ship_skin.png")))
                    await bot.send(event=event,message=msg, at_sender=True)
                    return
        except:
            msg = '处理出错，请看日志'
            traceback.print_exc()
            await bot.send(event=event,message=str(msg), at_sender=True)
            return


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




blhx = BLHX_BASE()