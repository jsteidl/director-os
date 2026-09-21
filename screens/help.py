from textual.screen import ModalScreen
from textual.widgets import Label
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult


GROUPS_LEFT = [
    ("Tasks", [
        ("a", "Add task"),
        ("e", "Edit selected"),
        ("x", "Complete task"),
        ("s", "Send to Someday"),
        ("M", "Flag for manager update (★)"),
        ("H", "Toggle personal flag (♦)"),
        ("delete", "Delete"),
    ]),
    ("Dependencies", [
        ("a", "Add dependency"),
        ("e", "Edit selected"),
        ("x", "Resolve dependency"),
        ("r", "Move to Risk"),
        ("delete", "Delete"),
    ]),
    ("Risks", [
        ("a", "Add risk"),
        ("e", "Edit selected"),
        ("delete", "Delete"),
    ]),
]

GROUPS_RIGHT = [
    ("Someday / Future", [
        ("a", "Add someday item"),
        ("e", "Edit selected"),
        ("t", "Promote to task"),
        ("delete", "Delete"),
    ]),
    ("Accomplishments", [
        ("u", "Reopen as task"),
        ("e", "Edit accomplishment"),
        ("M", "Flag for manager update (★)"),
        ("delete", "Delete"),
    ]),
    ("Filters & Navigation", [
        ("f / F", "Tag filter forward / reverse"),
        ("[ / ]", "Project filter forward / reverse"),
        ("P", "Cycle personal filter"),
        ("v", "View widget full-screen"),
        ("!", "Daily check-in"),
        ("l", "Daily log navigator"),
        ("c", "Calendar"),
        ("b", "Briefing"),
        ("n", "Scratch pad"),
    ]),
    ("System", [
        ("R", "Refresh"),
        ("G", "Sync logs (git push)"),
        (":", "Command palette (sync/config/tags/update/weekly/events)"),
        ("n: j/k", "Select checkbox item"),
        ("n: space", "Toggle checkbox"),
        ("n: p", "Promote item to task"),
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
