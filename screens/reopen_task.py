from textual.screen import ModalScreen
from textual.widgets import Label
from textual.containers import Vertical
from textual.binding import Binding


class ReopenTaskScreen(ModalScreen[bool]):

    BINDINGS = [
        Binding("enter", "confirm", "Reopen"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ReopenTaskScreen {
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
    """

    def __init__(self, task_name: str):
        super().__init__()
        self.task_name = task_name

    def compose(self):
        yield Vertical(
            Label(f"Reopen: [bold]{self.task_name}[/bold]"),
            Label("Move back to High-Priority?  [dim]enter to confirm · esc to cancel[/dim]"),
        )

    def action_confirm(self):
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)
