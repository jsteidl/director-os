from textual.screen import ModalScreen
from textual.widgets import Label, Input, Button
from textual.containers import Vertical, Horizontal


class AddDependencyScreen(ModalScreen[tuple]):

    def __init__(self, item="", owner=""):
        super().__init__()
        self._item = item
        self._owner = owner

    def compose(self):

        yield Vertical(

            Label("Dependency"),

            Input(id="dependency", value=self._item),

            Label("Owner"),

            Input(id="owner", value=self._owner),

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

        dependency = self.query_one("#dependency", Input).value
        owner = self.query_one("#owner", Input).value

        self.dismiss((dependency, owner))