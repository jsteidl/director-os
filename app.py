from textual.app import App
from textual.binding import Binding

from screens.dashboard import (
    DashboardScreen
)


class DirectorOS(App):

    TITLE = "Director OS"

    BINDINGS = [
        Binding(
            "q",
            "quit",
            "Quit"
        ),
    ]

    def on_mount(self):
        self.theme = 'gruvbox'
        
        self.push_screen(
            DashboardScreen()
        )


if __name__ == "__main__":

    DirectorOS().run()