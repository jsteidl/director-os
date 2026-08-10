import subprocess
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

    def action_quit(self):
        logs_path = str(_get_logs_path())
        try:
            subprocess.run(["git", "-C", logs_path, "add", "-A"], capture_output=True)
            r = subprocess.run(["git", "-C", logs_path, "commit", "-m", "sync"], capture_output=True, text=True)
            if "nothing to commit" not in r.stdout and r.returncode == 0:
                subprocess.run(["git", "-C", logs_path, "push"], capture_output=True)
        except Exception:
            pass
        self.exit()

    def on_mount(self):
        try:
            import tomllib
            with open("config.toml", "rb") as f:
                config = tomllib.load(f)
            self.theme = config.get("theme", "gruvbox")
        except Exception:
            self.theme = "gruvbox"
        logs_path = _get_logs_path()
        if not logs_path.exists():
            self.push_screen(ConfigErrorScreen(logs_path))
        else:
            self.push_screen(DashboardScreen())


if __name__ == "__main__":

    DirectorOS().run()
