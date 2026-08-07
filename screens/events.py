from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button, DataTable
from textual.binding import Binding

from parser import get_events, add_event, edit_event, delete_event
from screens.add_event import AddEventScreen
from screens.confirm import ConfirmScreen


class EventsScreen(ModalScreen):

    BINDINGS = [
        Binding("a", "add_event", "Add"),
        Binding("e", "edit_event", "Edit"),
        Binding("delete", "delete_event", "Delete"),
        Binding("escape", "dismiss", "Close"),
    ]

    def compose(self):
        yield Vertical(
            Label("Events", id="events-heading"),
            DataTable(id="events-table", zebra_stripes=True),
            Horizontal(
                Label("a=add  e=edit  del=delete  esc=close", id="events-hint"),
                id="events-footer",
            ),
        )

    def on_mount(self):
        table = self.query_one("#events-table", DataTable)
        table.add_columns("Title", "Date", "Type", "Location", "Remind")
        self._load()

    def _load(self):
        table = self.query_one("#events-table", DataTable)
        table.clear()
        for e in sorted(get_events(), key=lambda x: x.date):
            table.add_row(e.title, e.date, e.type, e.location, str(e.remind_days) + "d" if e.remind_days else "-")

    def action_add_event(self):
        self.app.push_screen(AddEventScreen(), self._add_callback)

    def _add_callback(self, result):
        if not result:
            return
        title, date, type_, location, remind_days = result
        add_event(title, date, type_, location, remind_days)
        self._load()

    def action_edit_event(self):
        table = self.query_one("#events-table", DataTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            old_title = str(table.get_cell_at((row, 0)))
            old_date = str(table.get_cell_at((row, 1)))
            type_ = str(table.get_cell_at((row, 2)))
            location = str(table.get_cell_at((row, 3)))
            remind = str(table.get_cell_at((row, 4))).replace("d", "").replace("-", "0")
        except Exception:
            return
        self.app.push_screen(
            AddEventScreen(old_title, old_date, type_, location, remind),
            lambda result: self._edit_callback(old_title, old_date, result),
        )

    def _edit_callback(self, old_title, old_date, result):
        if not result:
            return
        title, date, type_, location, remind_days = result
        edit_event(old_title, old_date, title, date, type_, location, remind_days)
        self._load()

    def action_delete_event(self):
        table = self.query_one("#events-table", DataTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            title = str(table.get_cell_at((row, 0)))
            date = str(table.get_cell_at((row, 1)))
        except Exception:
            return
        self.app.push_screen(
            ConfirmScreen("Delete this event? This cannot be undone."),
            lambda confirmed: self._delete_confirmed(title, date) if confirmed else None,
        )

    def _delete_confirmed(self, title, date):
        delete_event(title, date)
        self._load()

    CSS = """
    EventsScreen {
        align: center middle;
    }
    Vertical {
        width: 90%;
        height: 80%;
        border: solid $accent;
        background: $surface;
    }
    #events-heading {
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }
    #events-table {
        height: 1fr;
    }
    #events-footer {
        height: 1;
        padding: 0 1;
        background: $primary;
    }
    #events-hint {
        color: $text;
    }
    """
