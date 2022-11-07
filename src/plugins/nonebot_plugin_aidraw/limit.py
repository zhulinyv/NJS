from collections import defaultdict
from datetime import datetime

from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import Depends
from pydantic import BaseModel, Field

from .config import daily_times


class DailyLimiter(BaseModel):
    max: int
    day: int = Field(default=0, init=False)
    count: defaultdict = Field(defaultdict(int), init=False)

    def last(self, key: int) -> int:
        return self.max - self.count[key]

    def increase(self, key: int) -> None:
        self.count[key] += 1

    def check(self, key: int) -> bool:
        today = datetime.now().day
        if self.day != today:
            self.day = today
            self.count.clear()
        return self.count[key] < self.max


limiter = DailyLimiter(max=daily_times)


def daily_limiter():
    async def _daily_limiter(matcher: Matcher, event: MessageEvent):
        if not limiter.check(event.user_id):
            await matcher.finish("今日画图次数已用完, 明天再来吧~")

    return Depends(_daily_limiter)
