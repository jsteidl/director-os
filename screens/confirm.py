from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button


class ConfirmScreen(ModalScreen[bool]):

    def __init__(self, message: str):
        super().__init__()
        self._message = message

    def compose(self):
        yield Vertical(
            Label(self._message, id="confirm-message"),
            Horizontal(
                Button("Delete", id="confirm", variant="error"),
                Button("Cancel", id="cancel"),
                id="confirm-buttons",
            ),
        )

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id == "confirm")

    CSS = """
    ConfirmScreen {
        align: center middle;
    }

    Vertical {
        width: 50;
        height: auto;
        border: solid $error;
        background: $surface;
        padding: 1;
    }

    #confirm-message {
        padding: 1;
        text-align: center;
    }

    #confirm-buttons {
        height: 3;
        align: center middle;
        margin-top: 1;
    }

    #confirm-buttons Button {
        margin: 0 1;
    }
    """
