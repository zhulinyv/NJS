import fractions
import math
import re

from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from scipy.interpolate import lagrange

from .utils import Nums


class HomoNumber:
    # 参考并移植自 https://github.com/itorr/homo
    # 参考并移植自 https://github.com/HiDolen/nonebot_plugin_homonumber
    async def main(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ) -> None:
        number = arg.extract_plain_text()
        message = self.demolish(number)
        if message == '':
            message = '需要一个数字，这事数字吗（恼）'
        await matcher.send(message)

    def demolish(self, num_str: str) -> str:
        if not re.sub('[-.]', '', num_str).isdigit():  # 如果输入的不是数字
            return ''
        num = float(num_str) if '.' in num_str else int(num_str)
        if not math.isfinite(num):  # 若输入的不是 无穷 或 不是数字
            return f'这么臭的{num}有必要论证吗'

        if num < 0:
            return f'(11-4-5+1-4)*({self.demolish(str(num * -1))})'
        if not isinstance(num, int):  # 如果不是整数
            temp = str(num)
            start_on = temp.find('.') + 1
            length = len(temp[start_on:])
            _next = self.demolish(str(int(num*(10**length))))
            return f'({_next})/({self.demolish(str(10**length))})'

        if num in Nums:
            return Nums[num]
        div = next((one for one in Nums if num >= one), 1)  # 获取刚好比 num 大的那个数
        first_number = self.demolish(str(int(num/div)))
        second_number = self.demolish(str(int(num % div)))
        return f'({Nums[div]})*({first_number})+({second_number})'




class LagrangeInterpolation:
    async def main(
        self,
        matcher: Matcher,
        arg: Message = CommandArg()
    ) -> None:
        msg = arg.extract_plain_text().strip()
        if msg == "":
            return
        msg = msg.split(" ")
        msg = [item.strip() for item in msg if item.strip()]
        if len(msg) < 2 or not all(item.isdigit() for item in msg):
            return

        msg = [int(item) for item in msg]
        x = list(range(1, len(msg) + 1))
        coeffs = self.lagrange_fraction(x, msg)
        func = ""
        count = len(coeffs)
        for i in coeffs:
            count -= 1
            if str(i) == "0":
                continue
            if count == 0:
                func += f"({str(i)})" if int(i) < 0 else str(i)
            elif count == 1:
                func += "x+" if str(i) == "1" else f"({str(i)})x+"
            else:
                func += f"x^{count}+" if str(i) == "1" else f"({str(i)})x^{count}+"
        func = func[:-1] if func[-1] == "+" else func
        await matcher.send(f"f(x) = {func}")

    def lagrange_fraction(self, x, y) -> list:
        p = lagrange(x, y)
        c = p.c
        d = p.order
        return [fractions.Fraction(c[i]).limit_denominator() for i in range(d + 1)]


homo_number = HomoNumber()
lagrange_interpolation = LagrangeInterpolation()
