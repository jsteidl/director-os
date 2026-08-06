from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Vertical, Horizontal


class AddRiskScreen(ModalScreen[tuple]):

    def __init__(self, description="", owner="", severity="", tags=None):
        super().__init__()
        self._description = description
        self._owner = owner
        self._severity = severity
        self._tags = " ".join(tags) if tags else ""

    def compose(self):

        yield Vertical(

            Label("Risk"),

            Input(id="description", placeholder="Risk description", value=self._description),
            Input(id="owner", placeholder="Owner", value=self._owner),
            Input(id="severity", placeholder="Severity (H, M, or L)", value=self._severity),
            Input(id="tags", placeholder="Tags (optional, space-separated without #)", value=self._tags),

            Horizontal(
                Button("Save", id="save", variant="primary"),
                Button("Cancel", id="cancel"),
            ),

        )

    def on_button_pressed(self, event):

        if event.button.id == "cancel":
            self.dismiss(None)
            return

        if event.button.id != "save":
            return

        description = self.query_one("#description", Input).value
        owner = self.query_one("#owner", Input).value
        severity = self.query_one("#severity", Input).value.upper()
        tags_raw = self.query_one("#tags", Input).value
        tags = [t.strip() for t in tags_raw.split() if t.strip()]

        self.dismiss((description, owner, severity, tags))
