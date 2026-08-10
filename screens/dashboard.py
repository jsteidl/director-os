import subprocess
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual.widgets import Label
from datetime import datetime
from quotes import get_random_quote

from widgets.metrics import MetricsWidget
from widgets.tasks import TaskTable
from widgets.dependencies import DependencyTable
from widgets.accomplishments_table import AccomplishmentTable
from widgets.risks import RisksTable
from widgets.someday import SomedayTable
from widgets.today import TodayWidget

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
from screens.confirm import ConfirmScreen
from screens.widget_viewer import WidgetViewerScreen
from screens.weekly_review import WeeklyReviewScreen
from screens.tag_manager import TagManagerScreen

class DashboardScreen(Screen):

    BINDINGS = [
        Binding("a", "add_task", "Add Task"),
        Binding("e", "edit_selected", "Edit"),
        Binding("d", "complete_task", "Done"),
        Binding("delete", "delete_selected", "Delete"),
        Binding("u", "reopen_task", "Reopen"),
        Binding("r", "refresh_data", "Refresh"),
        Binding("t", "tag_manager", "Tags"),
        Binding("!", "daily_checkin", "Check-in"),
        Binding("w", "add_dependency", "Dependency"),
        Binding("x", "resolve_dependency", "Resolve"),
        Binding("i", "add_risk", "Risk"),
        Binding("s", "add_someday", "Someday"),
        Binding("p", "promote_someday", "Promote"),
        Binding("S", "demote_task", "Move to Someday"),
        Binding("l", "show_daily_log", "Daily Log"),
        Binding("W", "weekly_review", "Weekly Review"),
        Binding("c", "calendar", "Calendar"),
        Binding("E", "events", "Events"),
        Binding("v", "view_widget", "View"),
        Binding("m", "toggle_mgr", "Mgr flag"),
        Binding("U", "manager_update", "Update"),
        Binding("g", "sync_logs", "Sync Logs"),
        Binding("C", "config", "Config"),
        Binding("?", "show_help", "Help"),
    ]

    CSS = """
    #app-footer {
        dock: bottom;
        height: 1;
        width: 100%;
        padding: 0 1;
        background: $accent;
        color: $text;
        layout: horizontal;
    }

    #app-quote {
        width: 1fr;
        color: $text;
        background: $accent;
    }

    #app-clock {
        width: auto;
        color: $text;
        background: $accent;
        text-align: right;
    }

    #app-title {
        dock: top;
        height: 1;
        width: 100%;
        padding: 0 1;
        background: $accent;
        color: $text;
        text-style: bold;
        text-align: center;
    }

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
        height: 3;
        border: solid green;
        padding: 0 1;
    }

    #tasks {
        height: 1fr;
        border: solid green;
    }

    #today {
        height: 12;
        border: solid cyan;
        padding: 0 1;
    }

    #dependencies {
        height: 1fr;
        border: solid green;
    }

    #risks {
        height: 1fr;
        border: solid red;
    }

    #someday {
        height: 1fr;
        border: solid yellow;
    }

    #accomplishments {
        height: 1fr;
        border: solid green;
    }
    """

    def compose(self):

        yield Label("director_os", id="app-title")
        yield Horizontal(
            Label("", id="app-quote"),
            Label("", id="app-clock"),
            id="app-footer"
        )
        yield Horizontal(

            Vertical(
                Label("Executive Summary", classes="widget-label"),
                MetricsWidget(id="metrics"),
                Label("Tasks", classes="widget-label"),
                TaskTable(id="tasks"),
                Label("Today", classes="widget-label"),
                TodayWidget(id="today"),
            ),

            Vertical(
                Label("Dependencies", classes="widget-label"),
                DependencyTable(id="dependencies"),
                Label("Risks", classes="widget-label"),
                RisksTable(id="risks"),
                Label("Someday / Future", classes="widget-label"),
                SomedayTable(id="someday"),
                Label("Accomplishments", classes="widget-label"),
                AccomplishmentTable(id="accomplishments"),
            ),

        )

    def on_mount(self):
        self._quote = get_random_quote()
        self.set_interval(1, self._tick_clock)
        from parser import check_event_notifications
        check_event_notifications()

    def _tick_clock(self):
        clock = datetime.now().strftime("%A, %B %d  %I:%M %p")
        self.query_one("#app-quote", Label).update(self._quote)
        self.query_one("#app-clock", Label).update(clock)

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
        from parser import get_accomplishments
        accomplishments = get_accomplishments()
        if row >= len(accomplishments):
            return
        acc = accomplishments[row]
        from screens.add_accomplishment import EditAccomplishmentScreen
        self.app.push_screen(
            EditAccomplishmentScreen(task=acc.task, outcome=acc.outcome),
            lambda result: self._edit_accomplishment_callback(acc.task, result)
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
        from parser import get_tasks
        tasks = get_tasks()
        if row >= len(tasks):
            return
        task = tasks[row]
        self.app.push_screen(
            AddTaskScreen(title=task.title, priority=task.priority or "", due_date=task.due_date or "", tags=task.tags),
            lambda result: self._edit_task_callback(task.title, result)
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
        from parser import get_dependencies
        deps = get_dependencies()
        if row >= len(deps):
            return
        dep = deps[row]
        self.app.push_screen(
            AddDependencyScreen(item=dep.item, owner=dep.owner),
            lambda result: self._edit_dependency_callback(dep.item, result)
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
        from parser import get_risks
        risks = get_risks()
        if row >= len(risks):
            return
        risk = risks[row]
        self.app.push_screen(
            AddRiskScreen(description=risk.description, owner=risk.owner, severity=risk.severity),
            lambda result: self._edit_risk_callback(risk.description, result)
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
        from parser import get_someday_items
        items = get_someday_items()
        if row >= len(items):
            return
        item = items[row]
        self.app.push_screen(
            AddSomedayScreen(item=item.item, owner=item.owner),
            lambda result: self._edit_someday_callback(item.item, result)
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
            self._confirm_delete(self._delete_task)
        elif isinstance(focused, DependencyTable):
            self._confirm_delete(self._delete_dependency)
        elif isinstance(focused, RisksTable):
            self._confirm_delete(self._delete_risk)
        elif isinstance(focused, SomedayTable):
            self._confirm_delete(self._delete_someday)
        elif isinstance(focused, AccomplishmentTable):
            self._confirm_delete(self._delete_accomplishment)

    def _confirm_delete(self, delete_fn):
        self.app.push_screen(
            ConfirmScreen("Delete this item? This cannot be undone."),
            lambda confirmed: delete_fn() if confirmed else None
        )

    def _delete_task(self):
        table = self.query_one(TaskTable)
        row = table.cursor_row
        if row is None:
            return
        from parser import get_tasks
        tasks = get_tasks()
        if row >= len(tasks):
            return
        delete_task(tasks[row].title)
        self.refresh_data()

    def _delete_dependency(self):
        table = self.query_one(DependencyTable)
        row = table.cursor_row
        if row is None:
            return
        from parser import get_dependencies
        deps = get_dependencies()
        if row >= len(deps):
            return
        delete_dependency(deps[row].item)
        self.refresh_data()

    def _delete_risk(self):
        table = self.query_one(RisksTable)
        row = table.cursor_row
        if row is None:
            return
        from parser import get_risks
        risks = get_risks()
        if row >= len(risks):
            return
        delete_risk(risks[row].description)
        self.refresh_data()

    def _delete_someday(self):
        table = self.query_one(SomedayTable)
        row = table.cursor_row
        if row is None:
            return
        from parser import get_someday_items
        items = get_someday_items()
        if row >= len(items):
            return
        delete_someday_item(items[row].item)
        self.refresh_data()

    def _delete_accomplishment(self):
        table = self.query_one(AccomplishmentTable)
        row = table.cursor_row
        if row is None:
            return
        from parser import get_accomplishments
        accomplishments = get_accomplishments()
        if row >= len(accomplishments):
            return
        delete_accomplishment(accomplishments[row].task)
        self.refresh_data()

    # =====================================================
    # VIEW WIDGET
    # =====================================================

    def action_view_widget(self):

        focused = self.focused
        p = __import__('parser')

        if isinstance(focused, TaskTable):
            rows = [(t.title, t.priority or "", t.due_date or "", " ".join(f"#{tag}" for tag in t.tags)) for t in p.get_tasks()]
            self.app.push_screen(WidgetViewerScreen("Tasks", ["Task", "Priority", "Due", "Tags"], rows))
        elif isinstance(focused, DependencyTable):
            rows = [(d.item + (" " + " ".join(f"#{tag}" for tag in d.tags) if d.tags else ""), d.owner, f"{d.age}d") for d in p.get_dependencies()]
            self.app.push_screen(WidgetViewerScreen("Dependencies", ["Dependency", "Owner", "Age"], rows))
        elif isinstance(focused, RisksTable):
            rows = [(r.description + (" " + " ".join(f"#{tag}" for tag in r.tags) if r.tags else ""), r.owner, r.severity, r.since) for r in p.get_risks()]
            self.app.push_screen(WidgetViewerScreen("Risks", ["Risk", "Owner", "Severity", "Since"], rows))
        elif isinstance(focused, SomedayTable):
            rows = [(s.item + (" " + " ".join(f"#{tag}" for tag in s.tags) if s.tags else ""), s.owner, s.since) for s in p.get_someday_items()]
            self.app.push_screen(WidgetViewerScreen("Someday / Future", ["Item", "Owner", "Since"], rows))
        elif isinstance(focused, AccomplishmentTable):
            rows = [(a.task + (" " + " ".join(f"#{tag}" for tag in a.tags) if a.tags else ""), a.outcome, a.completed) for a in p.get_accomplishments()]
            self.app.push_screen(WidgetViewerScreen("Accomplishments", ["Task", "Outcome", "Completed"], rows))

    def action_tag_manager(self):
        self.app.push_screen(
            TagManagerScreen(),
            lambda saved: self.refresh_data() if saved else None
        )

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

        tasks = self.query_one(TaskTable)
        tasks.load_tasks()

        deps = self.query_one(
            DependencyTable
        )

        deps.load_dependencies()

        today = self.query_one(TodayWidget)
        today.load_today()

        risks = self.query_one(RisksTable)
        risks.load_risks()

        someday = self.query_one(SomedayTable)
        someday.load_items()

        accomplishments = self.query_one(AccomplishmentTable)

        accomplishments.load_data()

        self._quote = get_random_quote()
        self.query_one("#app-quote", Label).update(self._quote)
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

    def complete_task_callback(self, task_text, outcome):
        if outcome is None:
            return
        complete_task(task_text, outcome or task_text)
        self.refresh_data()
        self.app.notify("Task completed ✓", severity="information")

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

        from parser import get_today_entry
        entry = get_today_entry()

        if entry:
            screen = DailyCheckinScreen(
                priorities="\n".join(entry.priorities),
                accomplished="\n".join(entry.accomplished),
                blocked="\n".join(entry.blocked),
                notes="\n".join(entry.notes),
            )
        else:
            screen = DailyCheckinScreen()

        self.app.push_screen(screen, self.daily_checkin_callback)

    def daily_checkin_callback(self, result):

        if not result:
            return

        from parser import get_today_entry, edit_daily_entry
        from datetime import date

        if get_today_entry():
            edit_daily_entry(
                date.today().isoformat(),
                result["priorities"],
                result["accomplished"],
                result["blocked"],
                result["notes"],
            )
        else:
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
        if notes is None:
            return

        resolve_dependency(
            dependency_name,
            notes or "",
        )

        self.refresh_data()
        self.app.notify("Dependency resolved ✓", severity="information")

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

        from parser import get_someday_items
        items = get_someday_items()
        if row >= len(items):
            return
        item = items[row]

        self.app.push_screen(
            AddTaskScreen(title=item.item),
            lambda result: self._promote_someday_callback(item.item, result)
        )

    def _promote_someday_callback(self, item_text, result):
        if not result:
            return
        new_title, priority, due_date, tag = result
        tags = [t.strip() for t in tag.split() if t.strip()] if tag else []
        promote_someday_item(item_text, priority, due_date, tags)
        self.refresh_data()
        self.app.notify("Promoted to tasks ✓", severity="information")

    def action_demote_task(self):

        focused = self.focused
        if not isinstance(focused, TaskTable):
            return

        row = focused.cursor_row
        if row is None:
            return

        from parser import get_tasks
        tasks = get_tasks()
        if row >= len(tasks):
            return
        task = tasks[row]

        self.app.push_screen(
            AddSomedayScreen(item=task.title),
            lambda result: self._demote_task_callback(task.title, result)
        )

    def _demote_task_callback(self, task_title, result):
        if not result:
            return
        item, owner, tags = result
        delete_task(task_title)
        add_someday_item(item, owner, tags)
        self.refresh_data()
        self.app.notify("Moved to Someday ✓", severity="information")

    def action_toggle_mgr(self):
        from parser import get_tasks, get_accomplishments, toggle_mgr_task, toggle_mgr_accomplishment
        focused = self.focused
        if isinstance(focused, TaskTable):
            row = focused.cursor_row
            if row is None:
                return
            tasks = get_tasks()
            if row >= len(tasks):
                return
            toggle_mgr_task(tasks[row].title)
            self.refresh_data()
        elif isinstance(focused, AccomplishmentTable):
            row = focused.cursor_row
            if row is None:
                return
            accomplishments = get_accomplishments()
            if row >= len(accomplishments):
                return
            toggle_mgr_accomplishment(accomplishments[row].task)
            self.refresh_data()

    def action_manager_update(self):
        from screens.update import UpdateScreen
        self.app.push_screen(
            UpdateScreen(),
            lambda path: self.app.notify(f"Saved to {path}", severity="information") if path else None
        )

    def action_weekly_review(self):
        self.app.push_screen(WeeklyReviewScreen())

    def action_events(self):
        from screens.events import EventsScreen
        self.app.push_screen(EventsScreen())

    def action_calendar(self):
        from screens.calendar import CalendarScreen
        self.app.push_screen(CalendarScreen())

    # =====================================================
    # DAILY LOG VIEW
    # =====================================================

    def action_show_daily_log(self):

        self.app.push_screen(
            DailyLogNavigator()
        )

    # =====================================================
    # SYNC LOGS
    # =====================================================

    def action_config(self):
        from screens.config import ConfigScreen
        self.app.push_screen(ConfigScreen())

    def action_sync_logs(self):
        from parser import _get_logs_path
        logs_path = str(_get_logs_path())
        try:
            r = subprocess.run(["git", "-C", logs_path, "add", "-A"], capture_output=True, text=True)
            if r.returncode != 0:
                self.app.notify(f"Sync failed: {r.stderr.strip()}", severity="error")
                return
            r = subprocess.run(["git", "-C", logs_path, "commit", "-m", "sync"], capture_output=True, text=True)
            if r.returncode != 0 and "nothing to commit" not in r.stdout:
                self.app.notify(f"Sync failed: {r.stderr.strip()}", severity="error")
                return
            r = subprocess.run(["git", "-C", logs_path, "push"], capture_output=True, text=True)
            if r.returncode != 0:
                self.app.notify(f"Push failed: {r.stderr.strip()}", severity="error")
                return
            self.app.notify("Logs synced ✓", severity="information")
        except Exception as e:
            self.app.notify(f"Sync error: {e}", severity="error")