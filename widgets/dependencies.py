from textual.widgets import DataTable

from parser import get_dependencies

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"


class DependencyTable(DataTable):

    def on_mount(self):

        self.zebra_stripes = True
        self.add_columns(
            "Dependency",
            "Owner",
            "Age",
        )

        self.load_dependencies()

    def load_dependencies(self):

        self.clear()

        for dep in get_dependencies():
            self.add_row(
                _t(dep.item),
                _t(dep.owner),
                f"{dep.age}d",
            )