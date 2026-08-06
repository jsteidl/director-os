from textual.widgets import DataTable

from parser import get_accomplishments

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"


class AccomplishmentTable(
    DataTable
):

    def on_mount(self):

        self.zebra_stripes = True
        self.add_columns(
            "Task",
            "Outcome",
            "Completed",
        )

        self.load_data()

    def load_data(self):

        self.clear()

        for item in get_accomplishments():

            self.add_row(
                _t(item.task),
                _t(item.outcome),
                item.completed,
            )