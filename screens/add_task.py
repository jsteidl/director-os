from datetime import date, timedelta
from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.binding import Binding


DUE_SHORTHANDS = {
    "t": 0, "today": 0,
    "tm": 1, "tomorrow": 1,
    "w": 7, "week": 7,
    "2w": 14,
}


def _resolve_due(value: str) -> tuple[str, bool]:
    """Return (resolved_date_str, is_valid). Empty string is valid (no due date)."""
    if not value:
        return "", True
    lower = value.strip().lower()
    if lower in DUE_SHORTHANDS:
        return (date.today() + timedelta(days=DUE_SHORTHANDS[lower])).isoformat(), True
    if lower.startswith("+"):
        try:
            return (date.today() + timedelta(days=int(lower[1:]))).isoformat(), True
        except ValueError:
            return value, False
    try:
        date.fromisoformat(value.strip())
        return value.strip(), True
    except ValueError:
        return value, False


class AddTaskScreen(ModalScreen[tuple]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    AddTaskScreen {
        align: center middle;
    }
    Vertical {
        width: 60;
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 1 3;
    }
    Label {
        margin-top: 1;
    }
    Input {
        margin-bottom: 1;
    }
    """

    def __init__(self, title="", priority="", due_date="", tags=None):
        super().__init__()
        self._title = title
        self._priority = priority
        self._due_date = due_date
        self._tags = " ".join(tags) if tags else ""

    def compose(self):
        yield Vertical(
            Label("Task  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Input(id="task", placeholder="Task name", value=self._title),
            Label("Priority"),
            Input(id="priority", placeholder="A, B, or C", value=self._priority),
            Label("Due Date"),
            Input(id="due_date", value=self._due_date, placeholder="YYYY-MM-DD · t · tm · w · 2w · +N"),
            Label("Tags"),
            Input(id="tag", placeholder="optional, space-separated without #", value=self._tags),
        )

    def action_save(self):
        task = self.query_one("#task", Input).value
        priority = self.query_one("#priority", Input).value.upper()
        if priority and priority not in ("A", "B", "C"):
            self.query_one("#priority", Input).border_subtitle = "Must be A, B, or C"
            return
        due_raw = self.query_one("#due_date", Input).value
        due_date, valid = _resolve_due(due_raw)
        if not valid:
            self.query_one("#due_date", Input).border_subtitle = "Use YYYY-MM-DD, t, tm, w, 2w, or +N"
            return
        tag = self.query_one("#tag", Input).value
        self.dismiss((task, priority, due_date, tag))

    def action_cancel(self):
        self.dismiss(None)
