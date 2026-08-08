from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Label
from textual.binding import Binding


class ConfirmScreen(ModalScreen[bool]):

    BINDINGS = [
        Binding("enter", "confirm", "Confirm"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ConfirmScreen {
        align: center middle;
    }
    Vertical {
        width: 50;
        height: auto;
        border: solid $error;
        background: $surface;
        padding: 1 3;
    }
    Label {
        margin-top: 1;
        text-align: center;
    }
    """

    def __init__(self, message: str):
        super().__init__()
        self._message = message

    def compose(self):
        yield Vertical(
            Label(self._message),
            Label("[dim]enter to confirm · esc to cancel[/dim]"),
        )

    def action_confirm(self):
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)
