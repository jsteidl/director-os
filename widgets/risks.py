from textual.widgets import DataTable

from parser import get_risks


class RisksTable(DataTable):

    def on_mount(self):

        self.add_columns(
            "Risk",
            "Owner",
            "Severity",
            "Since",
        )

        self.load_risks()

    def load_risks(self):

        self.clear()

        for risk in get_risks():

            self.add_row(
                risk.description,
                risk.owner,
                risk.severity,
                risk.since,
            )
