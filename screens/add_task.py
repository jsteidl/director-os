from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical


class AddTaskScreen(
    ModalScreen[tuple]
):

    def compose(self):

        yield Vertical(

            Label(
                "New Task"
            ),

            Input(
                id="task",
                placeholder="Task name"
            ),

            Input(
                id="tag",
                placeholder="Tag (optional)"
            )

        )

    def on_input_submitted(
        self,
        event
    ):

        task = self.query_one(
            "#task",
            Input
        ).value

        tag = self.query_one(
            "#tag",
            Input
        ).value

        self.dismiss(
            (task, tag)
        )