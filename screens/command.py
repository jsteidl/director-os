from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical
from textual.app import ComposeResult
from textual.binding import Binding

COMMANDS = {
    "sync":    "Sync logs (git push)",
    "config":  "Edit logs path",
    "tags":    "Tag manager",
    "update":  "Manager update",
    "weekly":  "Weekly review",
    "events":  "Events",
    "help":    "List commands",
}


class CommandScreen(ModalScreen[str | None]):

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    CommandScreen {
        align: center middle;
    }
    Vertical {
        width: 50;
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    #cmd-title {
        height: 1;
        color: $text-muted;
        margin-bottom: 1;
    }
    #cmd-input {
        margin-bottom: 1;
    }
    #cmd-hint {
        height: 1;
        color: $text-muted;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[dim]Command[/dim]", id="cmd-title"),
            Input(placeholder="sync · config · tags · update · weekly · events · help", id="cmd-input"),
            Label("", id="cmd-hint"),
        )

    def on_mount(self):
        self.query_one("#cmd-input", Input).focus()

    def on_input_changed(self, event: Input.Changed):
        cmd = event.value.strip().lower()
        hint = COMMANDS.get(cmd, "")
        self.query_one("#cmd-hint", Label).update(f"[dim]{hint}[/dim]" if hint else "")

    def on_input_submitted(self, event: Input.Submitted):
        cmd = event.value.strip().lower()
        if cmd == "help":
            lines = "\n".join(f"  {k:<10} {v}" for k, v in COMMANDS.items() if k != "help")
            self.query_one("#cmd-hint", Label).update(f"[dim]{lines}[/dim]")
            return
        if cmd in COMMANDS:
            self.dismiss(cmd)
        else:
            self.query_one("#cmd-hint", Label).update("[red]Unknown command[/red]")

    def action_cancel(self):
        self.dismiss(None)
