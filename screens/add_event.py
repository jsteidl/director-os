from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Label, Input, Select
from textual.binding import Binding

EVENT_TYPES = ["Holiday", "Event", "Deadline", "OOO"]


class AddEventScreen(ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    AddEventScreen {
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
    Select {
        margin-bottom: 1;
        border: none;
    }
    """

    def __init__(self, title="", date="", type_="Event", location="All", remind_days="0"):
        super().__init__()
        self._title = title
        self._date = date
        self._type = type_
        self._location = location
        self._remind_days = remind_days

    def compose(self):
        options = [(t, t) for t in EVENT_TYPES]
        yield Vertical(
            Label("Add / Edit Event  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Label("Title"),
            Input(self._title, id="event-title"),
            Label("Date (YYYY-MM-DD)"),
            Input(self._date, id="event-date"),
            Label("Type"),
            Select(options, value=self._type, id="event-type"),
            Label("Location (e.g. US, India, All)"),
            Input(self._location, id="event-location"),
            Label("Remind Days (0 = no reminder)"),
            Input(self._remind_days, id="event-remind"),
        )

    def action_save(self):
        title = self.query_one("#event-title", Input).value.strip()
        date = self.query_one("#event-date", Input).value.strip()
        type_ = self.query_one("#event-type", Select).value
        location = self.query_one("#event-location", Input).value.strip()
        remind = self.query_one("#event-remind", Input).value.strip()
        if not title or not date:
            return
        try:
            remind_days = int(remind)
        except ValueError:
            remind_days = 0
        self.dismiss((title, date, type_, location, remind_days))

    def action_cancel(self):
        self.dismiss(None)
