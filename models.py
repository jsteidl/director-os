from dataclasses import dataclass


@dataclass
class Task:
    title: str


@dataclass
class Dependency:
    def __init__(
        self,
        item,
        owner,
        since,
        age,
    ):
        self.item = item
        self.owner = owner
        self.since = since
        self.age = age


@dataclass
class Accomplishment:
    title: str