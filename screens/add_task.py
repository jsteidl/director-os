from datetime import date
from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.binding import Binding


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
        self._due_date = due_date or date.today().isoformat()
        self._tags = " ".join(tags) if tags else ""

    def compose(self):
        yield Vertical(
            Label("Task  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Input(id="task", placeholder="Task name", value=self._title),
            Label("Priority"),
            Input(id="priority", placeholder="A, B, or C", value=self._priority),
            Label("Due Date"),
            Input(id="due_date", value=self._due_date),
            Label("Tags"),
            Input(id="tag", placeholder="optional, space-separated without #", value=self._tags),
        )

    def action_save(self):
        task = self.query_one("#task", Input).value
        priority = self.query_one("#priority", Input).value.upper()
        due_date = self.query_one("#due_date", Input).value
        tag = self.query_one("#tag", Input).value
        self.dismiss((task, priority, due_date, tag))

    def action_cancel(self):
        self.dismiss(None)
