from textual.widgets import DataTable
from rich.text import Text
from datetime import date, datetime

from parser import get_tasks

C_GOOD = "green"
C_WARN = "yellow"
C_BAD = "red"
C_DEFAULT = "default"

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"

PRIORITY_GLYPHS = {"A": "▲", "B": "●", "C": "▼"}
PRIORITY_COLORS = {"A": C_BAD, "B": C_WARN, "C": "cyan"}

def _age_color(created):
    if not created:
        return C_DEFAULT
    age = (date.today() - datetime.strptime(created, "%Y-%m-%d").date()).days
    if age >= 14:
        return C_BAD
    if age >= 7:
        return C_WARN
    return C_DEFAULT


class TaskTable(DataTable):

    personal_filter = "all"

    def on_mount(self):

        self.zebra_stripes = True
        self.add_columns("Task", "Priority", "Due", "Tags", "Created")
        self.load_tasks()

    def load_tasks(self):

        self.clear()

        for task in get_tasks():
            if self.personal_filter == "personal" and not task.personal:
                continue
            if self.personal_filter == "work" and task.personal and not task.mgr:
                continue
            color = _age_color(task.created)
            title = _t(task.title) + (" ↩" if task.carried else "") + (" ★" if task.mgr else "") + (" ♦" if task.personal else "")
            self.add_row(
                Text(title, style=color),
                Text(PRIORITY_GLYPHS.get(task.priority, task.priority or ""), style=f"bold {PRIORITY_COLORS.get(task.priority, color)}"),
                Text(task.due_date or "", style=color),
                Text(" ".join(f"#{t}" for t in task.tags) if task.tags else "", style=color),
                Text(task.created or "", style=color),
            )