from textual.screen import ModalScreen
from textual.widgets import DataTable, Label
from textual.containers import Vertical
from textual.binding import Binding


class WidgetViewerScreen(ModalScreen):

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]

    def __init__(self, title: str, columns: list[str], rows: list[tuple]):
        super().__init__()
        self._title = title
        self._columns = columns
        self._rows = rows

    def compose(self):
        yield Vertical(
            Label(self._title, id="viewer-title"),
            DataTable(id="viewer-table"),
        )

    def on_mount(self):
        table = self.query_one("#viewer-table", DataTable)
        table.add_columns(*self._columns)
        for row in self._rows:
            table.add_row(*row)

    CSS = """
    WidgetViewerScreen {
        align: center middle;
    }

    #viewer-title {
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    Vertical {
        width: 90%;
        height: 80%;
        border: solid $primary;
        background: $surface;
    }

    #viewer-table {
        height: 1fr;
    }
    """
