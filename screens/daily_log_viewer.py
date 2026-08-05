from textual.screen import Screen
from textual.widgets import Static

from parser import (
    get_daily_log_text
)


class DailyLogViewerScreen(
    Screen
):

    BINDINGS = [
        ("escape", "app.pop_screen", "Back")
    ]

    def compose(self):

        yield Static(
            get_daily_log_text()
        )
