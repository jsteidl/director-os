from dataclasses import dataclass
from datetime import date

@dataclass
class Task:
    title: str
    priority: str | None = None
    due_date: date | None = None

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