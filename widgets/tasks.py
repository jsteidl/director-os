from textual.widgets import DataTable

from parser import get_tasks


class TaskTable(DataTable):

    def on_mount(self):

        self.add_columns(
            "Task",
            "Priority",
            "Due",
        )

        self.load_tasks()

    def load_tasks(self):

        self.clear()

        for task in get_tasks():

            self.add_row(
                task.title,
                task.priority or "",
                task.due_date or "",
            )