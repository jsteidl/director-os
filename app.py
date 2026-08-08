from textual.app import App
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Label
from textual.containers import Vertical

from screens.dashboard import DashboardScreen
from parser import _get_logs_path


class ConfigErrorScreen(Screen):

    BINDINGS = [Binding("q", "quit", "Quit")]

    def __init__(self, path):
        super().__init__()
        self._path = path

    def compose(self):
        yield Vertical(
            Label("[bold red]director_os — Configuration Error[/bold red]"),
            Label(""),
            Label(f"Logs path not found: [bold]{self._path}[/bold]"),
            Label(""),
            Label("Check your [bold]config.toml[/bold] and ensure the path exists."),
            Label("See [bold]config.toml.example[/bold] for reference."),
            Label(""),
            Label("Press [bold]q[/bold] to quit."),
        )

    def action_quit(self):
        self.app.exit()


class DirectorOS(App):

    TITLE = "Director OS"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self):
        self.theme = "gruvbox"
        logs_path = _get_logs_path()
        if not logs_path.exists():
            self.push_screen(ConfigErrorScreen(logs_path))
        else:
            self.push_screen(DashboardScreen())


if __name__ == "__main__":

    DirectorOS().run()
