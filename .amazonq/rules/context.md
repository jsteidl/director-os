# director_os — AI Context File

This file provides full context for AI-assisted development on director_os. Read this before making any changes.

## What It Is

A terminal-based productivity OS for technology leaders, built with Python and [Textual](https://github.com/Textualize/textual). All data is stored as structured markdown in monthly log files. No database.

## Stack

- Python 3.11+
- Textual (TUI framework)
- Rich (text styling inside Textual widgets)
- `tomllib` (stdlib, Python 3.11+) — reads `config.toml`
- `tomli-w` — writes `config.toml` from `ConfigScreen`
- No external data dependencies — all state lives in markdown log files

## Project Structure

```
app.py                        # Entry point — includes ConfigErrorScreen for bad logs_path
parser.py                     # All read/write logic against the log file
models.py                     # Dataclasses: Task, Dependency, Risk, SomedayItem, Accomplishment, DailyLogEntry, Event
quotes.py                     # Douglas Adams quotes, get_random_quote()
fiscal.py                     # NRF 4-5-4 fiscal calendar logic
config.toml                   # Machine-local config (gitignored) — sets logs_path
config.toml.example           # Committed template for config.toml
logs/                         # Default log directory (overridden by config.toml)
screens/
  dashboard.py                # Main screen — layout, bindings, all action handlers
  add_task.py
  task_complete.py
  add_dependency.py
  resolve_dependency.py
  add_risk.py
  add_someday.py
  add_accomplishment.py       # EditAccomplishmentScreen
  daily_checkin.py
  daily_log_navigator.py
  daily_log_viewer.py
  reopen_task.py
  help.py
  widget_viewer.py            # WidgetViewerScreen — read-only full-screen modal for any table
  tag_manager.py              # TagManagerScreen — rename/merge tags across all objects
  calendar.py                 # CalendarScreen — Gregorian + NRF fiscal calendar modal
  events.py                   # EventsScreen — CRUD for events
  add_event.py                # AddEventScreen form
  update.py                  # UpdateScreen — manager update generator
  weekly_review.py            # WeeklyReviewScreen
  config.py                   # ConfigScreen — edit logs_path via UI
widgets/
  metrics.py                  # MetricsWidget — single-line executive summary bar
  tasks.py                    # TaskTable
  dependencies.py             # DependencyTable
  risks.py                    # RisksTable
  someday.py                  # SomedayTable
  accomplishments_table.py    # AccomplishmentTable
  today.py                    # TodayWidget — scrollable, shows today's check-in
```

## Dashboard Layout

```
┌─────────────── director_os ───────────────────────────────┐
│  Executive Summary                                        │
│  [metrics bar]                                            │
│                          │                                │
│  Tasks                   │  Dependencies                  │
│  [task table]            │  [dependency table]            │
│                          │                                │
│  Today                   │  Risks                         │
│  [today panel]           │  [risks table]                 │
│                          │                                │
│                          │  Someday / Future              │
│                          │  [someday table]               │
│                          │                                │
│                          │  Accomplishments               │
│                          │  [accomplishments table]       │
├── [quote] ─────────────────────────── [date & time] ──────┤
```

Left column = immediate action. Right column = situational awareness.

## Key Patterns

### Portable log storage
- Log path is configured via `config.toml` (`logs_path` key)
- `_get_logs_path()` in `parser.py` reads the config and falls back to `logs/` if absent
- All file functions (`get_log_file`, `get_prev_log_file`, `get_events_file`) use `_get_logs_path()`
- `config.toml` is gitignored — each machine has its own; `config.toml.example` is committed
- `app.py` checks `_get_logs_path().exists()` on startup and shows `ConfigErrorScreen` if missing

### Tag handling
- `extract_tags(text)` — matches `#+` (handles `##tag` double-hash)
- `strip_tags(text)` — removes all `#+\S+` patterns including double-hash and malformed tokens like `##j/k`

### Edit/delete operations
- All edit and delete handlers in `dashboard.py` read from parser functions by row index (e.g. `get_tasks()[row]`) — never from table cell values, which may be truncated or styled

### Log file read/write
- Always use `load_log()` / `save_log()` for normal operations
- If a function needs to read/write the file directly (e.g. migration, `rename_tag`), use `get_log_file()` path directly to avoid `load_log` → function → `load_log` recursion
- `rename_tag()` in `parser.py` uses direct path read/write for this reason

### Parser functions
- `get_tasks()`, `get_dependencies()`, `get_risks()`, `get_someday_items()`, `get_accomplishments()` — all return lists of dataclass objects
- `get_metrics()` — returns a dict with: `tasks`, `overdue`, `deps`, `oldest_dep`, `high_risks`, `accomplishments`, `month_wins`
- `get_all_tags()` — returns sorted unique tags across all object types
- `rename_tag(old, new)` — renames all occurrences in the log file
- `get_today_entry()` — returns today's `DailyLogEntry` or `None`
- `_find_accomplishment_block(content, task_title)` — helper that uses `strip_tags()` for matching; used by edit/delete/reopen
- `promote_someday_item(item_text, priority, due_date, tags)` — removes someday item, adds task with full metadata
- `get_update_data(since_date)` — returns accomplished, tasks, deps, H risks, blocked items across all log files since date; accomplishments and tasks include `mgr` flag
- `save_update(since_date, data)` — writes structured bullet update to `<logs_path>/updates/update-YYYY-MM-DD.md`
- `toggle_mgr_task(task_title)` — toggles `Mgr:true` on a task line
- `toggle_mgr_accomplishment(task_title)` — toggles `Mgr:true` on an accomplishment block
- `get_events()`, `add_event()`, `edit_event()`, `delete_event()` — CRUD for `events.md`

- `check_event_notifications()` — called on mount; appends reminders to today's daily log

### Personal flag
- `Personal:true` inline field on tasks, accomplishments, risks, and someday items
- `toggle_personal_task()`, `toggle_personal_accomplishment()`, `toggle_personal_risk()`, `toggle_personal_someday()` — toggled via `h` keybind
- `♦` glyph rendered in all four widget tables for flagged items
- `P` cycles `_personal_filter` on `DashboardScreen`: `all` → `personal` → `work` → `all`
- Current filter shown in title bar as `director_os (All)` etc.
- Work view hides personal items unless also `Mgr:true` (tasks/accomplishments only)
- `_filtered_tasks()`, `_filtered_accomplishments()`, `_filtered_risks()`, `_filtered_someday()` helpers on `DashboardScreen` mirror widget filter logic — all row-index operations use these to avoid index mismatch
- Personal flag is independent of mgr flag — items can carry both

### Mgr flag
- `Mgr:true` inline field on tasks and accomplishments — same pattern as `Carried:true`
- `toggle_mgr_task()` / `toggle_mgr_accomplishment()` — toggled via `m` keybind
- Completing a `Mgr:true` task carries the flag into the accomplishment block
- `edit_task` preserves `Mgr:true` on the rewritten line
- `★` glyph rendered in task and accomplishment tables for flagged items
- Update screen defaults to `★ flagged only`; toggle off to show all
- `_find_accomplishment_block` strips `Mgr:true` before title comparison
- `toggle_mgr_task` searches on title prefix before `@mention` to handle tags between title and mention in raw log

### Carry-forward
- Rolled-over tasks get `Carried:true` appended to their log line at rollover time
- `get_tasks()` parses and strips `Carried:true`, sets `Task.carried = True`
- `TaskTable` renders `↩` appended to the title for carried tasks
- Editing a carried task drops the marker (intentional — once edited, it's no longer a carry-forward)

### Task-dependency handoff
- Completing a task (`d`) shows optional "Hand off to someone?" checkbox
- If checked, captures waiting-on item (pre-filled with task title), owner, and expected date
- Creates dependency with `HandoffFrom:` and `Expected:` fields in the log line
- `CompleteTaskScreen` dismisses `(outcome, handoff_tuple_or_None)`
- Glyphs stripped from `task_name` before pre-filling handoff item field

### Dependency-to-task reopen
- Resolving a dependency (`x`) shows optional "Reopen as task?" checkbox
- If checked, opens `AddTaskScreen` pre-filled with dependency item after resolving
- `ResolveDependencyScreen` dismisses `(notes, reopen_bool)`
- `action_resolve_dependency` reads item from `get_dependencies()[row]` — not cell value — to avoid truncation mismatch

### Dependency model
- `Dependency.handoff_from` — optional, parsed from `HandoffFrom:` field in log line
- `Dependency.expected_date` — optional, parsed from `Expected:\s*(\d{4}-\d{2}-\d{2})` in log line
- `AddDependencyScreen` includes expected date field for all new dependencies
- `edit_dependency` preserves `HandoffFrom` and writes `Expected` on save
- `DependencyTable` shows `Expected` as a fourth column

### Log sync
- `g` keybind in `dashboard.py` runs `git -C <logs_path> add -A && commit -m "sync" && push`
- Uses `subprocess.run` with `capture_output=True`; shows toast on success or error
- "Nothing to commit" is treated as success
- `action_quit` in `app.py` overrides Textual's default to auto-sync silently before exit; errors are swallowed
- Any git remote works — not GitHub-specific
### complete_task glyph stripping
- `complete_task` in `parser.py` strips `↩`, `★`, `♦` glyphs from `task_text` before building the search regex — cell values may have glyphs appended that would cause the pattern to not match
- Uses regex `re.compile(r"- \[ \] .*" + re.escape(search_text) + r".*\n")` — not literal string replace — because priority prefixes like `(A)` appear before the task title in the log line

### Accomplishment blocks
Stored as structured blocks:
```
- Task: {title}
  Outcome: {outcome}
  Completed: {date}
```
Always use `_find_accomplishment_block()` to locate them — never raw string match.

## UI Conventions

- Priority glyphs: `▲/●/▼` color-coded using `C_BAD/C_WARN/C_DEFAULT` constants — stored as `A/B/C` in log, rendered in `tasks.py`
- Task rows age-colored after 7 days (`C_WARN`) and 14 days (`C_BAD`)
- All DataTables have `zebra_stripes = True`
- Text fields truncated to 50 chars with `…` via `_t()` helper in each widget file
- Risk severity color-coded: H=`C_BAD`, M=`C_WARN`, L=`C_GOOD` using `rich.text.Text`
- Color constants `C_GOOD`, `C_WARN`, `C_BAD`, `C_DEFAULT` defined at top of each widget file for easy adjustment
- Dashboard screen background set to `$panel` to match DataTable default background
- All widget borders use `$accent` token — theme-aware, consistent across all panels
- Header (`#app-title`) and footer (`#app-footer`) use `$accent` background with `$background` text
- Widget section labels (Tasks, Dependencies, etc.) unstyled — blend into dashboard background
- Theme hardcoded to `gruvbox` in `app.py` — Rich color strings are not theme-aware so other themes produce mismatched results
- Carried tasks show `↩` glyph appended to title in task table
- Mgr-flagged tasks and accomplishments show `★` glyph appended to title
- Personal-flagged items show `♦` glyph appended to title in all four widget tables
- `p` (promote someday) opens `AddTaskScreen` pre-filled with item title for full metadata entry
- `S` moves focused task to someday via `AddSomedayScreen` pre-filled with task title
- `g` syncs logs repo via git with toast feedback; auto-syncs silently on quit
- `?` opens `HelpScreen` — two-column static layout grouped by widget/screen area (Tasks, Dependencies, Risks, Someday, Accomplishments, Views & Navigation, System)
- Toast notifications on: complete task, resolve dependency, promote someday, demote task, log sync
- `U` opens `UpdateScreen` — manager update generator; since-date input, live preview, writes to `updates/`
- `c` opens `CalendarScreen` — Gregorian + NRF 4-5-4 fiscal calendar; lazy imported
- `E` opens `EventsScreen` — lazy imported
- `v` opens `WidgetViewerScreen` — read-only, full content, no truncation, tags included
- `C` opens `ConfigScreen` — edit `logs_path`; saves to `config.toml`
- Quote rotates on launch and on `r` refresh
- Executive summary is a single-line metrics bar with red/green health coloring

## Keyboard Bindings

| Key | Action |
|-----|--------|
| `a` | Add task |
| `e` | Edit selected row |
| `d` | Complete task |
| `u` | Reopen accomplishment as task |
| `delete` | Delete selected row |
| `!` | Daily check-in |
| `W` | Weekly review |
| `t` | Tag manager |
| `w` | Add dependency |
| `x` | Resolve dependency |
| `i` | Add risk |
| `s` | Add someday item |
| `S` | Move focused task to someday |
| `p` | Promote someday item to task (opens AddTaskScreen pre-filled) |
| `l` | Open daily log navigator |
| `c` | Calendar (Gregorian + NRF fiscal) |
| `E` | Events |
| `v` | View focused widget full-screen |
| `r` | Refresh data + new quote |
| `m` | Flag task/accomplishment for manager update (`★`) |
| `h` | Toggle personal flag on focused item (♦) |
| `P` | Cycle personal filter (All → Personal only → Work only) |
| `U` | Manager update generator |
| `C` | Config (logs path) |
| `g` | Sync logs (git add/commit/push); auto-syncs on quit |
| `?` | Help (grouped by widget/screen) |
| `q` | Quit |

## Open Issues

| # | Title |
|---|-------|
| #4 | ~~Manager Update Generator~~ ✓ |
| #5 | Copilot Prompt Generator |
| #8 | ~~Accomplishment Details View~~ ✓ |
| #11 | ~~Theme Configuration~~ (removed — locked to gruvbox) |
| #13 | Dependency Aging Dashboard |
| #14 | Tag Analytics Dashboard |
| #15 | ~~Export Manager Update~~ ✓ |
| #16 | Package Director OS |
| #27 | Search / filter across tables |
| #28 | ~~Carry-forward indicator for rolled-over tasks~~ ✓ |

## Git Workflow

- Feature branches per issue (e.g. `feature/dashboard-layout`)
- Merge to `master` after testing
- User runs git commands manually in terminal

## Coding Conventions

- Minimal code — no verbose implementations, no unused helpers
- No comments unless genuinely necessary — code should be self-explanatory
- Do not add tests unless explicitly requested
- Do not remove existing code unless explicitly asked
- Prefer `fsReplace` with multiple diffs in one call over incremental single-line edits
- All screens are `ModalScreen` subclasses; dismiss with result tuple or `None`/`False` for cancel
