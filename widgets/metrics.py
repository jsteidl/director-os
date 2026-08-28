from textual.widgets import Static
from rich.text import Text
from datetime import date, datetime

from parser import get_metrics

C_GOOD = "green"
C_WARN = "yellow"
C_BAD = "red"


def _colored(value, label, bad_if_nonzero=False):
    t = Text()
    color = C_BAD if (bad_if_nonzero and value > 0) else C_GOOD
    t.append(str(value), style=f"bold {color}")
    t.append(f" {label}")
    return t


class MetricsWidget(Static, can_focus=True):

    def update_metrics(self):

        m = get_metrics()

        line = Text()

        line.append_text(_colored(m["overdue"], "Overdue", bad_if_nonzero=True))
        line.append("  |  ")
        line.append_text(_colored(m["high_risks"], "High Risks", bad_if_nonzero=True))
        line.append("  |  ")
        line.append_text(_colored(m["oldest_task"], "Oldest Task (d)  [dim]→ to jump[/dim]", bad_if_nonzero=True))
        line.append("  |  ")
        line.append_text(_colored(m["month_wins"], "Wins This Month"))

        self.update(line)

    def on_mount(self):
        self.update_metrics()

    def on_key(self, event):
        if event.key != "right":
            return
        from parser import get_tasks
        from datetime import date, datetime
        tasks = get_tasks()
        if not tasks:
            return
        oldest_idx = max(
            range(len(tasks)),
            key=lambda i: (
                (date.today() - datetime.strptime(tasks[i].created, "%Y-%m-%d").date()).days
                if tasks[i].created else 0
            )
        )
        from widgets.tasks import TaskTable
        table = self.app.screen.query_one(TaskTable)
        table.focus()
        table.move_cursor(row=oldest_idx)
        event.stop()
