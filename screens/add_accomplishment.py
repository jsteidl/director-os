from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.containers import Vertical, Horizontal


class EditAccomplishmentScreen(ModalScreen[tuple | None]):

    def __init__(self, task: str = "", outcome: str = ""):
        super().__init__()
        self._task = task
        self._outcome = outcome

    def compose(self):
        yield Vertical(
            Label("Edit Accomplishment"),
            Input(value=self._task, placeholder="Task", id="task"),
            Input(value=self._outcome, placeholder="Outcome", id="outcome"),
            Horizontal(
                Button("Save", id="save", variant="primary"),
                Button("Cancel", id="cancel"),
            ),
        )

    def on_button_pressed(self, event):
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        task = self.query_one("#task", Input).value.strip()
        outcome = self.query_one("#outcome", Input).value.strip()
        if task:
            self.dismiss((task, outcome))
