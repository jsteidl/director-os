from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.suggester import SuggestFromList
from textual.containers import Vertical
from textual.binding import Binding
from parser import get_all_tags, get_all_projects
from screens.tab_complete import TabCompleteMixin


class AddSomedayScreen(TabCompleteMixin, ModalScreen[tuple]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", priority=True),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    AddSomedayScreen {
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

    def __init__(self, item="", owner="", tags=None, project=""):
        super().__init__()
        self._item = item
        self._owner = owner
        self._tags = " ".join(tags) if tags else ""
        self._project = project

    def compose(self):
        yield Vertical(
            Label("Someday / Future  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Input(id="item", placeholder="Item", value=self._item),
            Label("Owner"),
            Input(id="owner", placeholder="Owner", value=self._owner),
            Label("Tags"),
            Input(id="tags", placeholder="optional, space-separated without #", value=self._tags,
                  suggester=SuggestFromList(get_all_tags(), case_sensitive=False)),
            Label("Project"),
            Input(id="project", placeholder="optional, no spaces (e.g. Data_Platform)", value=self._project,
                  suggester=SuggestFromList(get_all_projects(), case_sensitive=False)),
        )

    def action_save(self):
        item = self.query_one("#item", Input).value
        owner = self.query_one("#owner", Input).value
        tags_raw = self.query_one("#tags", Input).value
        tags = [t.strip() for t in tags_raw.split() if t.strip()]
        project = self.query_one("#project", Input).value.strip()
        self.dismiss((item, owner, tags, project))

    def action_cancel(self):
        self.dismiss(None)
