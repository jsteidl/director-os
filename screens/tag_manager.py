from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Input
from textual.app import ComposeResult
from textual.binding import Binding

from parser import get_tag_counts, rename_tag, delete_tag
from screens.tab_complete import TabCompleteMixin


class TagManagerScreen(TabCompleteMixin, ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", priority=True),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        self._counts = get_tag_counts()
        self._tags = sorted(self._counts.keys(), key=str.lower)
        self._inputs = {}

        rows = []
        for tag in self._tags:
            count = self._counts[tag]
            inp = Input(value=tag, id=f"tag-{tag}", classes="tag-input")
            self._inputs[tag] = inp
            count_label = Label(
                f"[dim]{count}[/dim]" if count > 0 else "[red]0[/red]",
                classes="tag-count",
            )
            rows.append(
                Horizontal(
                    Label(f"#{tag}", classes="tag-label"),
                    inp,
                    count_label,
                    classes="tag-row" + (" zero-count" if count == 0 else ""),
                )
            )

        yield Vertical(
            Label("Tag Manager  [dim]ctrl+s to save · esc to cancel · clear to delete[/dim]", id="tm-title"),
            ScrollableContainer(*rows, id="tag-list"),
        )

    def action_save(self):
        for old_tag, inp in self._inputs.items():
            new_tag = inp.value.strip()
            if not new_tag:
                delete_tag(old_tag)
            elif new_tag != old_tag:
                rename_tag(old_tag, new_tag)
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)

    CSS = """
    TagManagerScreen {
        align: center middle;
    }

    Vertical {
        width: 70%;
        height: 80%;
        border: solid $accent;
        background: $surface;
    }

    #tm-title {
        height: 1;
        padding: 0 1;
        background: $accent-darken-2;
        color: $background;
        text-style: bold;
    }

    #tag-list {
        height: 1fr;
        padding: 1;
    }

    .tag-row {
        height: 3;
        margin-bottom: 1;
    }

    .zero-count .tag-label {
        color: $text-muted;
    }

    .tag-label {
        width: 22;
        padding: 1 1;
    }

    .tag-input {
        width: 1fr;
    }

    .tag-count {
        width: 5;
        padding: 1 1;
        text-align: right;
    }
    """
