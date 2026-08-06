from textual.widgets import DataTable

from parser import get_accomplishments


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
                item.task,
                item.outcome,
                item.completed,
            )