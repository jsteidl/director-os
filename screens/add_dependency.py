from textual.screen import ModalScreen
from textual.widgets import Label, Input
from textual.containers import Vertical
from textual.binding import Binding


class AddDependencyScreen(ModalScreen[tuple]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    AddDependencyScreen {
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

    def __init__(self, item="", owner=""):
        super().__init__()
        self._item = item
        self._owner = owner

    def compose(self):
        yield Vertical(
            Label("Dependency  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Input(id="dependency", placeholder="Dependency", value=self._item),
            Label("Owner"),
            Input(id="owner", placeholder="Owner", value=self._owner),
        )

    def action_save(self):
        dependency = self.query_one("#dependency", Input).value
        owner = self.query_one("#owner", Input).value
        self.dismiss((dependency, owner))

    def action_cancel(self):
        self.dismiss(None)
