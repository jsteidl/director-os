from textual.widgets import DataTable

from parser import get_someday_items


class SomedayTable(DataTable):

    def on_mount(self):

        self.add_columns(
            "Item",
            "Owner",
            "Since",
        )

        self.load_items()

    def load_items(self):

        self.clear()

        for item in get_someday_items():

            self.add_row(
                item.item,
                item.owner,
                item.since,
            )
