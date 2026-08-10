from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Input
from textual.app import ComposeResult
from textual.binding import Binding

from parser import get_all_tags, rename_tag


class TagManagerScreen(ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        self._tags = get_all_tags()
        self._inputs = {}

        rows = []
        for tag in self._tags:
            inp = Input(value=tag, id=f"tag-{tag}")
            self._inputs[tag] = inp
            rows.append(
                Horizontal(
                    Label(f"#{tag}", classes="tag-label"),
                    inp,
                    classes="tag-row",
                )
            )

        yield Vertical(
            Label("Tag Manager — ctrl+s to save, esc to cancel", id="tm-title"),
            ScrollableContainer(*rows, id="tag-list"),
        )

    def action_save(self):
        for old_tag, inp in self._inputs.items():
            new_tag = inp.value.strip()
            if new_tag and new_tag != old_tag:
                rename_tag(old_tag, new_tag)
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)

    CSS = """
    TagManagerScreen {
        align: center middle;
    }

    Vertical {
        width: 60%;
        height: 80%;
        border: solid $primary;
        background: $surface;
    }

    #tm-title {
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
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

    .tag-label {
        width: 20;
        padding: 1 1;
    }

    Input {
        width: 1fr;
    }


    """
