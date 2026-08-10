import tomllib
import tomli_w
from pathlib import Path
from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Label, Input, Select
from textual.app import ComposeResult
from textual.binding import Binding

THEMES = [
    "gruvbox", "textual-dark", "textual-light", "nord",
    "monokai", "dracula", "tokyo-night", "solarized-light",
]

CONFIG_PATH = Path("config.toml")


def _load_config() -> dict:
    try:
        with open(CONFIG_PATH, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


class ConfigScreen(ModalScreen):

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ConfigScreen {
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
    Input, Select {
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        config = _load_config()
        current_theme = config.get("theme", "gruvbox")
        current_path = config.get("logs_path", "logs")

        yield Vertical(
            Label("Configuration  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Label("Logs Path"),
            Input(value=current_path, id="logs-path"),
            Label("Theme"),
            Select(
                [(t, t) for t in THEMES],
                value=current_theme,
                id="theme",
            ),
        )

    def action_save(self):
        logs_path = self.query_one("#logs-path", Input).value.strip()
        theme = self.query_one("#theme", Select).value

        config = _load_config()
        if logs_path:
            config["logs_path"] = logs_path
        if theme and theme != Select.BLANK:
            config["theme"] = str(theme)

        with open(CONFIG_PATH, "wb") as f:
            tomli_w.dump(config, f)

        self.app.theme = config.get("theme", "gruvbox")
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)
