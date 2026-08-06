from datetime import date
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Vertical, Horizontal


class AddTaskScreen(ModalScreen[tuple]):

    def __init__(self, title="", priority="", due_date="", tags=None):
        super().__init__()
        self._title = title
        self._priority = priority
        self._due_date = due_date or date.today().isoformat()
        self._tags = " ".join(tags) if tags else ""

    def compose(self):

        yield Vertical(

            Label("Task"),

            Input(
                id="task",
                placeholder="Task name",
                value=self._title,
            ),

            Input(
                id="priority",
                placeholder="Priority (A, B, or C)",
                value=self._priority,
            ),

            Input(
                id="due_date",
                value=self._due_date,
            ),

            Input(
                id="tag",
                placeholder="Tags (optional)",
                value=self._tags,
            ),

            Horizontal(
                Button("Save", id="save", variant="primary"),
                Button("Cancel", id="cancel"),
            ),

        )

    def on_button_pressed(self, event):

        if event.button.id == "cancel":
            self.dismiss(None)
            return

        if event.button.id != "save":
            return

        task = self.query_one("#task", Input).value
        priority = self.query_one("#priority", Input).value.upper()
        due_date = self.query_one("#due_date", Input).value
        tag = self.query_one("#tag", Input).value

        self.dismiss((task, priority, due_date, tag))