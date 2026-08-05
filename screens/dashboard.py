from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

from widgets.metrics import MetricsWidget
from widgets.tasks import TaskTable
from widgets.dependencies import DependencyTable
from widgets.accomplishments_table import (
    AccomplishmentTable,
)

from parser import (
    complete_task,
    add_task,
    add_dependency,
    reopen_task,
)

from screens.task_complete import (
    CompleteTaskScreen,
)

from screens.add_task import (
    AddTaskScreen,
)
from parser import add_daily_entry

from screens.daily_checkin import (
    DailyCheckinScreen
)

from screens.add_dependency import (
    AddDependencyScreen
)

from parser import resolve_dependency

from screens.resolve_dependency import (
    ResolveDependencyScreen
)

from screens.daily_log_viewer import (
    DailyLogViewerScreen
)
class DashboardScreen(Screen):

    BINDINGS = [
        Binding("a", "add_task", "Add"),
        Binding("d", "complete_task", "Done"),
        Binding("u", "reopen_task", "Undo"),
        Binding("r", "refresh_data", "Refresh"),
        Binding("t", "daily_checkin", "Check-in"),
        Binding("w", "add_dependency", "Dependency"),
        Binding("x", "resolve_dependency", "Resolve"),
        Binding("l", "show_daily_log", "Daily Log")
    ]

    CSS = """
    DataTable {
        height: 1fr;
    }

    #metrics {
        height: 7;
        border: solid green;
    }

    #accomplishments {
        height: 12;
        border: solid green;
    }
    """

    def compose(self):

        yield Horizontal(

            Vertical(
                MetricsWidget(
                    id="metrics"
                ),
                TaskTable(),
            ),

            Vertical(
                DependencyTable(),
                AccomplishmentTable(
                    id="accomplishments"
                ),
            ),

        )

    # =====================================================
    # REFRESH
    # =====================================================

    def action_refresh_data(self):
        self.refresh_data()

    def refresh_data(self):

        metrics = self.query_one(
            MetricsWidget
        )

        metrics.update_metrics()

        tasks = self.query_one(
            TaskTable
        )

        tasks.load_tasks()

        deps = self.query_one(
            DependencyTable
        )

        deps.load_dependencies()

        accomplishments = self.query_one(
            AccomplishmentTable
        )

        accomplishments.load_data()

        self.refresh()

    # =====================================================
    # ADD TASK
    # =====================================================

    def action_add_task(self):

        self.app.push_screen(
            AddTaskScreen(),
            self.add_task_callback
        )

    def add_task_callback(
        self,
        result
    ):

        if not result:
            return

        task_name, tag = result

        if not task_name:
            return

        add_task(
            task_name,
            tag
        )

        self.refresh_data()

    # =====================================================
    # COMPLETE TASK
    # =====================================================

    def action_complete_task(self):

        table = self.query_one(
            TaskTable
        )

        row = table.cursor_row

        if row is None:
            return

        try:

            task_text = str(
                table.get_cell_at(
                    (row, 0)
                )
            )

        except Exception as ex:

            print(
                f"Task selection error: {ex}"
            )

            return

        self.app.push_screen(

            CompleteTaskScreen(
                task_text
            ),

            lambda outcome:
                self.complete_task_callback(
                    task_text,
                    outcome
                )

        )

    def complete_task_callback(
        self,
        task_text,
        outcome
    ):

        complete_task(
            task_text,
            outcome or task_text
        )

        self.refresh_data()

    # =====================================================
    # REOPEN TASK
    # =====================================================

    def action_reopen_task(self):

        table = self.query_one(
            AccomplishmentTable
        )

        row = table.cursor_row

        if row is None:
            return

        try:

            task_title = str(
                table.get_cell_at(
                    (row, 0)
                )
            )

        except Exception as ex:

            print(
                f"Accomplishment selection error: {ex}"
            )

            return

        reopen_task(
            task_title
        )

        self.refresh_data()

    # =====================================================
    # REOPEN TASK
    # =====================================================
    def action_daily_checkin(self):

        self.app.push_screen(
            DailyCheckinScreen(),
            self.daily_checkin_callback
        )
    # =====================================================
    # DAILY CHECKIN
    # =====================================================

    def daily_checkin_callback(
    self,
    result
    ):

        if not result:
            return

        success = add_daily_entry(
            result["priorities"],
            result["accomplished"],
            result["blocked"],
            result["notes"],
        )

        self.refresh_data()
        
    # =====================================================
    # DEPENDENCY
    # =====================================================
    def action_add_dependency(self):

        self.app.push_screen(
            AddDependencyScreen(),
            self.add_dependency_callback
        )


    def add_dependency_callback(
        self,
        result
    ):

        if not result:
            return

        dependency, owner = result

        if not dependency:
            return

        add_dependency(
            dependency,
            owner
        )

        self.refresh_data()

    def action_resolve_dependency(self):

        table = self.query_one(
            DependencyTable
        )

        row = table.cursor_row

        if row is None:
            return

        dependency_name = str(
            table.get_cell_at(
                (row, 0)
            )
        )

        self.app.push_screen(
            ResolveDependencyScreen(),
            lambda notes:
                self.resolve_dependency_callback(
                    dependency_name,
                    notes
                )
        )
    def resolve_dependency_callback(
        self,
        dependency_name,
        notes,
    ):

        resolve_dependency(
            dependency_name,
            notes or "",
        )

        self.refresh_data()
# =====================================================
# DAILY LOG VIEW
# =====================================================
    def action_show_daily_log(
        self
    ):

        self.app.push_screen(
            DailyLogViewerScreen()
        )