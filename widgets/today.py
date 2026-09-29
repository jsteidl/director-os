from textual.widgets import Static
from textual.containers import ScrollableContainer
from textual.css.query import NoMatches

from parser import get_today_entry
from parser.calendar import get_agenda, format_agenda_line


class TodayWidget(ScrollableContainer):

    def on_mount(self):
        self.load_today()

    def load_today(self):
        entry = get_today_entry()
        agenda = get_agenda()
        lines = []

        if agenda:
            lines.append("[bold]Agenda[/bold]")
            for e in agenda:
                lines.append(format_agenda_line(e))

        if not entry:
            if not agenda:
                text = "No check-in for today yet. Press [bold]![/bold] to add one."
            else:
                lines.append("\nNo check-in yet. Press [bold]![/bold] to add one.")
                text = "\n".join(lines)
        else:
            if agenda:
                lines.append("")

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

            if entry.notes:
                lines.append("\n[bold]Notes[/bold]")
                for n in entry.notes:
                    lines.append(f"  • {n}")

            text = "\n".join(lines) if lines else "No items logged today."

        try:
            self.query_one("#today-content", Static).update(text)
        except NoMatches:
            self.mount(Static(text, id="today-content"))
