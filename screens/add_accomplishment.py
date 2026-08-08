from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.binding import Binding


class EditAccomplishmentScreen(ModalScreen[tuple | None]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    EditAccomplishmentScreen {
        align: center middle;
    }
    Vertical {
        width: 60;
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 1 3;
    }
    Label {
        margin-top: 1;
    }
    Input {
        margin-bottom: 1;
    }
    """

    def __init__(self, task: str = "", outcome: str = ""):
        super().__init__()
        self._task = task
        self._outcome = outcome

    def compose(self):
        yield Vertical(
            Label("Edit Accomplishment  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Label("Task"),
            Input(value=self._task, placeholder="Task", id="task"),
            Label("Outcome"),
            Input(value=self._outcome, placeholder="Outcome", id="outcome"),
        )

    def action_save(self):
        task = self.query_one("#task", Input).value.strip()
        outcome = self.query_one("#outcome", Input).value.strip()
        if task:
            self.dismiss((task, outcome))

    def action_cancel(self):
        self.dismiss(None)
