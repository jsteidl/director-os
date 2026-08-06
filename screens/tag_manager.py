from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Input, Button
from textual.app import ComposeResult

from parser import get_all_tags, rename_tag


class TagManagerScreen(ModalScreen):

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
            Label("Tag Manager — edit to rename or merge", id="tm-title"),
            ScrollableContainer(*rows, id="tag-list"),
            Horizontal(
                Button("Save", id="save", variant="primary"),
                Button("Cancel", id="cancel"),
                id="tm-buttons",
            ),
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.dismiss(False)
            return

        for old_tag, inp in self._inputs.items():
            new_tag = inp.value.strip()
            if new_tag and new_tag != old_tag:
                rename_tag(old_tag, new_tag)

        self.dismiss(True)

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

    #tm-buttons {
        height: 3;
        dock: bottom;
        align: right middle;
        padding: 0 1;
    }

    #tm-buttons Button {
        margin-left: 1;
    }
    """
