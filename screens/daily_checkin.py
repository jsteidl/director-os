from textual.screen import ModalScreen
from textual.widgets import Label, Input, Button, TextArea
from textual.containers import Vertical


class DailyCheckinScreen(ModalScreen[dict]):

    def __init__(self, priorities="", accomplished="", blocked="", notes=""):
        super().__init__()
        self._priorities = priorities
        self._accomplished = accomplished
        self._blocked = blocked
        self._notes = notes

    def compose(self):

        yield Vertical(

            Label("Priorities"),

            TextArea(
                self._priorities,
                id="priorities",
            ),

            Label("Accomplished"),

            TextArea(
                self._accomplished,
                id="accomplished",
            ),

            Label("Blocked"),

            TextArea(
                self._blocked,
                id="blocked",
            ),

            Label("Notes"),

            TextArea(
                self._notes,
                id="notes",
            ),

            Button(
                "Save",
                id="save"
            ),
        )

    def on_button_pressed(self, event):

        if event.button.id != "save":
            return

        result = {
            "priorities": self.query_one(
                "#priorities",
                TextArea
            ).text,

            "accomplished": self.query_one(
                "#accomplished",
                TextArea
            ).text,

            "blocked": self.query_one(
                "#blocked",
                TextArea
            ).text,

            "notes": self.query_one(
                "#notes",
                TextArea
            ).text,
        }

        self.dismiss(result)