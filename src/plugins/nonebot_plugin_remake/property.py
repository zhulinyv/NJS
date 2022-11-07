from typing import Dict, Set

sum_data = {
    "CHR": [
        {"min": 0, "judge": "地狱", "grade": 0},
        {"min": 1, "judge": "折磨", "grade": 0},
        {"min": 2, "judge": "不佳", "grade": 0},
        {"min": 4, "judge": "普通", "grade": 0},
        {"min": 7, "judge": "优秀", "grade": 1},
        {"min": 9, "judge": "罕见", "grade": 2},
        {"min": 11, "judge": "逆天", "grade": 3},
    ],
    "MNY": [
        {"min": 0, "judge": "地狱", "grade": 0},
        {"min": 1, "judge": "折磨", "grade": 0},
        {"min": 2, "judge": "不佳", "grade": 0},
        {"min": 4, "judge": "普通", "grade": 0},
        {"min": 7, "judge": "优秀", "grade": 1},
        {"min": 9, "judge": "罕见", "grade": 2},
        {"min": 11, "judge": "逆天", "grade": 3},
    ],
    "SPR": [
        {"min": 0, "judge": "地狱", "grade": 0},
        {"min": 1, "judge": "折磨", "grade": 0},
        {"min": 2, "judge": "不幸", "grade": 0},
        {"min": 4, "judge": "普通", "grade": 0},
        {"min": 7, "judge": "幸福", "grade": 1},
        {"min": 9, "judge": "极乐", "grade": 2},
        {"min": 11, "judge": "天命", "grade": 3},
    ],
    "INT": [
        {"min": 0, "judge": "地狱", "grade": 0},
        {"min": 1, "judge": "折磨", "grade": 0},
        {"min": 2, "judge": "不佳", "grade": 0},
        {"min": 4, "judge": "普通", "grade": 0},
        {"min": 7, "judge": "优秀", "grade": 1},
        {"min": 9, "judge": "罕见", "grade": 2},
        {"min": 11, "judge": "逆天", "grade": 3},
        {"min": 21, "judge": "识海", "grade": 3},
        {"min": 131, "judge": "元神", "grade": 3},
        {"min": 501, "judge": "仙魂", "grade": 3},
    ],
    "STR": [
        {"min": 0, "judge": "地狱", "grade": 0},
        {"min": 1, "judge": "折磨", "grade": 0},
        {"min": 2, "judge": "不佳", "grade": 0},
        {"min": 4, "judge": "普通", "grade": 0},
        {"min": 7, "judge": "优秀", "grade": 1},
        {"min": 9, "judge": "罕见", "grade": 2},
        {"min": 11, "judge": "逆天", "grade": 3},
        {"min": 21, "judge": "凝气", "grade": 3},
        {"min": 101, "judge": "筑基", "grade": 3},
        {"min": 401, "judge": "金丹", "grade": 3},
        {"min": 1001, "judge": "元婴", "grade": 3},
        {"min": 2001, "judge": "仙体", "grade": 3},
    ],
    "AGE": [
        {"min": 0, "judge": "胎死腹中", "grade": 0},
        {"min": 1, "judge": "早夭", "grade": 0},
        {"min": 10, "judge": "少年", "grade": 0},
        {"min": 18, "judge": "盛年", "grade": 0},
        {"min": 40, "judge": "中年", "grade": 0},
        {"min": 60, "judge": "花甲", "grade": 1},
        {"min": 70, "judge": "古稀", "grade": 1},
        {"min": 80, "judge": "杖朝", "grade": 2},
        {"min": 90, "judge": "南山", "grade": 2},
        {"min": 95, "judge": "不老", "grade": 3},
        {"min": 100, "judge": "修仙", "grade": 3},
        {"min": 500, "judge": "仙寿", "grade": 3},
    ],
    "SUM": [
        {"min": 0, "judge": "地狱", "grade": 0},
        {"min": 41, "judge": "折磨", "grade": 0},
        {"min": 50, "judge": "不佳", "grade": 0},
        {"min": 60, "judge": "普通", "grade": 0},
        {"min": 80, "judge": "优秀", "grade": 1},
        {"min": 100, "judge": "罕见", "grade": 2},
        {"min": 110, "judge": "逆天", "grade": 3},
        {"min": 120, "judge": "传说", "grade": 3},
    ],
}


class Property:
    def __init__(self):
        self.AGE: int = -1  # 年龄 age AGE
        self.CHR: int = 0  # 颜值 charm CHR
        self.INT: int = 0  # 智力 intelligence INT
        self.STR: int = 0  # 体质 strength STR
        self.MNY: int = 0  # 家境 money MNY
        self.SPR: int = 5  # 快乐 spirit SPR
        self.LIF: int = 1  # 生命 life LIFE
        self.TMS: int = 1  # 次数 times TMS
        self.TLT: Set[int] = set()  # 天赋 talent TLT
        self.EVT: Set[int] = set()  # 事件 event EVT
        self.AVT: Set[int] = set()  # 触发过的事件 Achieve Event
        self.total: int = 20

    def apply(self, effect: Dict[str, int]):
        for key in effect:
            if key == "RDM":
                k = ["CHR", "INT", "STR", "MNY", "SPR"][id(key) % 5]
                setattr(self, k, getattr(self, k) + effect[key])
                continue
            setattr(self, key, getattr(self, key) + effect[key])

    def gen_summary(self) -> str:
        def summary(name: str, key: str):
            attr = getattr(self, key)
            judge = sum_data[key][0]["judge"]
            for res in sum_data[key]:
                if attr >= res["min"]:
                    judge = res["judge"]
                else:
                    break
            return f"{name}:  {attr}  {judge}"

        self.SUM = int(
            (self.CHR + self.INT + self.STR + self.MNY + self.SPR) * 2 + self.AGE / 2
        )
        names = {
            "CHR": "颜值",
            "INT": "智力",
            "STR": "体质",
            "MNY": "家境",
            "SPR": "快乐",
            "AGE": "享年",
            "SUM": "总评",
        }
        sums = [summary(name, key) for key, name in names.items()]
        sums = "\n".join(sums)
        return f"==人生总结==\n\n{sums}"
