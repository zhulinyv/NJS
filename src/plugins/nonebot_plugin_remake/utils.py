import re
from typing import List


class DummyList(list):
    def __init__(self, l: List[int]):
        super().__init__(l)

    def __contains__(self, o: object) -> bool:
        if type(o) is set:
            for x in self:
                if x in o:
                    return True
            return False
        return super().__contains__(o)


def parse_condition(cond: str):
    reg_attr = re.compile("[A-Z]{3}")
    cond2 = (
        reg_attr.sub(
            lambda m: f'getattr(x, "{m.group()}")', cond.replace("AEVT", "AVT")
        )
        .replace("?[", " in DummyList([")
        .replace("![", "not in DummyList([")
        .replace("]", "])")
        .replace("|", " or ")
    )
    while True:
        try:
            func = eval(f"lambda x: {cond2}")
            func.__doc__ = cond2
            return func
        except:
            print(f"[WARNING] missing ) in {cond}")
            cond2 += ")"
