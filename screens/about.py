from textual.screen import ModalScreen
from textual.widgets import Static
from textual.containers import Vertical
from textual.binding import Binding
from textual.app import ComposeResult


class AboutScreen(ModalScreen):

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "close", "Close", show=False),
        Binding("q", "close", "Close", show=False),
    ]

    CSS = """
    AboutScreen {
        align: center middle;
    }
    AboutScreen > Vertical {
        width: 80;
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 2 4;
    }
    #about-content {
        height: auto;
    }
    """

    CONTENT = """\
[bold]director_os[/bold]  [dim]v2026.09.23[/dim]

A terminal-based productivity OS for technology leaders. 

Plain markdown files. No database. No lock-in.

[dim]─────────────────────────────────────────────[/dim]

[bold]Repository[/bold]
  https://github.com/jsteidl/director-os

[bold]License[/bold]
  MIT

[bold]Stack[/bold]
  Python · Textual

[bold]AI Disclosure[/bold]
  This project was built with significant AI assistance.
  
  Architecture, features, and code were developed
  collaboratively with Amazon Q Developer.

[dim]─────────────────────────────────────────────[/dim]

[dim]Press Enter or Esc to close[/dim]\
"""

    def compose(self) -> ComposeResult:
        yield Vertical(Static(self.CONTENT, id="about-content"))

    def action_close(self):
        self.dismiss()
