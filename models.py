from dataclasses import dataclass
from datetime import date


@dataclass
class Task:
    title: str
    priority: str | None = None
    due_date: date | None = None


@dataclass
class Dependency:
    item: str
    owner: str
    since: str
    age: int


@dataclass
class Accomplishment:
    task: str
    outcome: str
    completed: str


@dataclass
class ResolvedDependency:
    item: str
    owner: str
    resolved: date
    notes: str


@dataclass
class DailyLogEntry:
    date: str
    priorities: list[str]
    accomplished: list[str]
    blocked: list[str]
    notes: list[str]