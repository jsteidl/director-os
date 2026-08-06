from textual.widgets import DataTable
from rich.text import Text
from datetime import date, datetime

from parser import get_tasks

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"

def _age_color(created):
    if not created:
        return "white"
    age = (date.today() - datetime.strptime(created, "%Y-%m-%d").date()).days
    if age >= 14:
        return "red"
    if age >= 7:
        return "yellow"
    return "white"


class TaskTable(DataTable):

    def on_mount(self):

        self.zebra_stripes = True
        self.add_columns(
            "Task",
            "Priority",
            "Due",
            "Tags",
            "Created",
        )

        self.load_tasks()

    def load_tasks(self):

        self.clear()

        for task in get_tasks():
            color = _age_color(task.created)
            self.add_row(
                Text(_t(task.title), style=color),
                Text(task.priority or "", style=color),
                Text(task.due_date or "", style=color),
                Text(" ".join(f"#{t}" for t in task.tags) if task.tags else "", style=color),
                Text(task.created or "", style=color),
            )