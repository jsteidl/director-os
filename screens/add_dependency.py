from textual.screen import ModalScreen
from textual.widgets import Label, Input
from textual.suggester import SuggestFromList
from textual.containers import Vertical
from textual.binding import Binding
from screens.due_date import resolve_due, DUE_PLACEHOLDER, DUE_ERROR
from parser import get_all_tags, get_all_projects
from screens.tab_complete import TabCompleteMixin


class AddDependencyScreen(TabCompleteMixin, ModalScreen[tuple]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", priority=True),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    AddDependencyScreen {
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

    def __init__(self, item="", owner="", expected_date="", tags=None, project=""):
        super().__init__()
        self._item = item
        self._owner = owner
        self._expected_date = expected_date
        self._tags = " ".join(tags) if tags else ""
        self._project = project

    def compose(self):
        yield Vertical(
            Label("Dependency  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Input(id="dependency", placeholder="Dependency", value=self._item),
            Label("Owner"),
            Input(id="owner", placeholder="Owner", value=self._owner),
            Label("Expected date"),
            Input(id="expected", placeholder=DUE_PLACEHOLDER, value=self._expected_date),
            Label("Tags"),
            Input(id="tags", placeholder="optional, space-separated without #", value=self._tags,
                  suggester=SuggestFromList(get_all_tags(), case_sensitive=False)),
            Label("Project"),
            Input(id="project", placeholder="optional, no spaces (e.g. Data_Platform)", value=self._project,
                  suggester=SuggestFromList(get_all_projects(), case_sensitive=False)),
        )

    def action_save(self):
        dependency = self.query_one("#dependency", Input).value
        owner = self.query_one("#owner", Input).value
        expected_raw = self.query_one("#expected", Input).value
        expected, valid = resolve_due(expected_raw)
        if not valid:
            self.query_one("#expected", Input).border_subtitle = DUE_ERROR
            return
        tags = [t.strip() for t in self.query_one("#tags", Input).value.split() if t.strip()]
        project = self.query_one("#project", Input).value.strip()
        self.dismiss((dependency, owner, expected or None, tags, project))

    def action_cancel(self):
        self.dismiss(None)
