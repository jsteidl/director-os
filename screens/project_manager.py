from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Input
from textual.app import ComposeResult
from textual.binding import Binding

from parser import get_project_counts, rename_project
from screens.tab_complete import TabCompleteMixin

C_TASKS = "#83a598"   # cyan
C_DEPS  = "#fabd2f"   # yellow
C_RISKS = "#fb4934"   # red
C_SOME  = "#a89984"   # muted
C_ACCS  = "#b8bb26"   # green
C_TOTAL = "#ebdbb2"   # light
C_WARN  = "#fb4934"   # red for ⚠


class ProjectManagerScreen(TabCompleteMixin, ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", priority=True),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        self._counts = get_project_counts()
        self._projects = sorted(self._counts.keys(), key=str.lower)
        self._inputs = {}

        rows = []
        for project in self._projects:
            c = self._counts[project]
            total = c['tasks'] + c['deps'] + c['risks'] + c['someday'] + c['accomplishments']
            inp = Input(value=project, id=f"proj-{project}", classes="proj-input")
            self._inputs[project] = inp

            warn = " [bold red]⚠[/bold red]" if c['high_risks'] > 0 else ""
            summary = (
                f"[{C_TASKS}]T:{c['tasks']}[/]  "
                f"[{C_DEPS}]D:{c['deps']}[/]  "
                f"[{C_RISKS}]R:{c['risks']}[/]  "
                f"[{C_SOME}]S:{c['someday']}[/]  "
                f"[{C_ACCS}]A:{c['accomplishments']}[/]  "
                f"[{C_TOTAL}]({total})[/]"
                f"{warn}"
            )
            rows.append(
                Horizontal(
                    Label(f"+{project}", classes="proj-label"),
                    inp,
                    Label(summary, classes="proj-summary"),
                    classes="proj-row",
                )
            )

        yield Vertical(
            Label("Project Manager  [dim]ctrl+s to save · esc to cancel[/dim]", id="pm-title"),
            Label(
                f"[{C_TASKS}]T[/] Tasks  [{C_DEPS}]D[/] Deps  [{C_RISKS}]R[/] Risks  [{C_SOME}]S[/] Someday  [{C_ACCS}]A[/] Accomplishments  [bold red]⚠[/bold red] High risk",
                id="pm-legend"
            ),
            ScrollableContainer(*rows, id="proj-list"),
        )

    def action_save(self):
        for old_proj, inp in self._inputs.items():
            new_proj = inp.value.strip()
            if new_proj and new_proj != old_proj:
                rename_project(old_proj, new_proj)
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)

    CSS = """
    ProjectManagerScreen {
        align: center middle;
    }

    Vertical {
        width: 80%;
        height: 80%;
        border: solid $accent;
        background: $surface;
    }

    #pm-title {
        height: 1;
        padding: 0 1;
        background: $accent-darken-2;
        color: $background;
        text-style: bold;
    }

    #pm-legend {
        height: 1;
        padding: 0 1;
    }

    #proj-list {
        height: 1fr;
        padding: 1;
    }

    .proj-row {
        height: 3;
        margin-bottom: 1;
    }

    .proj-label {
        width: 22;
        padding: 1 1;
    }

    .proj-input {
        width: 20;
    }

    .proj-summary {
        width: 1fr;
        padding: 1 1;
    }
    """
