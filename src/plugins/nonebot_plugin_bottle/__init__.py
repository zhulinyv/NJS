import random
import asyncio

from nonebot.matcher import Matcher
from nonebot import require, on_command
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.params import Arg, ArgStr, Depends, CommandArg

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from nonebot.adapters.onebot.v11 import (
    GROUP,
    Bot,
    Message,
    ActionFailed,
    MessageEvent,
    MessageSegment,
    GroupMessageEvent,
)

from .model import Bottle
from .config import Config
from .data_source import (
    ba,
    text_audit,
    bottle_manager,
    serialize_message,
    deserialize_message,
    get_content_preview,
)

__plugin_meta__ = PluginMetadata(
    name="漂流瓶",
    description="群与群互通的漂流瓶插件",
    config=Config,
    usage=f"""
指令：
    扔漂流瓶 [文本/图片]
    寄漂流瓶 [文本/图片] （同扔漂流瓶，防止指令冲突用）
    捡漂流瓶
    评论漂流瓶 [漂流瓶编号] [文本]
    举报漂流瓶 [漂流瓶编号]
    查看漂流瓶 [漂流瓶编号]
    删除漂流瓶 [漂流瓶编号]
    我的漂流瓶
SUPERUSER指令：
    清空漂流瓶
    恢复漂流瓶 [漂流瓶编号]
    删除漂流瓶评论 [漂流瓶编号] [QQ号]
    漂流瓶白名单 [QQ / 群聊 / 举报] [QQ号 / 群号]
    漂流瓶黑名单 [QQ / 群聊] [QQ号 / 群号]
    漂流瓶详情 [漂流瓶编号]
""".strip(),
    extra={
        "unique_name": "nonebot_plugin_bottle",
        "example": "扔漂流瓶\n寄漂流瓶\n捡漂流瓶\n评论漂流瓶\n举报漂流瓶\n查看漂流瓶\n删除漂流瓶",
        "author": "Todysheep",
        "version": "1.0.0",
    },
)

throw = on_command(
    "扔漂流瓶", aliases=set(["寄漂流瓶", "丢漂流瓶"]), permission=GROUP, priority=100, block=True
)
get = on_command("捡漂流瓶", priority=100, block=True)
report = on_command("举报漂流瓶", priority=100, block=True)
comment = on_command("评论漂流瓶", priority=100, block=True)
check_bottle = on_command("查看漂流瓶", priority=100, block=True)
remove = on_command("删除漂流瓶", priority=100, block=True)
listb = on_command("我的漂流瓶", priority=100, block=True)

resume = on_command("恢复漂流瓶", permission=SUPERUSER, priority=100, block=True)
clear = on_command("清空漂流瓶", permission=SUPERUSER, priority=100, block=True)
comrem = on_command("删除漂流瓶评论", permission=SUPERUSER, priority=100, block=True)
listqq = on_command("漂流瓶详情", permission=SUPERUSER, priority=100, block=True)
ban = on_command(
    "漂流瓶黑名单",
    aliases=set(["banbottle", "漂流瓶封禁"]),
    permission=SUPERUSER,
    priority=100,
    block=True,
)
white = on_command(
    "漂流瓶白名单",
    aliases=set(["whitebottle"]),
    permission=SUPERUSER,
    priority=100,
    block=True,
)


async def get_bottle(
    index: str, matcher: Matcher, session: AsyncSession, include_del=False
) -> Bottle:
    if not index.isdigit():
        await matcher.finish("漂流瓶编号必须为正整数！")
    bottle = await bottle_manager.get_bottle(
        index=int(index), session=session, include_del=include_del
    )
    if not bottle:
        await matcher.finish("该漂流瓶不存在或已被删除！")
    return bottle


async def verify(matcher: Matcher, event: GroupMessageEvent) -> None:
    if not ba.verify(event.user_id, event.group_id):
        await matcher.finish(ba.bannedMessage)


# 信息初始化
proceed = set(["是", "Y", "Yes", "y", "yes"])


@listb.handle()
async def _(
    bot: Bot, event: GroupMessageEvent, session: AsyncSession = Depends(get_session)
):
    bottles = await bottle_manager.list_bottles(
        user_id=event.user_id, session=session, include_del=False
    )
    if not bottles:
        await listb.finish("你还没有扔过漂流瓶哦～")

    # 获取漂流瓶预览内容
    bottles_info = []
    for bottle in bottles:
        content_preview = get_content_preview(bottle)
        bottles_info.append(f"#{bottle.id}：{content_preview}")

    # 整理消息
    messages = []
    total_bottles_info = f"您总共扔了{len(bottles_info)}个漂流瓶～\n"
    if len(bottles_info) > 10:
        i = 1
        while len(bottles_info) > 10:
            messages.append(
                total_bottles_info + "\n".join(bottles_info[:10]) + f"\n【第{i}页】"
            )
            bottles_info = bottles_info[10:]
            i = i + 1
        messages.append(
            total_bottles_info + "\n".join(bottles_info[:10]) + f"\n【第{i}页-完】"
        )

        # 发送合并转发消息
        if isinstance(event, GroupMessageEvent):
            await bot.send_group_forward_msg(
                group_id=event.group_id,
                messages=[
                    MessageSegment.node_custom(
                        user_id=event.self_id, nickname="bottle", content=msg
                    )
                    for msg in messages
                ],
            )
        else:
            await bot.send_private_forward_msg(
                user_id=event.user_id,
                messages=[
                    MessageSegment.node_custom(
                        user_id=event.self_id, nickname="bottle", content=msg
                    )
                    for msg in messages
                ],
            )
    else:
        await listb.finish(total_bottles_info + "\n".join(bottles_info[:10]))
    ba.add("cooldown", event.user_id)


@throw.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    await verify(matcher=matcher, event=event)

    if not args:
        await throw.finish("想说些什么话呢？在指令后边写上吧！")

    message_text = args.extract_plain_text().strip()

    audit = await text_audit(text=message_text)
    if not audit == "pass":
        if audit == "Error":
            await throw.finish("文字审核未通过！原因：调用审核API失败，请检查违禁词词表是否存在，或token是否正确设置！")
        elif audit["conclusion"] == "不合规":
            await throw.finish("文字审核未通过！原因：" + audit["data"][0]["msg"])

    try:
        group_info = await bot.get_group_info(group_id=event.group_id)
        group_name = group_info["group_name"]
    except:
        group_name = "Unknown"
    user_info = await bot.get_group_member_info(
        group_id=event.group_id, user_id=event.user_id
    )
    user_name = user_info.get("card") or user_info.get("nickname")

    add_index = await bottle_manager.add_bottle(
        user_id=event.user_id,
        group_id=event.group_id,
        content=await serialize_message(message=args),
        user_name=user_name,
        group_name=group_name,
        session=session,
    )
    await session.commit()
    if add_index:
        # 添加个人冷却
        ba.add("cooldown", event.user_id)
        await asyncio.sleep(2)
        await throw.send(
            f"你将编号No.{add_index}的漂流瓶以时速{random.randint(0,2**16)}km/h的速度扔出去，谁会捡到这个瓶子呢..."
        )
    else:
        await asyncio.sleep(2)
        await throw.send("你的瓶子以奇怪的方式消失掉了！")


@get.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    session: AsyncSession = Depends(get_session),
):
    await verify(matcher=matcher, event=event)

    bottle = await bottle_manager.select(session=session)
    if not bottle:
        await get.finish("好像一个瓶子也没有呢..要不要扔一个？")
    try:
        user_info = await bot.get_group_member_info(
            group_id=bottle.group_id, user_id=bottle.user_id
        )
        user_name = user_info.get("card") or user_info.get("nickname")
    except ActionFailed:
        user_name = bottle.user_name
    try:
        group_info = await bot.get_group_info(group_id=bottle.group_id)
        group_name = group_info["group_name"]
    except ActionFailed:
        group_name = bottle.group_name

    comments = await bottle_manager.get_comment(bottle=bottle, session=session)
    comment_str = "\n".join(
        [f"{comment.user_name}：{comment.content}" for comment in comments]
    )
    ba.add("cooldown", event.user_id)
    await get.send(
        f"【漂流瓶No.{bottle.id}|被捡到{bottle.picked}次】来自【{group_name}】的 {user_name} ！\n"
        + deserialize_message(bottle.content)
        + (f"\n★前 {len(comments)} 条评论★\n{comment_str}" if comment_str else "")
    )
    await session.commit()


@report.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    await verify(matcher=matcher, event=event)
    if not ba.verifyReport(event.user_id):
        await report.finish(ba.bannedMessage)

    index = args.extract_plain_text().strip()
    bottle = await get_bottle(index=index, matcher=matcher, session=session)
    result = await bottle_manager.report(
        bottle=bottle, user_id=event.user_id, session=session
    )
    if result == 0:
        await report.send("举报失败！")
    elif result == 1:
        ba.add("cooldown", event.user_id)
        await report.send(f"举报成功！关于此漂流瓶已经有 {bottle.report} 次举报")
        await session.commit()
    elif result == 2:
        mes = f"有一漂流瓶遭到封禁！\n编号：{bottle.id}\n用户QQ：{bottle.user_id}\n来源群组：{bottle.group_id}\n"
        mes += deserialize_message(bottle.content)
        comments = await bottle_manager.get_comment(
            bottle=bottle, session=session, limit=None
        )
        comment_str = "\n".join(
            [
                f"【{comment.user_id}】{comment.user_name}：{comment.content}"
                for comment in comments
            ]
        )
        await session.commit()

        # 私聊发送被删除的漂流瓶详情
        for i in list(bot.config.superusers):
            await bot.send_private_msg(user_id=i, message=mes)
            await bot.send_private_msg(user_id=i, message=comment_str)
            await asyncio.sleep(0.5)
        await report.send("举报成功！已经进行删除该漂流瓶处理！")
    elif result == 3:
        await report.send("该漂流瓶已经被删除！")


@comment.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    await verify(matcher=matcher, event=event)

    command = args.extract_plain_text().strip().split()
    if not command:
        await comment.finish(f"请在指令后接 漂流瓶id 评论")
    if len(command) == 1:
        await comment.finish("想评论什么呀，在后边写上吧！")
    bottle = await get_bottle(index=command[0], matcher=matcher, session=session)
    user_info = await bot.get_group_member_info(
        group_id=event.group_id, user_id=event.user_id
    )
    user_name = user_info.get("card") or user_info["nickname"]
    command[1] = command[1].strip()

    # 进行文字审核
    audit = await text_audit(text=command[1])
    if not audit == "pass":
        if audit == "Error":
            await comment.finish("文字审核未通过！原因：调用审核API失败，请检查违禁词词表格式是否正确，或token是否正确设置！")
        elif audit["conclusion"] == "不合规":
            await comment.finish("文字审核未通过！原因：" + audit["data"][0]["msg"])

    # 审核通过
    bottle_manager.comment(
        bottle=bottle,
        user_id=event.user_id,
        user_name=user_name,
        content=command[1],
        session=session,
    )
    try:
        await bot.send_group_msg(
            group_id=bottle.group_id,
            message=Message(
                MessageSegment.at(bottle.user_id)
                + f" 你的{bottle.id}号漂流瓶被评论啦！\n{command[1]}"
            ),
        )
        await asyncio.sleep(2)
    finally:
        ba.add("cooldown", event.user_id)
        await comment.send("回复成功！")
    await session.commit()


@check_bottle.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    index = args.extract_plain_text().strip()
    bottle = await get_bottle(index=index, matcher=matcher, session=session)

    try:
        user_info = await bot.get_group_member_info(
            group_id=bottle.group_id, user_id=bottle.user_id
        )
        user_name = user_info.get("card") or user_info.get("nickname")
    except ActionFailed:
        user_name = bottle.user_name
    try:
        group_info = await bot.get_group_info(group_id=bottle.group_id)
        group_name = group_info["group_name"]
    except ActionFailed:
        group_name = bottle.group_name
    comments = await bottle_manager.get_comment(bottle=bottle, session=session)
    if not comments and event.user_id != bottle.user_id:
        await check_bottle.finish(
            f"这个编号的漂流瓶还没有评论或你不是此漂流瓶的主人，不能给你看里面的东西！\n【该#{index} 漂流瓶来自【{group_name}】的 {user_name}，被捡到{bottle.picked}次，于{bottle.time.strftime('%Y-%m-%d %H:%M:%S')}扔出】"
        )
    comment_str = "\n".join(
        [f"{comment.user_name}：{comment.content}" for comment in comments]
    )
    ba.add("cooldown", event.user_id)
    await check_bottle.finish(
        f"来自【{group_name}】的 {user_name} 的第{index}号漂流瓶：\n"
        + deserialize_message(bottle.content)
        + f"\n★前 {len(comments)} 条评论★\n{comment_str}\n【被捡到{bottle.picked}次，于{bottle.time.strftime('%Y-%m-%d %H:%M:%S')}扔出】"
    )


@remove.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    arg: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    index = arg.extract_plain_text().strip()
    bottle = await get_bottle(index=index, matcher=matcher, session=session)
    if str(event.user_id) in bot.config.superusers or bottle.user_id == event.user_id:
        content_preview = get_content_preview(bottle)
        matcher.set_arg("index", int(index))
        await remove.send(f"你是否要删除漂流瓶（Y/N）？漂流瓶将会永久失去。（真的很久！）\n漂流瓶内容：{content_preview}")
    else:
        await remove.finish("删除失败！你没有相关的权限！")


@remove.got("prompt")
async def _(
    conf: str = ArgStr("prompt"),
    index: int = Arg("index"),
    session: AsyncSession = Depends(get_session),
):
    if conf in proceed:
        # 行数越少越好.jpg
        (await bottle_manager.get_bottle(index=index, session=session)).is_del = True
        await session.commit()
        await remove.send(f"成功删除 {index} 号漂流瓶！")
    else:
        await remove.finish("取消删除操作。")


###### SUPERUSER命令 ######


@resume.handle()
async def _(
    matcher: Matcher,
    arg: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    index = arg.extract_plain_text().strip()
    bottle = await get_bottle(
        index=index, matcher=matcher, session=session, include_del=True
    )
    bottle.is_del = False
    await session.commit()
    await resume.finish(f"成功恢复 {index} 号漂流瓶！")


@clear.got("prompt", prompt="你确定要清空所有漂流瓶吗？（Y/N）所有的漂流瓶都将会永久失去。（真的很久！）")
async def _(conf: str = ArgStr("prompt"), session: AsyncSession = Depends(get_session)):
    if conf in proceed:
        await bottle_manager.clear(session)
        await session.commit()
        await clear.finish("所有漂流瓶清空成功！")
    else:
        await clear.finish("取消清空操作。")


@listqq.handle()
async def _(
    matcher: Matcher,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    index = args.extract_plain_text().strip()
    bottle = await get_bottle(
        index=index, matcher=matcher, session=session, include_del=True
    )
    mes = f"漂流瓶编号：{index}\n用户QQ：{bottle.user_id}\n来源群组：{bottle.group_id}\n发送时间：{bottle.time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    await listqq.send(mes + deserialize_message(bottle.content))

    comments = await bottle_manager.get_comment(
        bottle=bottle, session=session, limit=None
    )
    comment_str = "\n".join(
        [
            f"【{comment.user_id}】{comment.user_name}：{comment.content}"
            for comment in comments
        ]
    )
    if comment_str:
        await listqq.send(comment_str)
    else:
        await listqq.send("漂流瓶暂无回复")


@ban.handle()
async def _(
    args: Message = CommandArg(),
):
    command = args.extract_plain_text().strip().split(" ")
    if command[0] in ["group", "群聊", "群号"]:
        if ba.add("group", command[1]):
            await ban.finish(f"成功封禁{command[0]}：{command[1]}")
        else:
            ba.remove("group", command[1])
            await ban.finish(f"成功解封{command[0]}：{command[1]}")

    if command[0] in ["qq", "QQ", "user", "用户", "qq号", "QQ号"]:
        if ba.add("user", command[1]):
            await ban.finish(f"成功封禁{command[0]}：{command[1]}")
        else:
            ba.remove("user", command[1])
            await ban.finish(f"成功解封{command[0]}：{command[1]}")

    if command[0] in ["report", "举报"]:
        result = ba.banreport(command[1])
        if result == 1:
            await ban.finish(f"成功取消{command[0]}权限：{command[1]}")
        elif result == 0:
            await ban.finish(f"成功赋予{command[0]}权限：{command[1]}")
        else:
            await ban.finish(result)


@white.handle()
async def _(
    args: Message = CommandArg(),
):
    command = args.extract_plain_text().strip().split(" ")
    if command[0] in ["group", "群聊", "群号"]:
        if ba.add("whiteGroup", command[1]):
            await ban.finish(f"成功设置白名单{command[0]}：{command[1]}")
        else:
            ba.remove("whiteGroup", command[1])
            await ban.finish(f"成功移除白名单{command[0]}：{command[1]}")

    if command[0] in ["qq", "QQ", "user", "用户", "qq号", "QQ号"]:
        if ba.add("whiteUser", command[1]):
            await ban.finish(f"成功设置白名单{command[0]}：{command[1]}")
        else:
            ba.remove("whiteUser", command[1])
            await ban.finish(f"成功移除白名单{command[0]}：{command[1]}")


@comrem.handle()
async def _(
    matcher: Matcher,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    command = args.extract_plain_text().strip().split()
    if len(command) != 2:
        await comrem.finish("请检查参数")
    bottle = await get_bottle(
        index=command[0], matcher=matcher, session=session, include_del=True
    )
    command[1] = command[1].strip()
    if not command[1].isdigit():
        await comrem.finish("用户id必须为数字！")
    await bottle_manager.del_comment(
        bottle=bottle, user_id=int(command[1]), session=session
    )
    await session.commit()
    await comrem.finish("删除成功！")
