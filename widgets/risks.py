from textual.widgets import DataTable
from rich.text import Text

from parser import get_risks

C_GOOD = "green"
C_WARN = "yellow"
C_BAD = "red"

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"

SEVERITY_COLORS = {"H": C_BAD, "M": C_WARN, "L": C_GOOD}
SEVERITY_LABELS = {"H": "● H", "M": "● M", "L": "● L"}


class RisksTable(DataTable):

    personal_filter = "all"

    def on_mount(self):

        self.zebra_stripes = True
        self.add_columns("Risk", "Owner", "Severity", "Since")
        self.load_risks()

    def load_risks(self):

        self.clear()

        for risk in get_risks():
            if self.personal_filter == "personal" and not risk.personal:
                continue
            if self.personal_filter == "work" and risk.personal:
                continue
            severity = risk.severity or ""
            color = SEVERITY_COLORS.get(severity, "default")
            label = SEVERITY_LABELS.get(severity, severity)
            desc = _t(risk.description) + (" ♦" if risk.personal else "")
            self.add_row(
                desc,
                _t(risk.owner),
                Text(label, style=f"bold {color}"),
                risk.since,
            )
