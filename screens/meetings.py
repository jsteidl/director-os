import subprocess
import sys
from datetime import date
from pathlib import Path
from textual.screen import ModalScreen
from textual.widgets import Static, Label
from textual.containers import Vertical, ScrollableContainer
from textual.binding import Binding
from textual.app import ComposeResult


class MeetingsScreen(ModalScreen):

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("[", "prev_month", "Prev month"),
        Binding("]", "next_month", "Next month"),
    ]

    CSS = """
    MeetingsScreen {
        align: center middle;
    }
    MeetingsScreen > Vertical {
        width: 80%;
        height: 85%;
        border: solid $accent;
        background: $surface;
        padding: 0 1;
    }
    #meetings-title {
        height: 1;
        padding: 1 0;
    }
    #meetings-scroll {
        height: 1fr;
    }
    #meetings-output {
        padding: 0 1;
    }
    """

    def __init__(self, include_tentative: bool = False):
        super().__init__()
        self._include_tentative = include_tentative
        today = date.today()
        self._year = today.year
        self._month = today.month

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("", id="meetings-title"),
            ScrollableContainer(
                Static("Running…", id="meetings-output"),
                id="meetings-scroll",
            ),
        )

    def on_mount(self):
        self._run()

    def _run(self):
        from calendar import monthrange
        period = f"{self._year}-{self._month:02d}"
        tent = " (including tentative)" if self._include_tentative else ""
        self.query_one("#meetings-title", Label).update(
            f"Meeting Analysis — {period}{tent}  [dim][ ] to change month · esc to close[/dim]"
        )
        self.query_one("#meetings-output", Static).update("Running…")
        script = Path(__file__).parent.parent / "analyze_calendar.py"
        args = [sys.executable, str(script), period]
        if self._include_tentative:
            args.append("--include-tentative")
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=30)
            output = result.stdout or result.stderr or "No output."
        except subprocess.TimeoutExpired:
            output = "Analysis timed out."
        except Exception as e:
            output = f"Error: {e}"
        self.query_one("#meetings-output", Static).update(output)
        self.query_one("#meetings-scroll", ScrollableContainer).scroll_home(animate=False)

    def action_prev_month(self):
        if self._month == 1:
            self._year -= 1
            self._month = 12
        else:
            self._month -= 1
        self._run()

    def action_next_month(self):
        if self._month == 12:
            self._year += 1
            self._month = 1
        else:
            self._month += 1
        self._run()
