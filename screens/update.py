from datetime import date, timedelta
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Input, Static, Switch
from textual.binding import Binding

from parser import get_update_data, save_update
from widgets.tasks import PRIORITY_GLYPHS
from screens.due_date import resolve_since, SINCE_PLACEHOLDER


class UpdateScreen(ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "generate", "Generate"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    UpdateScreen {
        align: center middle;
    }
    Vertical {
        width: 80%;
        height: 90%;
        border: solid $primary;
        background: $surface;
    }
    #update-title {
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
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
        height: 3;
        padding: 0 1;
        align: left middle;
    }
    .filter-label {
        width: auto;
        padding: 0 1 0 0;
    }
    #since-input {
        width: 20;
    }
    """

    def __init__(self):
        super().__init__()
        today = date.today()
        self._since = (today - timedelta(days=today.weekday())).isoformat()
        self._mgr_only = True
        self._data = None

    def compose(self):
        yield Vertical(
            Label("Manager Update  [dim]ctrl+s to generate · esc to cancel[/dim]", id="update-title"),
            Horizontal(
                Label("Since:", classes="filter-label"),
                Input(value=self._since, placeholder=SINCE_PLACEHOLDER, id="since-input"),
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
        if not self._mgr_only:
            return items
        return [i for i in items if i.mgr]

    def _refresh_preview(self):
        try:
            date.fromisoformat(self._since)
        except ValueError:
            return
        self._data = get_update_data(self._since)
        tasks = self._filter(self._data["tasks"])
        accomplishments = self._filter(self._data["accomplished"])
        lines = []

        lines.append(f"[bold]Since {self._since}[/bold]\n")

        lines.append("[bold]Accomplished[/bold]")
        if accomplishments:
            for a in accomplishments:
                lines.append(f"  • {a.task}")
        else:
            lines.append("  Nothing completed in this period")

        lines.append("\n[bold]In Progress[/bold]")
        if tasks:
            for t in tasks:
                glyph = PRIORITY_GLYPHS.get(t.priority, "") + " " if t.priority else ""
                due = f" (due {t.due_date})" if t.due_date else ""
                lines.append(f"  • {glyph}{t.title}{due}")
        else:
            lines.append("  No flagged tasks" if self._mgr_only else "  No open tasks")

        lines.append("\n[bold]Waiting On[/bold]")
        if self._data["deps"]:
            for d in self._data["deps"]:
                lines.append(f"  • {d.item} — {d.owner} ({d.age}d)")
        else:
            lines.append("  Nothing pending")

        lines.append("\n[bold]Risks[/bold]")
        if self._data["risks"]:
            for r in self._data["risks"]:
                lines.append(f"  • {r.description} (owner: {r.owner})")
        else:
            lines.append("  No high severity risks")

        lines.append("\n[bold]Resolved Dependencies[/bold]")
        if self._data.get("resolved_deps"):
            for d in self._data["resolved_deps"]:
                lines.append(f"  • {d['item']} — {d['owner']} (resolved {d['resolved']})")
        else:
            lines.append("  None")

        lines.append("\n[bold]Resolved Risks[/bold]")
        if self._data.get("resolved_risks"):
            for r in self._data["resolved_risks"]:
                lines.append(f"  • {r['item']} [{r['severity']}] — {r['owner']} (resolved {r['resolved']})")
        else:
            lines.append("  None")

        lines.append("\n[bold]Blocked / Notes[/bold]")
        if self._data["blocked"]:
            seen = set()
            for d, b in self._data["blocked"]:
                if b not in seen:
                    seen.add(b)
                    lines.append(f"  • {b} ({d})")
        else:
            lines.append("  Nothing blocked")

        self.query_one("#update-preview", Static).update("\n".join(lines))

    def action_generate(self):
        if not self._data:
            return
        filtered = dict(self._data)
        filtered["tasks"] = self._filter(self._data["tasks"])
        filtered["accomplished"] = self._filter(self._data["accomplished"])
        path = save_update(self._since, filtered)
        self.dismiss(path)

    def action_cancel(self):
        self.dismiss(None)
