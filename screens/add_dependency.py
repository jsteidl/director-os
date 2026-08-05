from textual.screen import ModalScreen
from textual.widgets import (
    Label,
    Input,
    Button,
)
from textual.containers import Vertical


class AddDependencyScreen(
    ModalScreen[tuple]
):

    def compose(self):

        yield Vertical(

            Label("Dependency"),

            Input(
                id="dependency"
            ),

            Label("Owner"),

            Input(
                id="owner"
            ),

            Button(
                "Save",
                id="save"
            )

        )

    def on_button_pressed(
        self,
        event,
    ):

        if event.button.id != "save":
            return

        dependency = self.query_one(
            "#dependency",
            Input
        ).value

        owner = self.query_one(
            "#owner",
            Input
        ).value

        self.dismiss(
            (
                dependency,
                owner,
            )
        )