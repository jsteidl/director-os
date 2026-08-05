from textual.screen import ModalScreen
from textual.widgets import (
    Label,
    TextArea,
    Button,
)
from textual.containers import Vertical


class ResolveDependencyScreen(
    ModalScreen[str]
):

    def compose(self):

        yield Vertical(

            Label(
                "Resolution Notes"
            ),

            TextArea(
                id="notes"
            ),

            Button(
                "Resolve",
                id="resolve"
            ),

        )

    def on_button_pressed(
        self,
        event,
    ):

        if event.button.id != "resolve":
            return

        notes = self.query_one(
            "#notes",
            TextArea
        ).text

        self.dismiss(notes)