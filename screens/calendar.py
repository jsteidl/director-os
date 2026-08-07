from datetime import date, timedelta
import calendar

from textual.screen import ModalScreen
from textual.widgets import Static, Label
from textual.containers import Vertical
from textual.binding import Binding
from rich.text import Text
from rich.table import Table

from parser import get_tasks, parse_daily_log, load_log
from fiscal import get_fiscal_info, get_period_weeks, period_label


def _due_dates() -> set[date]:
    result = set()
    for t in get_tasks():
        if t.due_date:
            try:
                result.add(date.fromisoformat(t.due_date))
            except ValueError:
                pass
    return result


def _checkin_dates() -> set[date]:
    entries = parse_daily_log(load_log())
    result = set()
    for e in entries:
        try:
            result.add(date.fromisoformat(e.date))
        except ValueError:
            pass
    return result


def _event_dates() -> set[date]:
    from parser import get_events
    result = set()
    for e in get_events():
        try:
            result.add(date.fromisoformat(e.date))
        except ValueError:
            pass
    return result


def _day_marker(d: date, due: set, checkins: set, events: set, today: date) -> Text:
    is_today = d == today
    style = "bold reverse" if is_today else ""
    t = Text(f"{d.day:2d}", style=style)
    if d in due and d in checkins:
        t.append("◆", style="bold magenta")
    elif d in due:
        t.append("●", style="bold yellow")
    elif d in checkins:
        t.append("✓", style="bold green")
    elif d in events:
        t.append("★", style="bold cyan")
    else:
        t.append(" ")
    return t


class CalendarScreen(ModalScreen):

    BINDINGS = [
        Binding("left", "prev", "Previous"),
        Binding("right", "next", "Next"),
        Binding("f", "toggle_mode", "Toggle Fiscal/Gregorian"),
        Binding("escape", "dismiss", "Close"),
    ]

    CSS = """
    CalendarScreen {
        align: center middle;
        background: $background 60%;
    }
    #cal-container {
        width: 64;
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    #cal-header {
        text-align: center;
        text-style: bold;
        height: 1;
        margin-bottom: 1;
    }
    #cal-body {
        height: auto;
    }
    #cal-legend {
        height: 1;
        margin-top: 1;
    }
    #cal-mode {
        height: 1;
        text-align: center;
    }
    """

    def __init__(self):
        super().__init__()
        self._today = date.today()
        self._fiscal_mode = False
        self._greg_year = self._today.year
        self._greg_month = self._today.month
        info = get_fiscal_info(self._today)
        self._fy = info["fy"]
        self._period = info["period"]

    def compose(self):
        yield Vertical(
            Label("", id="cal-header"),
            Static("", id="cal-body"),
            Label("● due  ✓ check-in  ★ event  ◆ both  [reverse] today [/]", id="cal-legend"),
            Label("f = toggle fiscal/gregorian  ← → navigate  esc = close", id="cal-mode"),
            id="cal-container",
        )

    def on_mount(self):
        self._draw()

    def _draw(self):
        due = _due_dates()
        checkins = _checkin_dates()
        events = _event_dates()
        if self._fiscal_mode:
            self._draw_fiscal(due, checkins, events)
        else:
            self._draw_gregorian(due, checkins, events)

    def _draw_gregorian(self, due, checkins, events):
        month_name = date(self._greg_year, self._greg_month, 1).strftime("%B %Y")
        self.query_one("#cal-header", Label).update(f"[bold]{month_name}[/bold]")

        table = Table(box=None, padding=(0, 1), show_header=True, header_style="bold")
        for day in ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]:
            table.add_column(day, width=4, justify="right")

        cal = calendar.Calendar(firstweekday=6)
        for week in cal.monthdayscalendar(self._greg_year, self._greg_month):
            # firstweekday=6 means Sun=0..Sat=6, no shifting needed
            row = []
            for day_num in week:
                if day_num == 0:
                    row.append(Text("   "))
                else:
                    row.append(_day_marker(date(self._greg_year, self._greg_month, day_num), due, checkins, events, self._today))
            table.add_row(*row)

        self.query_one("#cal-body", Static).update(table)

    def _draw_fiscal(self, due, checkins, events):
        self.query_one("#cal-header", Label).update(f"[bold]{period_label(self._fy, self._period)}[/bold]")

        table = Table(box=None, padding=(0, 1), show_header=True, header_style="bold")
        for day in ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]:
            table.add_column(day, width=4, justify="right")

        for week in get_period_weeks(self._fy, self._period):
            table.add_row(*[_day_marker(d, due, checkins, events, self._today) for d in week])

        self.query_one("#cal-body", Static).update(table)

    def action_prev(self):
        if self._fiscal_mode:
            self._period -= 1
            if self._period < 1:
                self._fy -= 1
                self._period = 12
        else:
            self._greg_month -= 1
            if self._greg_month < 1:
                self._greg_month = 12
                self._greg_year -= 1
        self._draw()

    def action_next(self):
        if self._fiscal_mode:
            self._period += 1
            if self._period > 12:
                self._fy += 1
                self._period = 1
        else:
            self._greg_month += 1
            if self._greg_month > 12:
                self._greg_month = 1
                self._greg_year += 1
        self._draw()

    def action_toggle_mode(self):
        self._fiscal_mode = not self._fiscal_mode
        self._draw()
