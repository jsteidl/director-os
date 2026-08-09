from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    title: str
    priority: str | None = None
    due_date: date | None = None
    created: str | None = None
    tags: list[str] = field(default_factory=list)
    carried: bool = False
    mgr: bool = False


@dataclass
class Dependency:
    item: str
    owner: str
    since: str
    age: int
    tags: list[str] = field(default_factory=list)


@dataclass
class Accomplishment:
    task: str
    outcome: str
    completed: str
    tags: list[str] = field(default_factory=list)
    mgr: bool = False


@dataclass
class Risk:
    description: str
    owner: str
    since: str
    severity: str
    tags: list[str] = field(default_factory=list)


@dataclass
class SomedayItem:
    item: str
    owner: str
    since: str
    tags: list[str] = field(default_factory=list)


@dataclass
class ResolvedDependency:
    item: str
    owner: str
    resolved: date
    notes: str


@dataclass
class Event:
    title: str
    date: str
    type: str
    location: str
    remind_days: int = 0


@dataclass
class DailyLogEntry:
    date: str
    priorities: list[str]
    accomplished: list[str]
    blocked: list[str]
    notes: list[str]