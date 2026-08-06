from textual.widgets import DataTable

from parser import get_someday_items

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"


class SomedayTable(DataTable):

    def on_mount(self):

        self.zebra_stripes = True
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
                _t(item.item),
                _t(item.owner),
                item.since,
            )
