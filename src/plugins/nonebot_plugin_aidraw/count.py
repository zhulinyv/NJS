from collections import Counter

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent

from .config import rank_number
from .database import DrawCount


def get_rank(count: Counter) -> str:
    counts = count.most_common(rank_number or None)
    msg = "".join(
        f"\n第{i}位: 『{tag}』 ({times}次)" for i, (tag, times) in enumerate(counts, 1)
    )
    return msg or "还没有任何记录哦"


user_count = on_command("个人标签排行", aliases={"我的标签排行"})


@user_count.handle()
async def user_count_rank(event: MessageEvent):
    count = await DrawCount.get_user_count(event.user_id)
    msg = get_rank(count)
    await user_count.send(msg, at_sender=True)


group_count = on_command("本群标签排行", aliases={"群标签排行"})


@group_count.handle()
async def group_count_rank(event: GroupMessageEvent):
    count = await DrawCount.get_group_count(event.group_id)
    msg = get_rank(count)
    await group_count.send(msg, at_sender=True)
