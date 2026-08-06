from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Vertical, Horizontal


class CompleteTaskScreen(ModalScreen[str]):

    def __init__(self, task_name: str):
        super().__init__()
        self.task_name = task_name

    def compose(self):

        yield Vertical(

            Label(f"Complete Task\n\nTask:\n{self.task_name}\n\nDescribe the business outcome:"),

            Input(
                id="outcome",
                placeholder="Example: Implemented Snowflake MFA enforcement strategy and rollout plan"
            ),

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

        self.dismiss(self.query_one("#outcome", Input).value)