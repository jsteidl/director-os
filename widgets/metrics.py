from textual.widgets import Static
from rich.text import Text
from datetime import date

from parser import get_tasks, get_risks, get_accomplishments, get_dependencies

C_GOOD = "green"
C_WARN = "yellow"
C_BAD = "red"


def _colored(value, label, bad_if_nonzero=False):
    t = Text()
    color = C_BAD if (bad_if_nonzero and value > 0) else C_GOOD
    t.append(str(value), style=f"bold {color}")
    t.append_text(Text.from_markup(f" {label}"))
    return t


class MetricsWidget(Static, can_focus=True):

    personal_filter = "all"

    def update_metrics(self):
        f = self.personal_filter
        today = date.today()

        tasks = get_tasks()
        tasks = [t for t in tasks
                 if not (f == "personal" and not t.personal)
                 and not (f == "work" and t.personal and not t.mgr)]

        risks = get_risks()
        risks = [r for r in risks
                 if not (f == "personal" and not r.personal)
                 and not (f == "work" and r.personal)]

        accomplishments = get_accomplishments()
        accomplishments = [a for a in accomplishments
                           if not (f == "personal" and not a.personal)
                           and not (f == "work" and a.personal and not a.mgr)]

        deps = get_dependencies()

        overdue = sum(1 for t in tasks if t.due_date and date.fromisoformat(t.due_date) < today)
        oldest_task = max(((today - date.fromisoformat(t.created)).days for t in tasks if t.created), default=0)
        high_risks = sum(1 for r in risks if r.severity.upper() == "H")
        month_wins = sum(1 for a in accomplishments if a.completed.startswith(today.strftime("%Y-%m")))
        oldest_dep = max((d.age for d in deps), default=0)

        line = Text()
        line.append_text(_colored(overdue, "Overdue", bad_if_nonzero=True))
        line.append("  |  ")
        line.append_text(_colored(high_risks, "High Risks", bad_if_nonzero=True))
        line.append("  |  ")
        line.append_text(_colored(oldest_task, "Oldest Task (d)  [dim]→ to jump[/dim]", bad_if_nonzero=True))
        line.append("  |  ")
        line.append_text(_colored(month_wins, "Wins This Month"))
        self.update(line)

    def on_mount(self):
        self.update_metrics()

    def on_key(self, event):
        if event.key != "right":
            return
        from parser import get_tasks
        tasks = get_tasks()
        if not tasks:
            return
        oldest_idx = max(
            range(len(tasks)),
            key=lambda i: (
                (date.today() - date.fromisoformat(tasks[i].created)).days
                if tasks[i].created else 0
            )
        )
        from widgets.tasks import TaskTable
        table = self.app.screen.query_one(TaskTable)
        table.focus()
        table.move_cursor(row=oldest_idx)
        event.stop()
