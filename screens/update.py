from datetime import date, timedelta
from textual.screen import ModalScreen
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Label, Input, Static
from textual.binding import Binding

from parser import get_update_data, save_update
from widgets.tasks import PRIORITY_GLYPHS


def _last_monday() -> str:
    today = date.today()
    return (today - timedelta(days=today.weekday())).isoformat()


class UpdateScreen(ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "generate", "Generate"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    UpdateScreen {
        align: center middle;
    }
    Vertical {
        width: 80%;
        height: 90%;
        border: solid $primary;
        background: $surface;
    }
    #update-title {
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }
    #update-scroll {
        height: 1fr;
        padding: 1;
    }
    #update-preview {
        height: auto;
    }
    #since-row {
        height: 3;
        padding: 0 1;
        align: left middle;
    }
    #since-label {
        width: auto;
        padding: 0 1 0 0;
    }
    #since-input {
        width: 20;
    }
    """

    def __init__(self):
        super().__init__()
        self._since = _last_monday()
        self._data = None

    def compose(self):
        from textual.containers import Horizontal
        yield Vertical(
            Label("Manager Update  [dim]ctrl+s to generate · esc to cancel[/dim]", id="update-title"),
            Horizontal(
                Label("Since:", id="since-label"),
                Input(value=self._since, id="since-input"),
                id="since-row",
            ),
            ScrollableContainer(
                Static("", id="update-preview"),
                id="update-scroll",
            ),
        )

    def on_mount(self):
        self._refresh_preview()

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "since-input":
            self._since = event.value
            self._refresh_preview()

    def _refresh_preview(self):
        try:
            date.fromisoformat(self._since)
        except ValueError:
            return
        self._data = get_update_data(self._since)
        lines = []

        lines.append(f"[bold]Since {self._since}[/bold]\n")

        lines.append("[bold]Accomplished[/bold]")
        if self._data["accomplished"]:
            for a in self._data["accomplished"]:
                lines.append(f"  • {a.task}")
        else:
            lines.append("  Nothing completed in this period")

        lines.append("\n[bold]In Progress[/bold]")
        if self._data["tasks"]:
            for t in self._data["tasks"]:
                glyph = PRIORITY_GLYPHS.get(t.priority, "") + " " if t.priority else ""
                due = f" (due {t.due_date})" if t.due_date else ""
                lines.append(f"  • {glyph}{t.title}{due}")
        else:
            lines.append("  No open tasks")

        lines.append("\n[bold]Waiting On[/bold]")
        if self._data["deps"]:
            for d in self._data["deps"]:
                lines.append(f"  • {d.item} — {d.owner} ({d.age}d)")
        else:
            lines.append("  Nothing pending")

        lines.append("\n[bold]Risks[/bold]")
        if self._data["risks"]:
            for r in self._data["risks"]:
                lines.append(f"  • {r.description} (owner: {r.owner})")
        else:
            lines.append("  No high severity risks")

        lines.append("\n[bold]Blocked / Notes[/bold]")
        if self._data["blocked"]:
            seen = set()
            for d, b in self._data["blocked"]:
                if b not in seen:
                    seen.add(b)
                    lines.append(f"  • {b} ({d})")
        else:
            lines.append("  Nothing blocked")

        self.query_one("#update-preview", Static).update("\n".join(lines))

    def action_generate(self):
        if not self._data:
            return
        path = save_update(self._since, self._data)
        self.dismiss(path)

    def action_cancel(self):
        self.dismiss(None)
