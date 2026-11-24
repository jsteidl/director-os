from textual.screen import ModalScreen
from textual.widgets import Label
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult

from parser import get_all_tags, get_project_meta, get_all_projects


class ReferenceScreen(ModalScreen):

    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
    ]

    DEFAULT_CSS = """
    ReferenceScreen {
        align: center middle;
    }
    #ref-outer {
        width: 80;
        height: auto;
        max-height: 40;
        background: $surface;
        border: solid $accent;
        padding: 1 1;
    }
    #ref-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #col-projects, #col-tags {
        width: 1fr;
        height: auto;
        padding: 0 1;
    }
    .ref-section-label {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    .ref-row {
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        meta = get_project_meta()
        projects = get_all_projects()
        tags = get_all_tags()

        with Vertical(id="ref-outer"):
            yield Label("Projects & Tags  [dim](esc to close)[/dim]", id="ref-title")
            with Horizontal():
                with Vertical(id="col-projects"):
                    yield Label("Projects", classes="ref-section-label")
                    for p in projects:
                        display = meta.get(p, {}).get("display", "")
                        label = f" [bold cyan]{p}[/bold cyan]" + (f"  [dim]{display}[/dim]" if display else "")
                        yield Label(label, classes="ref-row")
                    if not projects:
                        yield Label(" [dim]none[/dim]", classes="ref-row")
                with Vertical(id="col-tags"):
                    yield Label("Tags", classes="ref-section-label")
                    for t in tags:
                        yield Label(f" [bold cyan]{t}[/bold cyan]", classes="ref-row")
                    if not tags:
                        yield Label(" [dim]none[/dim]", classes="ref-row")
