from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.suggester import SuggestFromList
from textual.containers import Vertical
from textual.binding import Binding
from parser import get_all_tags, get_all_projects
from screens.tab_complete import TabCompleteMixin


class AddAccomplishmentScreen(TabCompleteMixin, ModalScreen[tuple | None]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", priority=True),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    AddAccomplishmentScreen {
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

    def compose(self):
        yield Vertical(
            Label("Accomplishment  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Input(id="task", placeholder="What did you accomplish?"),
            Label("Outcome  [dim]optional[/dim]"),
            Input(id="outcome", placeholder="Result or impact"),
            Label("Tags"),
            Input(id="tags", placeholder="optional, space-separated without #",
                  suggester=SuggestFromList(get_all_tags(), case_sensitive=False)),
            Label("Project"),
            Input(id="project", placeholder="optional, no spaces (e.g. Data_Platform)",
                  suggester=SuggestFromList(get_all_projects(), case_sensitive=False)),
        )

    def action_save(self):
        task = self.query_one("#task", Input).value.strip()
        if not task:
            return
        outcome = self.query_one("#outcome", Input).value.strip()
        tags = [t.strip() for t in self.query_one("#tags", Input).value.split() if t.strip()]
        project = self.query_one("#project", Input).value.strip()
        self.dismiss((task, outcome, tags, project))

    def action_cancel(self):
        self.dismiss(None)


class EditAccomplishmentScreen(TabCompleteMixin, ModalScreen[tuple | None]):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", priority=True),
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

    def __init__(self, task: str = "", outcome: str = "", tags: list | None = None, project: str = ""):
        super().__init__()
        self._task = task
        self._outcome = outcome
        self._tags = " ".join(tags) if tags else ""
        self._project = project

    def compose(self):
        yield Vertical(
            Label("Edit Accomplishment  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Label("Task"),
            Input(value=self._task, placeholder="Task", id="task"),
            Label("Outcome"),
            Input(value=self._outcome, placeholder="Outcome", id="outcome"),
            Label("Tags"),
            Input(value=self._tags, placeholder="optional, space-separated without #", id="tags",
                  suggester=SuggestFromList(get_all_tags(), case_sensitive=False)),
            Label("Project"),
            Input(value=self._project, placeholder="optional, no spaces (e.g. Data_Platform)", id="project",
                  suggester=SuggestFromList(get_all_projects(), case_sensitive=False)),
        )

    def action_save(self):
        task = self.query_one("#task", Input).value.strip()
        outcome = self.query_one("#outcome", Input).value.strip()
        tags = [t.strip() for t in self.query_one("#tags", Input).value.split() if t.strip()]
        project = self.query_one("#project", Input).value.strip()
        if task:
            self.dismiss((task, outcome, tags, project))

    def action_cancel(self):
        self.dismiss(None)
