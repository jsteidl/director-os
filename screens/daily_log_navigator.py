from textual import on
from textual.screen import Screen
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import (
    ListView,
    ListItem,
    Label,
    Markdown,
)

from parser import (
    load_log,
    parse_daily_log,
)


class DailyLogNavigator(Screen):

    CSS = """
    #dates {
        width: 20;
        border-right: solid $primary;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
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
            date_list.append(
                ListItem(
                    Label(entry.date)
                )
            )

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

        details = self.query_one(
            "#details",
            Markdown,
        )

        details.update(markdown)

    def render_list(self, items):

        if not items:
            return "_None_"

        return "\n".join(
            f"- {item}"
            for item in items
        )