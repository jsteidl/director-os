from textual.widgets import DataTable

from parser import get_someday_items

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"


class SomedayTable(DataTable):

    personal_filter = "all"

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
            if self.personal_filter == "personal" and not item.personal:
                continue
            if self.personal_filter == "work" and item.personal:
                continue
            self.add_row(
                _t(item.item) + (" ♦" if item.personal else ""),
                _t(item.owner),
                item.since,
            )
