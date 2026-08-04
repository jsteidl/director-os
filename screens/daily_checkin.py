from textual.screen import ModalScreen
from textual.widgets import Label, Input, Button, TextArea
from textual.containers import Vertical


class DailyCheckinScreen(ModalScreen[dict]):

    def compose(self):

        yield Vertical(

            Label("Priorities"),

            TextArea(
                id="priorities",
                placeholder="Today's priorities"
            ),

            Label("Accomplished"),

            TextArea(
                id="accomplished",
                placeholder="What did you accomplish?"
            ),

            Label("Blocked"),

            TextArea(
                id="blocked",
                placeholder="What is blocked?"
            ),

            Label("Notes"),

            TextArea(
                id="notes",
                placeholder="Additional notes"
            ),

            Button(
                "Save Check-In",
                id="save"
            ),
        )

    def on_button_pressed(self, event):

        print("BUTTON EVENT FIRED")

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

        print("ABOUT TO DISMISS")
        print(result)

        self.dismiss(result)