from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.binding import Binding


class AddRiskScreen(ModalScreen[tuple]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    AddRiskScreen {
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

    def __init__(self, description="", owner="", severity="", tags=None):
        super().__init__()
        self._description = description
        self._owner = owner
        self._severity = severity
        self._tags = " ".join(tags) if tags else ""

    def compose(self):
        yield Vertical(
            Label("Risk  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Input(id="description", placeholder="Risk description", value=self._description),
            Label("Owner"),
            Input(id="owner", placeholder="Owner", value=self._owner),
            Label("Severity"),
            Input(id="severity", placeholder="H, M, or L", value=self._severity),
            Label("Tags"),
            Input(id="tags", placeholder="optional, space-separated without #", value=self._tags),
        )

    def action_save(self):
        description = self.query_one("#description", Input).value
        owner = self.query_one("#owner", Input).value
        severity = self.query_one("#severity", Input).value.upper()
        tags_raw = self.query_one("#tags", Input).value
        tags = [t.strip() for t in tags_raw.split() if t.strip()]
        self.dismiss((description, owner, severity, tags))

    def action_cancel(self):
        self.dismiss(None)
