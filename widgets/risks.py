from textual.widgets import DataTable
from rich.text import Text

from parser import get_risks

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"

SEVERITY_COLORS = {"H": "red", "M": "yellow", "L": "green"}
SEVERITY_LABELS = {"H": "● H", "M": "● M", "L": "● L"}


class RisksTable(DataTable):

    personal_filter = "all"

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
            if self.personal_filter == "personal" and not risk.personal:
                continue
            if self.personal_filter == "work" and risk.personal:
                continue
            severity = risk.severity or ""
            color = SEVERITY_COLORS.get(severity, "white")
            label = SEVERITY_LABELS.get(severity, severity)
            severity_text = Text(label, style=f"bold {color}")
            desc = _t(risk.description) + (" ♦" if risk.personal else "")
            self.add_row(
                desc,
                _t(risk.owner),
                severity_text,
                risk.since,
            )
