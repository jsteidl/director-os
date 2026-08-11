from textual.screen import ModalScreen
from textual.widgets import Label
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult


GROUPS_LEFT = [
    ("Tasks", [
        ("a", "Add task"),
        ("e", "Edit selected"),
        ("d", "Complete task"),
        ("delete", "Delete"),
        ("S", "Move to Someday"),
        ("m", "Flag for manager update (★)"),
    ]),
    ("Dependencies", [
        ("w", "Add dependency"),
        ("e", "Edit selected"),
        ("x", "Resolve dependency"),
        ("delete", "Delete"),
    ]),
    ("Risks", [
        ("i", "Add risk"),
        ("e", "Edit selected"),
        ("delete", "Delete"),
    ]),
]

GROUPS_RIGHT = [
    ("Someday / Future", [
        ("s", "Add someday item"),
        ("e", "Edit selected"),
        ("p", "Promote to task"),
        ("delete", "Delete"),
    ]),
    ("Accomplishments", [
        ("u", "Reopen as task"),
        ("e", "Edit accomplishment"),
        ("m", "Flag for manager update (★)"),
        ("delete", "Delete"),
    ]),
    ("Views & Navigation", [
        ("v", "View widget full-screen"),
        ("!", "Daily check-in"),
        ("l", "Daily log navigator"),
        ("W", "Weekly review"),
        ("c", "Calendar"),
        ("E", "Events"),
    ]),
    ("System", [
        ("r", "Refresh + new quote"),
        ("t", "Tag manager"),
        ("U", "Manager update"),
        ("g", "Sync logs (git push)"),
        ("C", "Config"),
        ("?", "Help"),
        ("q", "Quit"),
    ]),
]


def _render_group(group_name, shortcuts):
    yield Label(f" {group_name}", classes="group-label")
    for key, action in shortcuts:
        yield Label(f" [bold cyan]{key:<8}[/bold cyan] {action}", classes="shortcut-row")


class HelpScreen(ModalScreen):

    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
        ("?", "app.pop_screen", "Close"),
    ]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    #help-outer {
        width: 90;
        height: auto;
        background: $surface;
        border: solid $accent;
        padding: 1 1;
    }
    #help-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #col-left, #col-right {
        width: 1fr;
        height: auto;
        padding: 0 1;
    }
    .group-label {
        text-style: bold;
        color: $accent;
        margin-top: 1;
    }
    .shortcut-row {
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="help-outer"):
            yield Label("Keyboard Shortcuts  [dim](esc to close)[/dim]", id="help-title")
            with Horizontal():
                with Vertical(id="col-left"):
                    for group_name, shortcuts in GROUPS_LEFT:
                        yield from _render_group(group_name, shortcuts)
                with Vertical(id="col-right"):
                    for group_name, shortcuts in GROUPS_RIGHT:
                        yield from _render_group(group_name, shortcuts)
