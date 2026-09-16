from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Label, TextArea
from textual.app import ComposeResult
from textual.binding import Binding

from parser import get_scratch, save_scratch


class ScratchPadScreen(ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Close"),
    ]

    CSS = """
    ScratchPadScreen {
        align: center middle;
    }
    Vertical {
        width: 80%;
        height: 80%;
        border: solid $accent;
        background: $surface;
    }
    #scratch-title {
        height: 1;
        padding: 0 1;
        background: $accent-darken-2;
        color: $background;
        text-style: bold;
    }
    TextArea {
        height: 1fr;
    }
    #scratch-hint {
        height: 1;
        padding: 0 1;
        color: $text-muted;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Scratch Pad  [dim]ctrl+s to save · esc to close[/dim]", id="scratch-title"),
            TextArea(get_scratch(), id="scratch-area"),
            Label("[dim]scratch.md in your logs directory[/dim]", id="scratch-hint"),
        )

    def on_mount(self):
        self.query_one("#scratch-area", TextArea).focus()

    def action_save(self):
        text = self.query_one("#scratch-area", TextArea).text
        save_scratch(text)
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)
