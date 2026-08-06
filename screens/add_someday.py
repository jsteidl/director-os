from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Vertical, Horizontal


class AddSomedayScreen(ModalScreen[tuple]):

    def __init__(self, item="", owner="", tags=None):
        super().__init__()
        self._item = item
        self._owner = owner
        self._tags = " ".join(tags) if tags else ""

    def compose(self):

        yield Vertical(

            Label("Someday / Future"),

            Input(id="item", placeholder="Item", value=self._item),
            Input(id="owner", placeholder="Owner", value=self._owner),
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

        item = self.query_one("#item", Input).value
        owner = self.query_one("#owner", Input).value
        tags_raw = self.query_one("#tags", Input).value
        tags = [t.strip() for t in tags_raw.split() if t.strip()]

        self.dismiss((item, owner, tags))
