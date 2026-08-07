from textual.widgets import Static
from textual.containers import ScrollableContainer

from parser import get_today_entry


class TodayWidget(ScrollableContainer):

    def on_mount(self):
        self.load_today()

    def load_today(self):
        entry = get_today_entry()

        if not entry:
            text = "No check-in for today yet. Press [bold]![/bold] to add one."
        else:
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

            text = "\n".join(lines) if lines else "No items logged today."

        try:
            self.query_one("#today-content", Static).update(text)
        except Exception:
            self.mount(Static(text, id="today-content"))
