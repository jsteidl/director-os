from textual.screen import ModalScreen
from textual.widgets import Label, Button
from textual.containers import Vertical, Horizontal


class ReopenTaskScreen(ModalScreen[bool]):

    def __init__(self, task_name: str):
        super().__init__()
        self.task_name = task_name

    def compose(self):

        yield Vertical(

            Label(
                f"Reopen Task\n\n{self.task_name}\n\nMove back to High-Priority?"
            ),

            Horizontal(
                Button("Reopen", id="confirm", variant="primary"),
                Button("Cancel", id="cancel"),
            ),

        )

    def on_button_pressed(self, event):

        self.dismiss(event.button.id == "confirm")
