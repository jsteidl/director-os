from textual.widgets import DataTable
from rich.text import Text

from parser import get_risks

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"

SEVERITY_COLORS = {
    "high": "red",
    "medium": "yellow",
    "low": "green",
}


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
            color = SEVERITY_COLORS.get(severity.lower(), "white")
            severity_text = Text(severity, style=color)
            self.add_row(
                _t(risk.description),
                _t(risk.owner),
                severity_text,
                risk.since,
            )
