from textual.screen import ModalScreen
from textual.widgets import Input, Label, Checkbox
from textual.containers import Vertical
from textual.binding import Binding


class CompleteTaskScreen(ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    CompleteTaskScreen {
        align: center middle;
    }
    Vertical {
        width: 60;
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 1 3;
    }
    Label {
        margin-top: 1;
    }
    Input {
        margin-bottom: 1;
    }
    #handoff-fields {
        display: none;
        height: auto;
    }
    #handoff-fields.visible {
        display: block;
    }
    """

    def __init__(self, task_name: str):
        super().__init__()
        # Strip glyphs appended by the widget before using as pre-fill
        self.task_name = task_name.replace(" ↩", "").replace(" ★", "").replace(" ♦", "").strip()

    def compose(self):
        yield Vertical(
            Label(f"Complete: [bold]{self.task_name}[/bold]  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Label("Describe the business outcome:"),
            Input(id="outcome", placeholder="e.g. Implemented Snowflake MFA enforcement strategy"),
            Checkbox("Hand off to someone?", id="handoff-toggle"),
            Vertical(
                Label("Waiting on"),
                Input(id="handoff-item", placeholder="What are you waiting on?", value=self.task_name),
                Label("Owner"),
                Input(id="handoff-owner", placeholder="Owner"),
                Label("Expected date"),
                Input(id="handoff-date", placeholder="YYYY-MM-DD"),
                id="handoff-fields",
            ),
        )

    def on_checkbox_changed(self, event: Checkbox.Changed):
        fields = self.query_one("#handoff-fields")
        if event.value:
            fields.add_class("visible")
        else:
            fields.remove_class("visible")

    def action_save(self):
        outcome = self.query_one("#outcome", Input).value
        handoff = None
        if self.query_one("#handoff-toggle", Checkbox).value:
            item = self.query_one("#handoff-item", Input).value.strip()
            owner = self.query_one("#handoff-owner", Input).value.strip()
            expected = self.query_one("#handoff-date", Input).value.strip()
            if item and owner:
                handoff = (item, owner, expected or None)
        self.dismiss((outcome, handoff))

    def action_cancel(self):
        self.dismiss(None)
