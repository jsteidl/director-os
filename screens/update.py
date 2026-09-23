from datetime import date, timedelta
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Input, Static, Switch, ListView, ListItem
from textual.binding import Binding

from parser import get_update_data, save_update, get_project_meta
from screens.due_date import resolve_since

SINCE_PRESETS = [
    ("Today",           "t"),
    ("Yesterday",       "y"),
    ("Last 7 days",     "-7"),
    ("Last 2 weeks",    "-2w"),
    ("Last 30 days",    "-30"),
    ("This week (Mon)", "lw"),
    ("Custom date…",    "custom"),
]


class UpdateScreen(ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "generate", "Generate"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    UpdateScreen {
        align: center middle;
    }
    UpdateScreen > Vertical {
        width: 80%;
        height: 90%;
        border: solid $accent;
        background: $surface;
    }
    #update-title {
        height: 1;
        padding: 0 1;
        background: $accent-darken-2;
        color: $background;
        text-style: bold;
    }
    #update-scroll {
        height: 1fr;
        padding: 1;
    }
    #update-preview {
        height: auto;
    }
    .filter-row {
        height: auto;
        padding: 0 1;
        align: left middle;
    }
    .filter-label {
        width: auto;
        padding: 0 1 0 0;
    }
    #since-list {
        width: 22;
        height: auto;
        max-height: 9;
        border: none;
        margin-right: 1;
    }
    #since-input {
        width: 22;
        display: none;
    }
    #since-input.visible {
        display: block;
    }
    """

    def __init__(self):
        super().__init__()
        today = date.today()
        self._since = (today - timedelta(days=today.weekday())).isoformat()
        self._mgr_only = True
        self._data = None

    def compose(self):
        items = [ListItem(Label(label), id=f"preset-{i}") for i, (label, _) in enumerate(SINCE_PRESETS)]
        yield Vertical(
            Label("Manager Update  [dim]ctrl+s to generate · esc to cancel[/dim]", id="update-title"),
            Horizontal(
                Label("Since:", classes="filter-label"),
                ListView(*items, id="since-list"),
                Input(placeholder="YYYY-MM-DD or shorthand", id="since-input"),
                Label("  ★ flagged only:", classes="filter-label"),
                Switch(value=True, id="mgr-switch"),
                classes="filter-row",
            ),
            ScrollableContainer(
                Static("", id="update-preview"),
                id="update-scroll",
            ),
        )

    def on_mount(self):
        self.query_one("#since-list", ListView).index = 5
        self._refresh_preview()

    def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.id != "since-list":
            return
        idx = list(event.list_view.children).index(event.item)
        _, shorthand = SINCE_PRESETS[idx]
        inp = self.query_one("#since-input", Input)
        if shorthand == "custom":
            inp.add_class("visible")
            inp.value = self._since
            inp.focus()
        else:
            inp.remove_class("visible")
            resolved, valid = resolve_since(shorthand)
            if valid:
                self._since = resolved
                self._refresh_preview()

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "since-input":
            resolved, valid = resolve_since(event.value)
            if valid:
                self._since = resolved
                self._refresh_preview()

    def on_switch_changed(self, event: Switch.Changed):
        self._mgr_only = event.value
        self._refresh_preview()

    def _filter(self, items):
        items = [i for i in items if not i.personal]
        return [i for i in items if i.mgr] if self._mgr_only else items

    def _filter_deps(self, deps):
        deps = [d for d in deps if not getattr(d, "personal", False)]
        return [d for d in deps if d.mgr] if self._mgr_only else deps

    def _filter_risks(self, risks):
        risks = [r for r in risks if not r.personal]
        return [r for r in risks if r.severity.upper() == "H" or r.mgr]

    def _star(self, item):
        return " ★" if (not self._mgr_only and item.mgr) else ""

    def _tags(self, item):
        return f" [dim]{' '.join(f'#{t}' for t in item.tags)}[/dim]" if item.tags else ""

    def _build_lines(self, tasks, accomplishments, deps, risks, resolved_deps, resolved_risks, blocked):
        meta = get_project_meta()
        all_projects = sorted(
            {i.project for i in [*tasks, *accomplishments, *deps, *risks] if i.project},
            key=str.lower
        )
        lines = []

        for project in [*all_projects, None]:
            pt = sorted([i for i in tasks if i.project == project], key=lambda t: t.due_date or "9999")
            pa = [i for i in accomplishments if i.project == project]
            pd = [i for i in deps if i.project == project]
            pr = [i for i in risks if i.project == project]
            if not any([pt, pa, pd, pr]):
                continue

            if project:
                m = meta.get(project, {})
                display = m.get("display") or project
                description = m.get("description", "")
                due_dates = sorted(t.due_date for t in pt if t.due_date)
                due_str = f"next due {due_dates[0]}" if due_dates else "no due dates"
                lines.append(f"\n[bold]{display}[/bold]  [dim]{len(pt)} open · {len(pa)} done · {due_str}[/dim]")
                if description:
                    lines.append(f"  [dim italic]{description}[/dim italic]")
            else:
                lines.append("\n[bold](General)[/bold]")

            if pa:
                lines.append("  [bold]Accomplished[/bold]")
                for a in pa:
                    label = f"{a.task} — {a.outcome}" if a.outcome else a.task
                    lines.append(f"    • {label}{self._tags(a)}{self._star(a)}")

            if pt:
                lines.append("  [bold]In Progress[/bold]")
                for t in pt:
                    due = f" [dim](due {t.due_date})[/dim]" if t.due_date else ""
                    lines.append(f"    • {t.title}{due}{self._tags(t)}{self._star(t)}")

            if pd:
                lines.append("  [bold]Waiting On[/bold]")
                for d in pd:
                    lines.append(f"    • {d.item} — {d.owner} ({d.age}d){self._tags(d)}{self._star(d)}")

            if pr:
                lines.append("  [bold]Risks[/bold]")
                for r in pr:
                    lines.append(f"    • [{r.severity}] {r.description} (owner: {r.owner}){self._tags(r)}{self._star(r)}")

        lines.append("\n[dim]─────────────────────────────────────────[/dim]")

        lines.append("\n[bold]Resolved Dependencies[/bold]")
        if resolved_deps:
            for d in resolved_deps:
                lines.append(f"  • {d['item']} — {d['owner']} (resolved {d['resolved']})")
        else:
            lines.append("  None")

        lines.append("\n[bold]Resolved Risks[/bold]")
        if resolved_risks:
            for r in resolved_risks:
                lines.append(f"  • {r['item']} [{r['severity']}] — {r['owner']} (resolved {r['resolved']})")
        else:
            lines.append("  None")

        lines.append("\n[bold]Blocked / Notes[/bold]")
        if blocked:
            seen = set()
            for d, b in blocked:
                if b not in seen:
                    seen.add(b)
                    lines.append(f"  • {b} ({d})")
        else:
            lines.append("  Nothing blocked")

        return lines

    def _refresh_preview(self):
        try:
            date.fromisoformat(self._since)
        except ValueError:
            return
        self._data = get_update_data(self._since)
        tasks = self._filter(self._data["tasks"])
        accomplishments = self._filter(self._data["accomplished"])
        deps = self._filter_deps(self._data["deps"])
        risks = self._filter_risks(self._data["risks"])
        resolved_deps = self._data.get("resolved_deps", [])
        resolved_risks = self._data.get("resolved_risks", [])
        blocked = self._data["blocked"]

        lines = [f"[bold]Since {self._since}[/bold]\n"]
        lines += self._build_lines(tasks, accomplishments, deps, risks, resolved_deps, resolved_risks, blocked)
        self.query_one("#update-preview", Static).update("\n".join(lines))

    def action_generate(self):
        if not self._data:
            return
        filtered = dict(self._data)
        filtered["tasks"] = self._filter(self._data["tasks"])
        filtered["accomplished"] = self._filter(self._data["accomplished"])
        filtered["deps"] = self._filter_deps(self._data["deps"])
        filtered["risks"] = self._filter_risks(self._data["risks"])
        path = save_update(self._since, filtered)
        self.dismiss(path)

    def action_cancel(self):
        self.dismiss(None)
