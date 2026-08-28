from textual.screen import ModalScreen
from textual.widgets import Label, TextArea, Checkbox
from textual.containers import Vertical
from textual.binding import Binding


class DailyCheckinScreen(ModalScreen[dict]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    DailyCheckinScreen {
        align: center middle;
    }
    Vertical {
        width: 80;
        height: auto;
        max-height: 90vh;
        border: solid $accent;
        background: $surface;
        padding: 1 3;
    }
    TextArea {
        height: 4;
        margin-bottom: 1;
    }
    Label {
        margin-top: 1;
    }
    """

    def __init__(self, priorities="", accomplished="", blocked="", notes=""):
        super().__init__()
        self._priorities = priorities
        self._accomplished = accomplished
        self._blocked = blocked
        self._notes = notes

    def compose(self):
        yield Vertical(
            Label("Daily Check-in  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Label("Priorities"),
            TextArea(self._priorities, id="priorities"),
            Label("Accomplished"),
            TextArea(self._accomplished, id="accomplished"),
            Label("Blocked"),
            TextArea(self._blocked, id="blocked"),
            Label("Notes"),
            TextArea(self._notes, id="notes"),
            Checkbox("Add priorities as tasks", id="add-tasks"),
        )

    def action_save(self):
        self.dismiss({
            "priorities": self.query_one("#priorities", TextArea).text,
            "accomplished": self.query_one("#accomplished", TextArea).text,
            "blocked": self.query_one("#blocked", TextArea).text,
            "notes": self.query_one("#notes", TextArea).text,
            "add_tasks": self.query_one("#add-tasks", Checkbox).value,
        })

    def action_cancel(self):
        self.dismiss(None)