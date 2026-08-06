from textual import on
from textual.screen import Screen
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import ListView, ListItem, Label, Markdown

from parser import load_log, parse_daily_log, edit_daily_entry
from screens.daily_checkin import DailyCheckinScreen


class DailyLogNavigator(Screen):

    CSS = """
    #dates {
        width: 20;
        border-right: solid $primary;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("e", "edit_entry", "Edit"),
    ]

    def compose(self):
        yield Horizontal(
            ListView(id="dates"),
            VerticalScroll(
                Markdown("", id="details")
            ),
        )

    def on_mount(self):

        content = load_log()
        self.entries = parse_daily_log(content)
        date_list = self.query_one("#dates", ListView)

        for entry in self.entries:
            date_list.append(ListItem(Label(entry.date)))

        if self.entries:
            date_list.index = 0
            self.show_entry(0)

    @on(ListView.Highlighted)
    def date_highlighted(self, event):

        index = event.list_view.index

        if index is None:
            return

        self.show_entry(index)

    def show_entry(self, index):

        entry = self.entries[index]

        markdown = f"""
# {entry.date}

## Priorities

{self.render_list(entry.priorities)}

## Accomplished

{self.render_list(entry.accomplished)}

## Blocked

{self.render_list(entry.blocked)}

## Notes

{self.render_list(entry.notes)}
"""

        self.query_one("#details", Markdown).update(markdown)

    def action_edit_entry(self):

        index = self.query_one("#dates", ListView).index

        if index is None or index >= len(self.entries):
            return

        entry = self.entries[index]

        self.app.push_screen(
            DailyCheckinScreen(
                priorities="\n".join(entry.priorities),
                accomplished="\n".join(entry.accomplished),
                blocked="\n".join(entry.blocked),
                notes="\n".join(entry.notes),
            ),
            lambda result: self.edit_entry_callback(entry.date, result)
        )

    def edit_entry_callback(self, entry_date, result):

        if not result:
            return

        edit_daily_entry(
            entry_date,
            result["priorities"],
            result["accomplished"],
            result["blocked"],
            result["notes"],
        )

        content = load_log()
        self.entries = parse_daily_log(content)
        self.show_entry(self.query_one("#dates", ListView).index)

    def render_list(self, items):

        if not items:
            return "_None_"

        return "\n".join(f"- {item}" for item in items)