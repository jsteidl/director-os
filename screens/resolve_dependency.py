from textual.screen import ModalScreen
from textual.widgets import Label, TextArea
from textual.containers import Vertical
from textual.binding import Binding


class ResolveDependencyScreen(ModalScreen[str]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ResolveDependencyScreen {
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
        margin-bottom: 1;
    }
    TextArea {
        height: 6;
        margin-bottom: 1;
    }
    """

    def compose(self):
        yield Vertical(
            Label("Resolution Notes  [dim]ctrl+s to save · esc to cancel[/dim]"),
            TextArea(id="notes"),
        )

    def action_save(self):
        notes = self.query_one("#notes", TextArea).text
        self.dismiss(notes)

    def action_cancel(self):
        self.dismiss("")
