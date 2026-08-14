from textual.widgets import Static
from rich.text import Text

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


class MetricsWidget(Static):

    def update_metrics(self):

        m = get_metrics()

        line = Text()

        line.append_text(_colored(m["overdue"], "Overdue", bad_if_nonzero=True))
        line.append("  |  ")
        line.append_text(_colored(m["high_risks"], "High Risks", bad_if_nonzero=True))
        line.append("  |  ")
        line.append_text(_colored(m["oldest_task"], "Oldest Task (d)", bad_if_nonzero=True))
        line.append("  |  ")
        line.append_text(_colored(m["month_wins"], "Wins This Month"))

        self.update(line)

    def on_mount(self):
        self.update_metrics()
