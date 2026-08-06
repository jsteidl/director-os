from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Button, TextArea, Static

from parser import get_weekly_summary, save_weekly_review


class WeeklyReviewScreen(ModalScreen[bool]):

    def compose(self):
        summary = get_weekly_summary()
        self._week_start = summary["week_start"]
        self._week_end = summary["week_end"]

        lines = []

        lines.append(f"[bold]Week of {self._week_start} → {self._week_end}[/bold]\n")

        lines.append("[bold]Accomplishments[/bold]")
        if summary["accomplishments"]:
            for a in summary["accomplishments"]:
                lines.append(f"  • {a.task}")
        else:
            lines.append("  None this week")

        lines.append("\n[bold]Daily Priorities (this week)[/bold]")
        if summary["entries"]:
            for e in sorted(summary["entries"], key=lambda x: x.date):
                lines.append(f"  [dim]{e.date}[/dim]")
                for p in e.priorities:
                    lines.append(f"    • {p}")
        else:
            lines.append("  No check-ins this week")

        lines.append("\n[bold]Blocked (this week)[/bold]")
        blocked = [
            (e.date, b)
            for e in summary["entries"]
            for b in e.blocked
        ]
        if blocked:
            for d, b in blocked:
                lines.append(f"  [dim]{d}[/dim] {b}")
        else:
            lines.append("  Nothing blocked")

        lines.append(f"\n[bold]Open Tasks[/bold] ({len(summary['open_tasks'])} total)")
        for t in summary["open_tasks"][:10]:
            lines.append(f"  • {t.title}")
        if len(summary["open_tasks"]) > 10:
            lines.append(f"  … and {len(summary['open_tasks']) - 10} more")

        yield Vertical(
            Label(f"Weekly Review", id="wr-title"),
            ScrollableContainer(
                Static("\n".join(lines), id="wr-summary"),
                id="wr-scroll",
            ),
            Label("Reflections / Notes"),
            TextArea("", id="wr-notes"),
            Horizontal(
                Button("Save", id="save", variant="primary"),
                Button("Close", id="close"),
                id="wr-buttons",
            ),
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save":
            notes = self.query_one("#wr-notes", TextArea).text.strip()
            if notes:
                save_weekly_review(notes, self._week_start, self._week_end)
            self.dismiss(True)
        else:
            self.dismiss(False)

    CSS = """
    WeeklyReviewScreen {
        align: center middle;
    }

    Vertical {
        width: 80%;
        height: 90%;
        border: solid $primary;
        background: $surface;
    }

    #wr-title {
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #wr-scroll {
        height: 1fr;
        padding: 1;
    }

    #wr-summary {
        height: auto;
    }

    TextArea {
        height: 6;
        margin: 0 1;
    }

    #wr-buttons {
        height: 3;
        dock: bottom;
        align: right middle;
        padding: 0 1;
    }

    #wr-buttons Button {
        margin-left: 1;
    }
    """
