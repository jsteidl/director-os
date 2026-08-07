from textual.widgets import DataTable
from rich.text import Text

from parser import get_risks

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"

SEVERITY_COLORS = {"H": "red", "M": "yellow", "L": "green"}
SEVERITY_LABELS = {"H": "● H", "M": "● M", "L": "● L"}


class RisksTable(DataTable):

    def on_mount(self):

        self.zebra_stripes = True
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
            severity = risk.severity or ""
            color = SEVERITY_COLORS.get(severity, "white")
            label = SEVERITY_LABELS.get(severity, severity)
            severity_text = Text(label, style=f"bold {color}")
            self.add_row(
                _t(risk.description),
                _t(risk.owner),
                severity_text,
                risk.since,
            )
