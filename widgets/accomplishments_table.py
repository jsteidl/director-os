from textual.widgets import DataTable
from rich.text import Text

from parser import get_accomplishments

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"


class AccomplishmentTable(DataTable):

    personal_filter = "all"
    tag_filter = ""
    project_filter = ""

    def on_mount(self):

        self.zebra_stripes = True
        self.add_columns(
            "Task",
            "Outcome",
            "Completed",
            "Project",
            "Tags",
        )

        self.load_data()

    def load_data(self):

        self.clear()

        for item in get_accomplishments():
            if self.personal_filter == "personal" and not item.personal:
                continue
            if self.personal_filter == "work" and item.personal and not item.mgr:
                continue
            if self.tag_filter and self.tag_filter not in item.tags:
                continue
            if self.project_filter and item.project != self.project_filter:
                continue
            title = _t(item.task) + (" ★" if item.mgr else "") + (" ♦" if item.personal else "")
            self.add_row(
                title,
                _t(item.outcome),
                item.completed,
                f"+{item.project}" if item.project else "",
                " ".join(f"#{t}" for t in item.tags) if item.tags else "",
            )