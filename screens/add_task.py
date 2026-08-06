from datetime import date
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
                id="priority",
                placeholder="Priority (A, B, or C)"
            ),

            Input(
                id="due_date",
                value=date.today().isoformat(),
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

        task = self.query_one("#task", Input).value
        priority = self.query_one("#priority", Input).value.upper()
        due_date = self.query_one("#due_date", Input).value
        tag = self.query_one("#tag", Input).value

        self.dismiss(
            (task, priority, due_date, tag)
        )