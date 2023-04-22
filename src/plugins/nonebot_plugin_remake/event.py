import json
import random
from pathlib import Path
from typing import Dict, Iterator, List, Union

from .property import Property
from .utils import parse_condition


class Branch:
    def __init__(self, s: str):
        ss = s.split(":")
        self.condition = parse_condition(ss[0])
        self.event_id: int = int(ss[1])


class WeightedEvent:
    def __init__(self, s: Union[str, int]):
        if not isinstance(s, str) or "*" not in s:
            self.weight: float = 1.0
            self.event_id: int = int(s)
        else:
            ss = s.split("*")
            self.weight: float = float(ss[1])
            self.event_id: int = int(ss[0])


class Event:
    def __init__(self, data: dict):
        self.id: int = int(data["id"])
        self.name: str = data["event"]
        self.include = (
            parse_condition(data["include"]) if "include" in data else lambda _: True
        )
        self.exclude = (
            parse_condition(data["exclude"]) if "exclude" in data else lambda _: False
        )
        self.effect: Dict[str, int] = data["effect"] if "effect" in data else {}
        self.branch: List[Branch] = (
            [Branch(x) for x in data["branch"]] if "branch" in data else []
        )
        self.no_random = "NoRandom" in data and data["NoRandom"]
        self.post_event = data["postEvent"] if "postEvent" in data else None

    def check_condition(self, prop: Property) -> bool:
        return not self.no_random and self.include(prop) and not self.exclude(prop)

    def run(self, prop: Property, runner) -> Iterator[str]:
        for b in self.branch:
            if b.condition(prop):
                prop.apply(self.effect)
                yield self.name
                for text in runner(b.event_id):
                    yield text
                return
        prop.apply(self.effect)
        prop.EVT.add(self.id)
        yield self.name
        if self.post_event:
            yield self.post_event


class EventManager:
    def __init__(self, prop: Property):
        self.prop = prop
        self.events: Dict[int, Event] = {}

    def load(self, path: Path):
        data: Dict[str, dict] = json.load(path.open("r", encoding="utf8"))
        self.events = {int(k): Event(v) for k, v in data.items()}

    def rand_event(self, weighted_events: List[WeightedEvent]) -> int:
        events_checked = [
            e
            for e in weighted_events
            if self.events[e.event_id].check_condition(self.prop)
        ]
        total = sum(e.weight for e in events_checked)
        rnd = random.random() * total
        for e in events_checked:
            rnd -= e.weight
            if rnd <= 0:
                return e.event_id
        return weighted_events[0].event_id

    def run_event(self, event_id: int) -> Iterator[str]:
        return self.events[event_id].run(self.prop, self.run_event)

    def run_events(self, weighted_events: List[WeightedEvent]) -> Iterator[str]:
        event_id = self.rand_event(weighted_events)
        return self.run_event(event_id)
