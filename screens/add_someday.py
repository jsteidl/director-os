from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Vertical


class AddSomedayScreen(ModalScreen[tuple]):

    def compose(self):

        yield Vertical(

            Label("Someday / Future"),

            Input(
                id="item",
                placeholder="Item",
            ),

            Input(
                id="owner",
                placeholder="Owner",
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

        item = self.query_one("#item", Input).value
        owner = self.query_one("#owner", Input).value
        tags_raw = self.query_one("#tags", Input).value

        tags = [t.strip() for t in tags_raw.split() if t.strip()]

        self.dismiss((item, owner, tags))
