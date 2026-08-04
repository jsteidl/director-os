from textual.widgets import DataTable

from parser import get_dependencies


class DependencyTable(DataTable):

    def on_mount(self):

        self.add_columns(
            "Dependency",
            "Owner",
            "Since",
        )

        self.load_dependencies()

    def load_dependencies(self):

        self.clear()

        for dep in get_dependencies():

            self.add_row(
                dep.item,
                dep.owner,
                dep.since,
            )