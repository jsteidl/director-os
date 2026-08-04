from dataclasses import dataclass


@dataclass
class Task:
    title: str


@dataclass
class Dependency:
    item: str
    owner: str
    since: str


@dataclass
class Accomplishment:
    title: str