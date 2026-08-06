from textual.widgets import DataTable

from parser import get_tasks

def _t(text, n=50):
    return text if len(text) <= n else text[:n - 1] + "…"


class TaskTable(DataTable):

    def on_mount(self):

        self.zebra_stripes = True
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
                _t(task.title),
                task.priority or "",
                task.due_date or "",
            )