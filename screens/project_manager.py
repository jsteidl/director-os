from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Input
from textual.app import ComposeResult
from textual.binding import Binding

from parser import get_project_counts, get_project_meta, rename_project, save_project_meta, delete_project_meta
from screens.tab_complete import TabCompleteMixin

C_TASKS = "#83a598"
C_DEPS  = "#fabd2f"
C_RISKS = "#fb4934"
C_SOME  = "#a89984"
C_ACCS  = "#b8bb26"
C_TOTAL = "#ebdbb2"


class ProjectManagerScreen(TabCompleteMixin, ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", priority=True),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        self._counts = get_project_counts()
        self._meta = get_project_meta()
        self._projects = sorted(self._counts.keys(), key=str.lower)
        self._tag_inputs = {}
        self._display_inputs = {}
        self._desc_inputs = {}

        rows = []
        for project in self._projects:
            c = self._counts[project]
            total = c['tasks'] + c['deps'] + c['risks'] + c['someday'] + c['accomplishments']
            m = self._meta.get(project, {})

            tag_inp = Input(value=project, id=f"tag-{project}", classes="proj-tag-input")
            disp_inp = Input(value=m.get("display", ""), placeholder="Display name", id=f"disp-{project}", classes="proj-disp-input")
            desc_inp = Input(value=m.get("description", ""), placeholder="Description", id=f"desc-{project}", classes="proj-desc-input")

            self._tag_inputs[project] = tag_inp
            self._display_inputs[project] = disp_inp
            self._desc_inputs[project] = desc_inp

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
                Vertical(
                    Horizontal(
                        Label(project, classes="proj-label"),
                        tag_inp,
                        Label(summary, classes="proj-summary"),
                        classes="proj-top-row",
                    ),
                    Horizontal(
                        Label("Display:", classes="proj-field-label"),
                        disp_inp,
                        Label("Description:", classes="proj-field-label"),
                        desc_inp,
                        classes="proj-meta-row",
                    ),
                    classes="proj-row",
                )
            )

        yield Vertical(
            Label("Project Manager  [dim]ctrl+s to save · blank tag to delete · esc to cancel[/dim]", id="pm-title"),
            Label(
                f"[{C_TASKS}]T[/] Tasks  [{C_DEPS}]D[/] Deps  [{C_RISKS}]R[/] Risks  [{C_SOME}]S[/] Someday  [{C_ACCS}]A[/] Accomplishments  [bold red]⚠[/bold red] High risk",
                id="pm-legend"
            ),
            ScrollableContainer(*rows, id="proj-list"),
        )

    def action_save(self):
        for old_proj in self._projects:
            new_tag = self.query_one(f"#tag-{old_proj}", Input).value.strip()
            display = self.query_one(f"#disp-{old_proj}", Input).value.strip()
            desc = self.query_one(f"#desc-{old_proj}", Input).value.strip()

            if not new_tag:
                delete_project_meta(old_proj)
                from parser import delete_project
                delete_project(old_proj)
                continue

            if new_tag != old_proj:
                rename_project(old_proj, new_tag)
                tag = new_tag
            else:
                tag = old_proj

            if display or desc:
                save_project_meta(tag, display, desc)
            else:
                delete_project_meta(tag)

        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)

    CSS = """
    ProjectManagerScreen {
        align: center middle;
    }

    ProjectManagerScreen > Vertical {
        width: 85%;
        height: 85%;
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
        height: auto;
        margin-bottom: 1;
        border: solid $accent-darken-3;
        padding: 0 1;
    }

    .proj-top-row {
        height: 3;
    }

    .proj-meta-row {
        height: 3;
        margin-bottom: 1;
    }

    .proj-label {
        width: 22;
        padding: 1 1;
    }

    .proj-tag-input {
        width: 20;
    }

    .proj-summary {
        width: 1fr;
        padding: 1 1;
    }

    .proj-field-label {
        width: 12;
        padding: 1 1;
        color: $text-muted;
    }

    .proj-disp-input {
        width: 20;
    }

    .proj-desc-input {
        width: 1fr;
    }
    """
