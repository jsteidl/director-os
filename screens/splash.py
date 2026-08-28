from textual.screen import ModalScreen
from textual.widgets import Label, Static
from textual.containers import Vertical, Center
from textual.binding import Binding
from datetime import date

STYLE = "minimal"

_ART_BLOCK = """\
[bold cyan]
  ██████╗ ██╗██████╗ ███████╗ ██████╗████████╗ ██████╗ ██████╗      ██████╗ ███████╗
  ██╔══██╗██║██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗    ██╔═══██╗██╔════╝
  ██║  ██║██║██████╔╝█████╗  ██║        ██║   ██║   ██║██████╔╝    ██║   ██║███████╗
  ██║  ██║██║██╔══██╗██╔══╝  ██║        ██║   ██║   ██║██╔══██╗    ██║   ██║╚════██║
  ██████╔╝██║██║  ██║███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║    ╚██████╔╝███████║
  ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝     ╚═════╝ ╚══════╝
[/bold cyan]"""

_ART_SLIM = """\
[bold green]
   ___ ___ ___ ___ ___ _____ ___  ___     ___  ___
  |   \_ _| _ \ __/ __|_   _/ _ \| _ \   / _ \/ __|
  | |) | ||   / _| (__  | || (_) |   /  | (_) \__ \\
  |___/___|_|_\___\___| |_| \___/|_|_\   \___/|___/
[/bold green]"""

_ART_MINIMAL = """\
[bold green]──────────────────────────────────────────────────────[/bold green]
[bold white]                    director_os[/bold white]
[bold green]──────────────────────────────────────────────────────[/bold green]"""

_ARTS = {"block": _ART_BLOCK, "slim": _ART_SLIM, "minimal": _ART_MINIMAL}
_WIDTHS = {"block": 92, "slim": 60, "minimal": 60}


class BriefingScreen(ModalScreen):

    BINDINGS = [Binding("escape", "dismiss_briefing", show=False)]

    DEFAULT_CSS = """
    BriefingScreen {
        align: center middle;
    }
    #splash-outer {
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    #splash-outer.block { width: 92; }
    #splash-outer.slim  { width: 60; }
    #splash-outer.minimal { width: 60; }
    #ascii {
        width: 100%;
        text-align: center;
    }
    #splash-date {
        text-align: center;
        color: $accent;
        margin-bottom: 1;
    }
    .splash-section {
        color: $accent;
        text-style: bold;
        margin-top: 1;
    }
    .splash-row   { margin-left: 2; }
    .splash-bad   { margin-left: 2; color: red; }
    .splash-warn  { margin-left: 2; color: yellow; }
    .splash-good  { margin-left: 2; color: green; }
    #splash-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    def on_key(self, event) -> None:
        self.action_dismiss_briefing()

    def compose(self):
        from parser import get_metrics, get_events
        from fiscal import get_fiscal_info
        from datetime import datetime

        metrics = get_metrics()
        today = date.today()
        fiscal = get_fiscal_info(today)
        fiscal_label = f"FY{fiscal['fy'] % 100} Q{fiscal['quarter']} P{fiscal['period']} W{fiscal['week']}"

        todays_events, reminders = [], []
        for e in get_events():
            try:
                edate = datetime.strptime(e.date, "%Y-%m-%d").date()
                days_away = (edate - today).days
                if days_away == 0:
                    todays_events.append(e)
                elif 0 < days_away <= e.remind_days:
                    reminders.append((days_away, e))
            except ValueError:
                pass

        width = _WIDTHS.get(STYLE, 70)
        sep = "─" * (width - 4)

        with Center():
            with Vertical(id="splash-outer", classes=STYLE):
                yield Static(_ARTS.get(STYLE, _ART_SLIM), id="ascii")
                yield Label(
                    f"[dim]{today.strftime('%A, %B %d %Y')}  ·  {fiscal_label}[/dim]",
                    id="splash-date",
                )

                yield Label(f"── Briefing {sep[:max(0,width-15)]}", classes="splash-section")

                if metrics["overdue"] > 0:
                    yield Label(f"[bold red]⚠  {metrics['overdue']} overdue task{'s' if metrics['overdue'] != 1 else ''}[/bold red]", classes="splash-bad")
                else:
                    yield Label("✓  No overdue tasks", classes="splash-good")

                if metrics["high_risks"] > 0:
                    yield Label(f"[bold red]⚠  {metrics['high_risks']} high severity risk{'s' if metrics['high_risks'] != 1 else ''}[/bold red]", classes="splash-bad")
                else:
                    yield Label("✓  No high severity risks", classes="splash-good")

                if metrics["oldest_task"] >= 14:
                    yield Label(f"[yellow]●  Oldest open task: {metrics['oldest_task']} days[/yellow]", classes="splash-warn")
                elif metrics["oldest_task"] > 0:
                    yield Label(f"●  Oldest open task: {metrics['oldest_task']} days", classes="splash-row")

                yield Label(
                    f"●  {metrics['tasks']} open task{'s' if metrics['tasks'] != 1 else ''}  ·  {metrics['month_wins']} win{'s' if metrics['month_wins'] != 1 else ''} this month",
                    classes="splash-row",
                )

                if todays_events:
                    yield Label(f"── Today's Events {sep[:max(0,width-20)]}", classes="splash-section")
                    for e in todays_events:
                        yield Label(f"📅  {e.title}  [{e.type}]  {e.location}", classes="splash-row")

                if reminders:
                    yield Label(f"── Upcoming {sep[:max(0,width-14)]}", classes="splash-section")
                    for days_away, e in sorted(reminders, key=lambda x: x[0]):
                        yield Label(f"🔔  {e.title} in {days_away}d  [{e.type}]", classes="splash-row")

                yield Label("[dim]press any key to close[/dim]", id="splash-hint")

    def action_dismiss_briefing(self):
        self.dismiss()
