from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Vertical


class AddRiskScreen(ModalScreen[tuple]):

    def compose(self):

        yield Vertical(

            Label("New Risk"),

            Input(
                id="description",
                placeholder="Risk description",
            ),

            Input(
                id="owner",
                placeholder="Owner",
            ),

            Input(
                id="severity",
                placeholder="Severity (H, M, or L)",
            ),

            Input(
                id="tags",
                placeholder="Tags (optional, space-separated without #)",
            ),

            Button("Save", id="save"),

        )

    def on_button_pressed(self, event):

        if event.button.id != "save":
            return

        description = self.query_one("#description", Input).value
        owner = self.query_one("#owner", Input).value
        severity = self.query_one("#severity", Input).value.upper()
        tags_raw = self.query_one("#tags", Input).value

        tags = [t.strip() for t in tags_raw.split() if t.strip()]

        self.dismiss((description, owner, severity, tags))
