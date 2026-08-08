from textual import on
from textual.screen import Screen
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import ListView, ListItem, Label, Markdown

from parser import get_all_daily_entries, edit_daily_entry
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
        self.entries = get_all_daily_entries()
        date_list = self.query_one("#dates", ListView)

        for entry in self.entries:
            label = entry.date
            if getattr(entry, "_readonly", False):
                label += " ◀"
            date_list.append(ListItem(Label(label)))

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
        readonly = getattr(entry, "_readonly", False)
        header = f"# {entry.date}" + (" _(read only)_" if readonly else "")

        markdown = f"""{header}

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
        if getattr(entry, "_readonly", False):
            return

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

        self.entries = get_all_daily_entries()
        self.show_entry(self.query_one("#dates", ListView).index)

    def render_list(self, items):
        if not items:
            return "_None_"
        return "\n".join(f"- {item}" for item in items)
