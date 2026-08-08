from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.binding import Binding


class AddSomedayScreen(ModalScreen[tuple]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    AddSomedayScreen {
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

    def __init__(self, item="", owner="", tags=None):
        super().__init__()
        self._item = item
        self._owner = owner
        self._tags = " ".join(tags) if tags else ""

    def compose(self):
        yield Vertical(
            Label("Someday / Future  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Input(id="item", placeholder="Item", value=self._item),
            Label("Owner"),
            Input(id="owner", placeholder="Owner", value=self._owner),
            Label("Tags"),
            Input(id="tags", placeholder="optional, space-separated without #", value=self._tags),
        )

    def action_save(self):
        item = self.query_one("#item", Input).value
        owner = self.query_one("#owner", Input).value
        tags_raw = self.query_one("#tags", Input).value
        tags = [t.strip() for t in tags_raw.split() if t.strip()]
        self.dismiss((item, owner, tags))

    def action_cancel(self):
        self.dismiss(None)
