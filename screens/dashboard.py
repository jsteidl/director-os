from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual.widgets import Label

from widgets.metrics import MetricsWidget
from widgets.tasks import TaskTable
from widgets.dependencies import DependencyTable
from widgets.accomplishments_table import AccomplishmentTable
from widgets.risks import RisksTable
from widgets.someday import SomedayTable

from parser import (
    complete_task,
    add_task, edit_task, delete_task,
    add_dependency, edit_dependency, delete_dependency,
    reopen_task,
    add_daily_entry,
    resolve_dependency,
    add_risk, edit_risk, delete_risk, resolve_risk,
    add_someday_item, edit_someday_item, delete_someday_item, promote_someday_item,
    delete_accomplishment, edit_accomplishment,
)

from screens.task_complete import CompleteTaskScreen
from screens.add_task import AddTaskScreen
from screens.daily_checkin import DailyCheckinScreen
from screens.add_dependency import AddDependencyScreen
from screens.resolve_dependency import ResolveDependencyScreen
from screens.daily_log_viewer import DailyLogViewerScreen
from screens.daily_log_navigator import DailyLogNavigator
from screens.help import HelpScreen
from screens.reopen_task import ReopenTaskScreen
from screens.add_risk import AddRiskScreen
from screens.add_someday import AddSomedayScreen

class DashboardScreen(Screen):

    BINDINGS = [
        Binding("a", "add_task", "Add Task"),
        Binding("e", "edit_selected", "Edit"),
        Binding("d", "complete_task", "Done"),
        Binding("delete", "delete_selected", "Delete"),
        Binding("u", "reopen_task", "Reopen"),
        Binding("r", "refresh_data", "Refresh"),
        Binding("t", "daily_checkin", "Check-in"),
        Binding("w", "add_dependency", "Dependency"),
        Binding("x", "resolve_dependency", "Resolve"),
        Binding("i", "add_risk", "Risk"),
        Binding("s", "add_someday", "Someday"),
        Binding("p", "promote_someday", "Promote"),
        Binding("l", "show_daily_log", "Daily Log"),
        Binding("?", "show_help", "Help"),
    ]

    CSS = """
    DataTable {
        height: 1fr;
    }

    .widget-label {
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #metrics {
        height: 7;
        border: solid green;
    }

    #accomplishments {
        height: 12;
        border: solid green;
    }

    #risks {
        height: 12;
        border: solid red;
    }

    #someday {
        height: 12;
        border: solid yellow;
    }
    """

    def compose(self):

        yield Horizontal(

            Vertical(
                MetricsWidget(id="metrics"),
                Label("Tasks", classes="widget-label"),
                TaskTable(),
                Label("Someday / Future", classes="widget-label"),
                SomedayTable(id="someday"),
            ),

            Vertical(
                Label("Dependencies", classes="widget-label"),
                DependencyTable(),
                Label("Risks", classes="widget-label"),
                RisksTable(id="risks"),
                Label("Accomplishments", classes="widget-label"),
                AccomplishmentTable(id="accomplishments"),
            ),

        )

    # =====================================================
    # EDIT SELECTED
    # =====================================================

    def action_edit_selected(self):

        focused = self.focused

        if isinstance(focused, TaskTable):
            self._edit_task()
        elif isinstance(focused, DependencyTable):
            self._edit_dependency()
        elif isinstance(focused, RisksTable):
            self._edit_risk()
        elif isinstance(focused, SomedayTable):
            self._edit_someday()
        elif isinstance(focused, AccomplishmentTable):
            self._edit_accomplishment()

    def _edit_accomplishment(self):

        table = self.query_one(AccomplishmentTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            old_task = str(table.get_cell_at((row, 0)))
            outcome = str(table.get_cell_at((row, 1)))
        except Exception:
            return
        from screens.add_accomplishment import EditAccomplishmentScreen
        self.app.push_screen(
            EditAccomplishmentScreen(task=old_task, outcome=outcome),
            lambda result: self._edit_accomplishment_callback(old_task, result)
        )

    def _edit_accomplishment_callback(self, old_task, result):
        if not result:
            return
        new_task, outcome = result
        edit_accomplishment(old_task, new_task, outcome)
        self.refresh_data()

    def _edit_task(self):

        table = self.query_one(TaskTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            old_title = str(table.get_cell_at((row, 0)))
            priority = str(table.get_cell_at((row, 1)))
            due_date = str(table.get_cell_at((row, 2)))
        except Exception:
            return
        self.app.push_screen(
            AddTaskScreen(title=old_title, priority=priority, due_date=due_date),
            lambda result: self._edit_task_callback(old_title, result)
        )

    def _edit_task_callback(self, old_title, result):
        if not result:
            return
        new_title, priority, due_date, tag = result
        tags = [t.strip() for t in tag.split() if t.strip()] if tag else []
        edit_task(old_title, new_title, priority, due_date, tags)
        self.refresh_data()

    def _edit_dependency(self):

        table = self.query_one(DependencyTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            old_item = str(table.get_cell_at((row, 0)))
            owner = str(table.get_cell_at((row, 1)))
        except Exception:
            return
        self.app.push_screen(
            AddDependencyScreen(item=old_item, owner=owner),
            lambda result: self._edit_dependency_callback(old_item, result)
        )

    def _edit_dependency_callback(self, old_item, result):
        if not result:
            return
        new_item, owner = result
        edit_dependency(old_item, new_item, owner)
        self.refresh_data()

    def _edit_risk(self):

        table = self.query_one(RisksTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            old_desc = str(table.get_cell_at((row, 0)))
            owner = str(table.get_cell_at((row, 1)))
            severity = str(table.get_cell_at((row, 2)))
        except Exception:
            return
        self.app.push_screen(
            AddRiskScreen(description=old_desc, owner=owner, severity=severity),
            lambda result: self._edit_risk_callback(old_desc, result)
        )

    def _edit_risk_callback(self, old_desc, result):
        if not result:
            return
        description, owner, severity, tags = result
        edit_risk(old_desc, description, owner, severity, tags)
        self.refresh_data()

    def _edit_someday(self):

        table = self.query_one(SomedayTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            old_item = str(table.get_cell_at((row, 0)))
            owner = str(table.get_cell_at((row, 1)))
        except Exception:
            return
        self.app.push_screen(
            AddSomedayScreen(item=old_item, owner=owner),
            lambda result: self._edit_someday_callback(old_item, result)
        )

    def _edit_someday_callback(self, old_item, result):
        if not result:
            return
        new_item, owner, tags = result
        edit_someday_item(old_item, new_item, owner, tags)
        self.refresh_data()

    # =====================================================
    # DELETE SELECTED
    # =====================================================

    def action_delete_selected(self):

        focused = self.focused

        if isinstance(focused, TaskTable):
            self._delete_task()
        elif isinstance(focused, DependencyTable):
            self._delete_dependency()
        elif isinstance(focused, RisksTable):
            self._delete_risk()
        elif isinstance(focused, SomedayTable):
            self._delete_someday()
        elif isinstance(focused, AccomplishmentTable):
            self._delete_accomplishment()

    def _delete_task(self):
        table = self.query_one(TaskTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            title = str(table.get_cell_at((row, 0)))
        except Exception:
            return
        delete_task(title)
        self.refresh_data()

    def _delete_dependency(self):
        table = self.query_one(DependencyTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            item = str(table.get_cell_at((row, 0)))
        except Exception:
            return
        delete_dependency(item)
        self.refresh_data()

    def _delete_risk(self):
        table = self.query_one(RisksTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            desc = str(table.get_cell_at((row, 0)))
        except Exception:
            return
        delete_risk(desc)
        self.refresh_data()

    def _delete_someday(self):
        table = self.query_one(SomedayTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            item = str(table.get_cell_at((row, 0)))
        except Exception:
            return
        delete_someday_item(item)
        self.refresh_data()

    def _delete_accomplishment(self):
        table = self.query_one(AccomplishmentTable)
        row = table.cursor_row
        if row is None:
            return
        try:
            title = str(table.get_cell_at((row, 0)))
        except Exception:
            return
        delete_accomplishment(title)
        self.refresh_data()

    # =====================================================
    # HELP
    # =====================================================

    def action_show_help(self):

        self.app.push_screen(HelpScreen())

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

        risks = self.query_one(RisksTable)
        risks.load_risks()

        someday = self.query_one(SomedayTable)
        someday.load_items()

        accomplishments = self.query_one(AccomplishmentTable)

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

        task_name, priority, due_date, tag = result

        if not task_name:
            return

        add_task(
            task_name,
            tag,
            due_date,
            priority,
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

        except Exception:
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

        except Exception:
            return

        self.app.push_screen(
            ReopenTaskScreen(task_title),
            lambda confirmed: reopen_task(task_title) or self.refresh_data() if confirmed else None
        )

    # =====================================================
    # DAILY CHECKIN
    # =====================================================

    def action_daily_checkin(self):

        self.app.push_screen(
            DailyCheckinScreen(),
            self.daily_checkin_callback
        )

    def daily_checkin_callback(self, result):

        if not result:
            return

        add_daily_entry(
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
    # RISKS
    # =====================================================

    def action_add_risk(self):

        self.app.push_screen(
            AddRiskScreen(),
            self.add_risk_callback
        )

    def add_risk_callback(self, result):

        if not result:
            return

        description, owner, severity, tags = result

        if not description:
            return

        add_risk(description, owner, severity, tags)
        self.refresh_data()

    # =====================================================
    # SOMEDAY
    # =====================================================

    def action_add_someday(self):

        self.app.push_screen(
            AddSomedayScreen(),
            self.add_someday_callback
        )

    def add_someday_callback(self, result):

        if not result:
            return

        item, owner, tags = result

        if not item:
            return

        add_someday_item(item, owner, tags)
        self.refresh_data()

    def action_promote_someday(self):

        table = self.query_one(SomedayTable)
        row = table.cursor_row

        if row is None:
            return

        try:
            item_text = str(table.get_cell_at((row, 0)))
        except Exception:
            return

        promote_someday_item(item_text)
        self.refresh_data()

    # =====================================================
    # DAILY LOG VIEW
    # =====================================================

    def action_show_daily_log(self):

        self.app.push_screen(
            DailyLogNavigator()
        )