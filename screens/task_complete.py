from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.containers import Vertical


class CompleteTaskScreen(ModalScreen[str]):

    def __init__(self, task_name: str):
        super().__init__()

        self.task_name = task_name

    def compose(self):

        yield Vertical(

            Label(
                f"""
Complete Task

Task:
{self.task_name}

Describe the business outcome:
"""
            ),

            Input(
                placeholder=(
                    "Example: Implemented Snowflake MFA "
                    "enforcement strategy and rollout plan"
                )
            )

        )

    def on_input_submitted(self, event):
        self.dismiss(event.value)