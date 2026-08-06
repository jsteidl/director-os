from textual.widgets import Static
from textual.reactive import reactive

from parser import get_today_entry


class TodayWidget(Static):

    def on_mount(self):
        self.load_today()

    def load_today(self):
        entry = get_today_entry()

        if not entry:
            self.update("No check-in for today yet. Press [bold]t[/bold] to add one.")
            return

        lines = []

        if entry.priorities:
            lines.append("[bold]Priorities[/bold]")
            for p in entry.priorities:
                lines.append(f"  • {p}")

        if entry.accomplished:
            lines.append("\n[bold]Accomplished[/bold]")
            for a in entry.accomplished:
                lines.append(f"  • {a}")

        if entry.blocked:
            lines.append("\n[bold]Blocked[/bold]")
            for b in entry.blocked:
                lines.append(f"  • {b}")

        self.update("\n".join(lines) if lines else "No items logged today.")
