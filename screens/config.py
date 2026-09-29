import tomllib
import tomli_w
from tomllib import TOMLDecodeError
from pathlib import Path
from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Label, Input
from textual.app import ComposeResult
from textual.binding import Binding

CONFIG_PATH = Path("config.toml")


def _load_config() -> dict:
    try:
        with open(CONFIG_PATH, "rb") as f:
            return tomllib.load(f)
    except (FileNotFoundError, TOMLDecodeError):
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
        width: 80;
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
        ts = config.get("terminal_size", [])
        ts_str = f"{ts[0]}x{ts[1]}" if ts else ""

        yield Vertical(
            Label("Configuration  [dim]ctrl+s to save · esc to cancel[/dim]"),
            Label("Logs Path"),
            Input(value=config.get("logs_path", "logs"), id="logs-path"),
            Label("Calendar ICS Path  [dim]today panel agenda[/dim]"),
            Input(value=config.get("calendar_ics_path", ""), id="cal-ics"),
            Label("Calendar History ICS Path  [dim]analyze_calendar.py[/dim]"),
            Input(value=config.get("calendar_history_ics_path", ""), id="cal-history"),
            Label("Terminal Size  [dim]WxH e.g. 220x50 — leave blank to use current[/dim]"),
            Input(value=ts_str, id="terminal-size"),
        )

    def action_save(self):
        config = _load_config()

        logs_path = self.query_one("#logs-path", Input).value.strip()
        if logs_path:
            config["logs_path"] = logs_path

        cal_ics = self.query_one("#cal-ics", Input).value.strip()
        if cal_ics:
            config["calendar_ics_path"] = cal_ics
        else:
            config.pop("calendar_ics_path", None)

        cal_history = self.query_one("#cal-history", Input).value.strip()
        if cal_history:
            config["calendar_history_ics_path"] = cal_history
        else:
            config.pop("calendar_history_ics_path", None)

        ts_str = self.query_one("#terminal-size", Input).value.strip()
        if ts_str and "x" in ts_str:
            try:
                w, h = ts_str.lower().split("x")
                config["terminal_size"] = [int(w), int(h)]
            except ValueError:
                pass
        else:
            config.pop("terminal_size", None)

        with open(CONFIG_PATH, "wb") as f:
            tomli_w.dump(config, f)

        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)
