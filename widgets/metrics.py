from textual.widgets import Static

from parser import get_tasks
from parser import get_dependencies
from parser import get_accomplishments


class MetricsWidget(Static):

    def update_metrics(self):

        tasks = len(get_tasks())
        deps = len(get_dependencies())
        accomplishments = len(
            get_accomplishments()
        )

        self.update(
            f"""
Tasks: {tasks}

Dependencies: {deps}

Accomplishments: {accomplishments}
"""
        )

    def on_mount(self):
        self.update_metrics()