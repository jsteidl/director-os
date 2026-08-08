from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.binding import Binding


class CompleteTaskScreen(ModalScreen[str]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    CompleteTaskScreen {
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

    def __init__(self, task_name: str):
        super().__init__()
        self.task_name = task_name

    def compose(self):
        yield Vertical(
            Label(f"Complete: [bold]{self.task_name}[/bold]  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Label("Describe the business outcome:"),
            Input(id="outcome", placeholder="e.g. Implemented Snowflake MFA enforcement strategy"),
        )

    def action_save(self):
        self.dismiss(self.query_one("#outcome", Input).value)

    def action_cancel(self):
        self.dismiss(None)
