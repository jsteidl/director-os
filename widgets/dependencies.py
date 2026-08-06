from textual.widgets import DataTable
from rich.text import Text

from parser import get_dependencies

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"

def _age_color(age):
    if age >= 14:
        return "red"
    if age >= 7:
        return "yellow"
    return "white"


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
            color = _age_color(dep.age)
            self.add_row(
                Text(_t(dep.item), style=color),
                Text(_t(dep.owner), style=color),
                Text(f"{dep.age}d", style=color),
            )