import json
import random
from pathlib import Path
from typing import Dict, List, Iterator

from .property import Property
from .utils import parse_condition


class Talent:
    def __init__(self, data):
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.grade: int = int(data["grade"])
        self.exclusive: List[int] = (
            [int(x) for x in data["exclusive"]] if "exclusive" in data else []
        )
        self.effect: Dict[str, int] = data["effect"] if "effect" in data else {}
        self.status = int(data["status"]) if "status" in data else 0
        self.condition = (
            parse_condition(data["condition"])
            if "condition" in data
            else lambda _: True
        )

    def __str__(self) -> str:
        return f"{self.name}（{self.description}）"

    def exclusive_with(self, talent: "Talent") -> bool:
        return talent.id in self.exclusive or self.id in talent.exclusive

    def check_condition(self, prop: Property) -> bool:
        return self.condition(prop)

    def run(self, prop: Property) -> List[str]:
        if self.check_condition(prop):
            prop.apply(self.effect)
            prop.TLT.add(self.id)
            return [f"天赋【{self.name}】发动：{self.description}"]
        return []


class TalentManager:
    def __init__(self, prop: Property):
        self.prop = prop
        self.talents: List[Talent] = []
        self.talent_dict: Dict[int, List[Talent]] = {}
        self.grade_count = 4
        self.grade_prob = [0.889, 0.1, 0.01, 0.001]

    def load(self, path: Path):
        data: dict = json.load(path.open("r", encoding="utf8"))
        talent_list: List[Talent] = [Talent(data) for data in data.values()]
        self.talent_dict = {
            i: [t for t in talent_list if t.grade == i] for i in range(self.grade_count)
        }

    def rand_talents(self, count: int) -> Iterator[Talent]:
        def rand_grade():
            rnd = random.random()
            result = self.grade_count
            while rnd > 0:
                result -= 1
                rnd -= self.grade_prob[result]
            return result

        counts = {i: 0 for i in range(self.grade_count)}
        for _ in range(count):
            counts[rand_grade()] += 1
        for grade in range(self.grade_count - 1, -1, -1):
            count = counts[grade]
            n = len(self.talent_dict[grade])
            if count > n:
                counts[grade - 1] += count - n
                count = n
            for talent in random.sample(self.talent_dict[grade], k=count):
                yield talent

    def update_talent_prop(self):
        self.prop.total += sum(t.status for t in self.talents)

    def update_talent(self) -> Iterator[str]:
        for t in self.talents:
            if t.id in self.prop.TLT:
                continue
            for result in t.run(self.prop):
                yield result

    def add_talent(self, talent: Talent):
        for t in self.talents:
            if t.id == talent.id:
                return
        self.talents.append(talent)
