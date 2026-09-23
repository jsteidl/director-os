from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListView, ListItem
from textual.containers import Vertical
from textual.app import ComposeResult
from textual.binding import Binding

COMMANDS = [
    ("sync",     "Sync logs (git push)"),
    ("config",   "Edit logs path"),
    ("tags",     "Tag manager"),
    ("projects", "Project manager"),
    ("update",   "Manager update"),
    ("weekly",   "Weekly review"),
    ("events",   "Events"),
    ("about",    "About director_os"),
]


class CommandScreen(ModalScreen[str | None]):

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    CommandScreen {
        align: center middle;
    }
    CommandScreen > Vertical {
        width: 50;
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    #cmd-input {
        margin-bottom: 1;
    }
    #cmd-list {
        height: auto;
        max-height: 12;
        border: none;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(placeholder="filter commands…", id="cmd-input"),
            ListView(
                *[ListItem(Label(f"[bold]{cmd}[/bold]  [dim]{desc}[/dim]"), id=f"cmd-{cmd}") for cmd, desc in COMMANDS],
                id="cmd-list",
            ),
        )

    def on_mount(self):
        self.query_one("#cmd-input", Input).focus()

    def on_input_changed(self, event: Input.Changed):
        q = event.value.strip().lower()
        lv = self.query_one("#cmd-list", ListView)
        for item in lv.query(ListItem):
            cmd_id = item.id.removeprefix("cmd-")
            item.display = q == "" or q in cmd_id
        # move highlight to first visible
        for i, item in enumerate(lv.query(ListItem)):
            if item.display:
                lv.index = i
                break

    def on_key(self, event):
        lv = self.query_one("#cmd-list", ListView)
        if event.key in ("down", "up"):
            lv.focus()
            event.prevent_default()
        elif event.key == "enter":
            self._select_highlighted(lv)
            event.prevent_default()

    def on_list_view_selected(self, event: ListView.Selected):
        cmd = event.item.id.removeprefix("cmd-")
        self.dismiss(cmd)

    def _select_highlighted(self, lv: ListView):
        highlighted = lv.highlighted_child
        if highlighted:
            cmd = highlighted.id.removeprefix("cmd-")
            self.dismiss(cmd)

    def action_cancel(self):
        self.dismiss(None)
