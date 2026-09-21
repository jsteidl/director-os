from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.binding import Binding
from screens.due_date import resolve_due, DUE_PLACEHOLDER, DUE_ERROR


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

    def __init__(self, title="", priority="", due_date="", tags=None, project=""):
        super().__init__()
        self._title = title
        self._priority = priority
        self._due_date = due_date
        self._tags = " ".join(tags) if tags else ""
        self._project = project

    def compose(self):
        yield Vertical(
            Label("Task  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Input(id="task", placeholder="Task name", value=self._title),
            Label("Priority"),
            Input(id="priority", placeholder="A, B, or C", value=self._priority),
            Label("Due Date"),
            Input(id="due_date", value=self._due_date, placeholder=DUE_PLACEHOLDER),
            Label("Tags"),
            Input(id="tag", placeholder="optional, space-separated without #", value=self._tags),
            Label("Project"),
            Input(id="project", placeholder="optional, without +", value=self._project),
        )

    def action_save(self):
        task = self.query_one("#task", Input).value
        priority = self.query_one("#priority", Input).value.upper()
        if priority and priority not in ("A", "B", "C"):
            self.query_one("#priority", Input).border_subtitle = "Must be A, B, or C"
            return
        due_raw = self.query_one("#due_date", Input).value
        due_date, valid = resolve_due(due_raw)
        if not valid:
            self.query_one("#due_date", Input).border_subtitle = DUE_ERROR
            return
        tag = self.query_one("#tag", Input).value
        project = self.query_one("#project", Input).value.strip()
        self.dismiss((task, priority, due_date, tag, project))

    def action_cancel(self):
        self.dismiss(None)
