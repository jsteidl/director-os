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
models.py                     # Dataclasses: Task, Dependency, Risk, SomedayItem, Accomplishment, DailyLogEntry, Event
migrate_logs.py               # One-time migration script; --dry-run flag; accepts optional path override arg
quotes.py                     # Douglas Adams quotes, get_random_quote()
fiscal.py                     # NRF 4-5-4 fiscal calendar logic
config.toml                   # Machine-local config (gitignored) — sets logs_path
config.toml.example           # Committed template for config.toml
logs/                         # Default log directory (overridden by config.toml)
parser/
  __init__.py                 # Re-exports all public functions — always import from `parser`, never submodules
  _core.py                    # _get_logs_path, load_log, save_log, extract_tags, strip_tags, _clean, get_terminal_size
  _files.py                   # Path helpers: get_log_file, get_prev_log_file, get_events_file, get_projects_file, get_scratch_file
  _scaffold.py                # scaffold_log, rollover_log
  tasks.py                    # get_tasks, add_task, edit_task, delete_task, complete_task, reopen_task, toggle_mgr_task, toggle_personal_task
  dependencies.py             # get_dependencies, add_dependency, edit_dependency, delete_dependency, resolve_dependency, toggle_mgr_dependency
  risks.py                    # get_risks, add_risk, edit_risk, delete_risk, resolve_risk, toggle_mgr_risk, toggle_personal_risk
  someday.py                  # get_someday_items, add_someday_item, edit_someday_item, delete_someday_item, promote_someday_item, toggle_personal_someday
  accomplishments.py          # get_accomplishments, add_accomplishment, edit_accomplishment, delete_accomplishment, toggle_mgr_accomplishment, toggle_personal_accomplishment
  daily.py                    # get_today_entry, get_all_daily_entries, add_daily_entry, edit_daily_entry
  tags.py                     # get_all_tags, get_tag_counts, rename_tag, delete_tag
  projects.py                 # get_all_projects, get_project_counts, get_project_meta, save_project_meta, delete_project_meta, rename_project, delete_project
  metrics.py                  # get_metrics, get_update_data, save_update
  events.py                   # get_events, add_event, edit_event, delete_event, check_event_notifications
  scratch.py                  # get_scratch, save_scratch
screens/
  dashboard.py                # Main screen — layout, bindings, all action handlers
  add_task.py
  task_complete.py
  add_dependency.py
  due_date.py                 # Shared due date resolution: resolve_due(), resolve_since(), DUE_PLACEHOLDER, DUE_ERROR, SINCE_PLACEHOLDER, SINCE_ERROR
  resolve_dependency.py
  add_risk.py
  add_someday.py
  add_accomplishment.py       # AddAccomplishmentScreen (standalone) + EditAccomplishmentScreen (edit with tags/project)
  daily_checkin.py
  daily_log_navigator.py
  daily_log_viewer.py
  reopen_task.py
  help.py
  widget_viewer.py            # WidgetViewerScreen — read-only full-screen modal for any table
  tag_manager.py              # TagManagerScreen — rename/merge/delete tags; shows usage counts; zero-count rows highlighted
  project_manager.py          # ProjectManagerScreen — rename projects; color-coded per-type counts; ⚠ high-risk indicator; Display and Description fields per project; saves to projects.md
  calendar.py                 # CalendarScreen — Gregorian + NRF fiscal calendar modal
  events.py                   # EventsScreen — CRUD for events
  add_event.py                # AddEventScreen form
  update.py                   # UpdateScreen — manager update generator; grouped by project (default) or flat toggle; ★ flagged only switch; personal items always excluded; display name + description as grouped headers
  weekly_review.py            # WeeklyReviewScreen
  config.py                   # ConfigScreen — edit logs_path via UI
  scratch.py                  # ScratchPadScreen — markdown scratch pad with checkbox navigation and promote-to-task
  command.py                  # CommandScreen — command palette modal (:sync, :config, :tags, :projects, :update, :weekly, :events)
  tab_complete.py             # TabCompleteMixin — intercepts Tab to apply SuggestFromList completion on focused Input
widgets/
  metrics.py                  # MetricsWidget — single-line executive summary bar; personal_filter attribute; computes filtered metrics inline (does not call get_metrics())
  tasks.py                    # TaskTable — tag_filter, project_filter, personal_filter attributes
  dependencies.py             # DependencyTable — tag_filter, project_filter attributes
  risks.py                    # RisksTable — tag_filter, project_filter, personal_filter attributes
  someday.py                  # SomedayTable — tag_filter, project_filter, personal_filter attributes
  accomplishments_table.py    # AccomplishmentTable — tag_filter, project_filter, personal_filter attributes; Project and Tags columns
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
- `_get_logs_path()` in `parser/_core.py` reads the config and falls back to `logs/` if absent
- All file functions (`get_log_file`, `get_prev_log_file`, `get_events_file`) use `_get_logs_path()`
- `config.toml` is gitignored — each machine has its own; `config.toml.example` is committed
- `app.py` checks `_get_logs_path().exists()` on startup and shows `ConfigErrorScreen` if missing
- `config.toml` supports optional `terminal_size = [width, height]` — emits xterm resize escape on launch via `sys.stdout.write(f"\033[8;{rows};{cols}t")` before `App.run()`
- `get_terminal_size()` in `parser/_core.py` reads this value; no-op if not set or not a tty

### Log format
- All single-line object types use pipe-delimited named fields: `- Title | Field: value | Field: value`
- Field names are capitalized with colon-space: `Due: 2026-09-23`, `Tags: strategy hiring`, `Project: edp`
- Optional fields are omitted entirely when not set — no empty `Tags: ` or `Project: `
- Tag values are lowercase and space-separated; project values are lowercase with underscores
- Accomplishments use a multi-line block format with pipe fields on the Task line
- Resolved dependency blocks are write-once and never migrated
- Full spec in `.amazonq/rules/log-format.md`
- Migration script: `migrate_logs.py` — converts legacy `Key:value` / `+project` / `#tag` format

### Tag handling
- `extract_tags(text)` — reads `Tags: word1 word2` from pipe field; falls back to `#tag` for legacy/daily log lines
- `strip_tags(text)` — removes `| Tags: ...` pipe field; falls back to `#tag` stripping for legacy lines

### Edit/delete operations
- All edit and delete handlers in `dashboard.py` read from parser functions by row index (e.g. `get_tasks()[row]`) — never from table cell values, which may be truncated or styled

### Log file read/write
- Always use `load_log()` / `save_log()` for normal operations
- If a function needs to read/write the file directly (e.g. migration, `rename_tag`), use `get_log_file()` path directly to avoid `load_log` → function → `load_log` recursion
- `rename_tag()`, `delete_tag()`, `rename_project()`, `delete_project()` all use direct path read/write for this reason
- Always import from `parser` (the package `__init__`), never from submodules directly

### Parser functions
- `get_tasks()`, `get_dependencies()`, `get_risks()`, `get_someday_items()`, `get_accomplishments()` — all return lists of dataclass objects
- `get_metrics()` — returns a dict with: `tasks`, `overdue`, `deps`, `oldest_dep`, `high_risks`, `accomplishments`, `month_wins` — not called by `MetricsWidget` (which computes filtered metrics inline)
- `get_scratch()` / `save_scratch()` — read/write `scratch.md` in logs directory
- `_parse_task_line(line)` — in `parser/tasks.py`; splits on ` | `, extracts all named fields
- `_parse_dep_line`, `_parse_risk_line`, `_parse_someday_line` — same pattern in their respective modules
- `_build_task_line`, `_build_dep_line`, `_build_risk_line`, `_build_someday_line` — write canonical pipe-delimited lines
- `get_all_tags()` — returns sorted unique tags across all object types
- `get_all_projects()` — returns sorted unique project names across all object types
- `get_tag_counts()` — returns `{tag: count}` across all object types
- `get_project_counts()` — returns `{project: {tasks, deps, risks, high_risks, someday, accomplishments}}` counts
- `rename_tag(old, new)` — rewrites `Tags:` field per line in the log file
- `delete_tag(tag)` — removes tag from `Tags:` field per line in the log file
- `rename_project(old, new)` — rewrites `Project:` field in the log file; keeps `projects.md` in sync
- `delete_project(tag)` — removes `Project:` field from all matching lines; removes from `projects.md`
- `get_projects_file()` — path to `projects.md` in logs directory
- `get_project_meta()` — returns `{tag: {display, description}}` from `projects.md`
- `save_project_meta(tag, display, description)` — upsert a project meta entry
- `delete_project_meta(tag)` — remove a project meta entry
- `toggle_mgr_dependency(item_text)` — toggles `Mgr: true` on a dependency line
- `toggle_mgr_risk(description)` — toggles `Mgr: true` on a risk line
- `get_today_entry()` — returns today's `DailyLogEntry` or `None`
- `_find_accomplishment_block(content, task_title)` — matches on clean title only (strips all pipe fields before comparison)
- `promote_someday_item(item_text, priority, due_date, tags, project)` — removes someday item, adds task with full metadata
- `add_accomplishment(task, outcome, tags, project)` — writes accomplishment block directly; used by standalone add
- `get_update_data(since_date)` — returns accomplished, tasks, deps, H risks, blocked, resolved_deps, resolved_risks across all log files since date
- `save_update(since_date, data)` — writes structured bullet update including resolved deps/risks to `<logs_path>/updates/update-YYYY-MM-DD.md`
- `toggle_mgr_task(task_title)` — toggles `Mgr: true` on a task line
- `toggle_mgr_accomplishment(task_title)` — toggles `Mgr: true` on an accomplishment block
- `get_events()`, `add_event()`, `edit_event()`, `delete_event()` — CRUD for `events.md`
- `check_event_notifications()` — called on mount; appends reminders to today's daily log

### Personal flag
- `Personal: true` pipe field on tasks, accomplishments, risks, and someday items
- `toggle_personal_task()`, `toggle_personal_accomplishment()`, `toggle_personal_risk()`, `toggle_personal_someday()` — toggled via `H` keybind
- `♦` glyph rendered in all widget tables for flagged items
- `P` cycles `_personal_filter` on `DashboardScreen`: `all` → `personal` → `work` → `all`
- Work view hides personal items unless also `Mgr:true` (tasks/accomplishments only)
- `_filtered_tasks()`, `_filtered_accomplishments()`, `_filtered_risks()`, `_filtered_someday()` helpers on `DashboardScreen` mirror widget filter logic — all row-index operations use these to avoid index mismatch
- Personal flag is independent of mgr flag — items can carry both

### Mgr flag
- `Mgr: true` pipe field on tasks, accomplishments, dependencies, and risks
- `toggle_mgr_task()` / `toggle_mgr_accomplishment()` / `toggle_mgr_dependency()` / `toggle_mgr_risk()` — toggled via `M` keybind
- Completing a `Mgr: true` task carries the flag into the accomplishment block
- `edit_task` preserves `Mgr: true` on the rewritten line; `edit_dependency` and `edit_risk` preserve it too
- `★` glyph rendered in task, accomplishment, dependency, and risk tables for flagged items
- Update screen defaults to `★ flagged only`; toggle off to show all with `★` inline
- Personal items always excluded from manager update regardless of mgr flag
- Deps: shown in update only if `★`-flagged (when switch on) or all (when switch off)
- Risks: H-severity always shown; M/L shown only if `★`-flagged
- `_find_accomplishment_block` matches on clean title only — strips all pipe fields before comparison
- `toggle_mgr_task` matches by `Created:` date when available

### Project field
- `Project: name` pipe field on tasks, accomplishments, dependencies, risks, and someday items
- `Task.project`, `Accomplishment.project`, `Dependency.project`, `Risk.project`, `SomedayItem.project` — `str | None`
- All add/edit modals expose Tags and Project fields; project uses underscore convention (`edp`, `bi_discovery`)
- `complete_task` carries `Project:` forward from the task line into the accomplishment block
- `promote_someday_item(... project="")` writes `Project:` on the new task line
- `AddTaskScreen` dismisses 5-tuple `(task, priority, due_date, tag, project)`
- `]`/`[` cycles global project filter forward/reverse on `DashboardScreen`; `0` clears all filters
- Project filter applies to all widgets; project list pulled from all object types
- `TaskTable` renders project in the Project column
- `AccomplishmentTable`, `DependencyTable`, `RisksTable`, `SomedayTable` all render Project and Tags columns

### Global tag and project filters
- Filter state lives on `DashboardScreen` as `_tag_filter: str` and `_project_filter: str`
- `refresh_data()` pushes both filters to all widgets on every refresh
- `f`/`F` cycles tag filter forward/reverse — applies to all widgets (tasks, deps, risks, someday, accomplishments)
- `]`/`[` cycles project filter forward/reverse — applies to all widgets; project list pulled from all object types
- `0` clears both tag and project filters simultaneously
- Active filters shown in title bar: `director_os (All #active +DataPlatform)`
- Tag list for cycling pulled from `get_all_tags()` (all object types); project list from all object types

### Carry-forward
- Rolled-over tasks get `| Carried: true` appended to their log line at rollover time
- `get_tasks()` parses and strips `Carried: true`, sets `Task.carried = True`
- `TaskTable` renders `↩` appended to the title for carried tasks
- Editing a carried task drops the marker (intentional — once edited, it's no longer a carry-forward)
- `complete_task` carries `Mgr: true`, `Personal: true`, `Project:`, and tags forward into the accomplishment block

### Due date shorthands
- Shared module `screens/due_date.py` exports `resolve_due()`, `resolve_since()`, and their placeholder/error constants
- `resolve_due` shorthands: `t`/`today`=today, `tm`/`tomorrow`=+1d, `w`/`week`=+7d, `2w`=+14d, `+N`=+N days, `YYYY-MM-DD`=literal
- `resolve_since` shorthands: `t`/`today`=today, `y`/`yesterday`=-1d, `lw`/`lastweek`=last Monday, `-N`=-N days, `-2w`=-2 weeks, `YYYY-MM-DD`=literal
- `resolve_due` used in `AddTaskScreen`, `AddDependencyScreen`, `CompleteTaskScreen`; `resolve_since` used in `UpdateScreen`

### Task-dependency handoff
- Completing a task (`x` on TaskTable) shows optional "Hand off to someone?" checkbox
- If checked, captures waiting-on item (pre-filled with task title), owner, and expected date (supports due date shorthands)
- Creates dependency with `HandoffFrom:` and `Expected:` fields in the log line
- `CompleteTaskScreen` dismisses `(outcome, handoff_tuple_or_None)`
- Glyphs stripped from `task_name` before pre-filling handoff item field

### Dependency-to-risk
- `r` keybind on `DependencyTable` opens `AddRiskScreen` pre-filled with dependency item and owner
- On save: deletes the dependency, adds the risk
- Severity field is blank — must be filled in manually; `get_risks()` regex requires `[HML]` — blank severity causes silent parse failure

### Dependency-to-task reopen
- Resolving a dependency (`x` on DependencyTable) shows optional "Reopen as task?" checkbox
- If checked, opens `AddTaskScreen` pre-filled with dependency item after resolving
- `ResolveDependencyScreen` dismisses `(notes, reopen_bool)`
- `action_resolve_dependency` reads item from `get_dependencies()[row]` — not cell value — to avoid truncation mismatch

### Dependency model
- `Dependency.handoff_from` — optional, parsed from `HandoffFrom:` field in log line
- `Dependency.expected_date` — optional, parsed from `Expected:\s*(\d{4}-\d{2}-\d{2})` in log line
- `AddDependencyScreen` includes expected date, tags, and project fields; dismisses 5-tuple `(item, owner, expected, tags, project)`
- `edit_dependency` preserves `HandoffFrom` and writes `Expected`, tags, project on save
- `DependencyTable` shows `Expected`, `Project`, `Tags` columns

### Log sync
- `G` keybind in `dashboard.py` runs `git -C <logs_path> add -A && commit -m "sync" && push`
- Uses `subprocess.run` with `capture_output=True`; shows toast on success or error
- "Nothing to commit" is treated as success
- `action_quit` in `app.py` overrides Textual's default to auto-sync silently before exit; errors are swallowed
- Any git remote works — not GitHub-specific

### Task matching by Created: date
- `complete_task(task_text, outcome, created=None)` and `edit_task(old_title, new_title, ..., created=None)` both accept an optional `created` date
- When `created` is provided, matching uses `Created:YYYY-MM-DD` as the unique key — avoids regex mismatch when tags appear between the title and other text
- `action_complete_task` and `_edit_task` in `dashboard.py` pass `task.created` from the parsed `Task` object
- Fallback (no `created`): title-based match, splitting on ` @` before building the regex
- All tasks added via `add_task` include `Created:` so new tasks always match by date
- `add_task` writes tags as `Tags: word1 word2` — the tag field accepts space-separated words without `#`

### Scratch pad
- `n` opens `ScratchPadScreen` — persistent markdown scratch pad stored as `scratch.md` in logs directory
- Default view mode renders `Markdown`; `e` switches to `TextArea` edit mode; `ctrl+s` saves and returns to view; `esc` closes from either mode
- `_to_md(text, cursor)` — converts single line breaks to hard breaks, plain bullets to `•`, injects `›` cursor marker next to selected checkbox item
- Checkbox navigation: `j`/`k` move `_cursor` over `- [ ]`/`- [x]` items; `space` toggles and auto-saves; `p` promotes selected item via `AddTaskScreen` pre-filled with item text; on save, item removed from scratch and `add_task()` called
- Keys work via screen-level `BINDINGS` with `self.set_focus(None)` in view mode
- `action_scratch_pad` passes `lambda _: self.refresh_data()` so dashboard refreshes on close
- Syncs with git on `G` / quit auto-sync

### Manager update
- `UpdateScreen` (`:update`) — grouped by project by default; flat view via Grouped toggle switch
- Grouped view: `### Display Name` header, `_description_` subtitle, items nested under project; untagged items in `(General)` at bottom
- Flat view: traditional section-per-type layout
- `★ flagged only` switch: when on, filters tasks/accomplishments/deps to flagged only; when off, shows all with `★` inline next to flagged items
- Risks: H-severity always included; M/L included only if `★`-flagged
- Personal items always excluded regardless of switches
- Resolved deps/risks and blocked always shown flat at the bottom
- `save_update()` mirrors grouped/flat structure in saved markdown

### Command palette
- `:` opens `CommandScreen` — input-driven command palette modal
- Dispatches: `sync`, `config`, `tags`, `projects`, `update`, `weekly`, `events`
- Returns command string via `dismiss()`; `DashboardScreen.action_command` handles routing

### Tag manager
- `TagManagerScreen` shows all tags with usage count on the right — red `0` for unused, dim count otherwise
- Zero-count rows have muted label styling
- Clearing an input and saving deletes that tag from the log via `delete_tag()`
- Changing an input and saving renames via `rename_tag()`

### Project manager
- `ProjectManagerScreen` (`:projects`) shows all projects with per-type counts: T=Tasks, D=Deps, R=Risks, S=Someday, A=Accomplishments
- Counts are color-coded: tasks=cyan, deps=yellow, risks=red, someday=muted, accomplishments=green, total=light
- `⚠` glyph shown in red if project has any H-severity risks
- Each row has Display and Description inputs — saved to `projects.md` in logs directory
- Display name used as header in grouped manager update; Description shown as subtitle
- Changing tag input and saving renames via `rename_project()`; blank tag input is a no-op
- `projects.md` format: `- Tag | Display: Display Name | Description: description text`

### Autocomplete on tag/project inputs
- All add/edit screens use `SuggestFromList` from `textual.suggester` on tag and project `Input` fields
- Suggestion lists built at compose time from `get_all_tags()` / `get_all_projects()`
- `TabCompleteMixin` in `screens/tab_complete.py` intercepts Tab to apply the current suggestion without moving focus
- All screens using the mixin set `priority=True` on their `ctrl+s` binding to ensure save works regardless of focused widget

### Accomplishment blocks
Stored as structured blocks:
```
- Task: {title} [| Mgr: true] [| Personal: true] [| Project: name] [| Tags: tag1 tag2]
  Outcome: {outcome}
  Completed: {date}
```
Always use `_find_accomplishment_block()` to locate them — never raw string match.
`_find_accomplishment_block` strips all pipe fields before title comparison.

## UI Conventions

- Priority glyphs: `▲/●/▼` color-coded using `C_BAD/C_WARN/C_DEFAULT` constants — stored as `A/B/C` in log, rendered in `tasks.py`
- Task rows color-coded by due date when present: overdue=red, today=cyan, this week=yellow, next week=green, future=dim; falls back to age-based coloring (7d=yellow, 14d=red) when no due date
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
- Personal-flagged items show `♦` glyph appended to title in all widget tables
- `t` (promote someday) opens `AddTaskScreen` pre-filled with item title for full metadata entry
- `s` moves focused task to someday via `AddSomedayScreen` pre-filled with task title
- `G` syncs logs repo via git with toast feedback; auto-syncs silently on quit
- `?` opens `HelpScreen` — two-column static layout grouped by widget/screen area
- Toast notifications on: complete task, resolve dependency, promote someday, demote task, log sync
- `:update` opens `UpdateScreen` — manager update generator; since-date input, live preview, writes to `updates/`
- `c` opens `CalendarScreen` — Gregorian + NRF 4-5-4 fiscal calendar; lazy imported
- `:events` opens `EventsScreen` — lazy imported
- `v` opens `WidgetViewerScreen` — read-only, full content, no truncation, tags included
- `:config` opens `ConfigScreen` — edit `logs_path`; saves to `config.toml`
- Quote rotates on launch and on `R` refresh
- Executive summary is a single-line metrics bar with red/green health coloring
- Title bar shows active filters: `director_os (All #tag +Project)`

## Keyboard Bindings

| Key | Action |
|-----|--------|
| `a` | Add (context-sensitive: task / dep / risk / someday / accomplishment) |
| `e` | Edit selected row |
| `x` | Complete task (TaskTable) or resolve dependency (DependencyTable) |
| `u` | Reopen accomplishment as task |
| `delete` | Delete selected row |
| `s` | Send focused task to someday |
| `t` | Promote focused someday item to task |
| `r` | Move focused dependency to risk |
| `M` | Flag task/accomplishment for manager update (`★`) |
| `H` | Toggle personal flag on focused item (`♦`) |
| `P` | Cycle personal filter (All → Personal only → Work only) |
| `f` | Cycle global tag filter forward (all → #tag1 → #tag2 → all) |
| `F` | Cycle global tag filter reverse |
| `[` | Cycle global project filter reverse |
| `]` | Cycle global project filter forward |
| `0` | Clear all filters |
| `!` | Daily check-in |
| `l` | Open daily log navigator |
| `c` | Calendar (Gregorian + NRF fiscal) |
| `v` | View focused widget full-screen |
| `R` | Refresh data + new quote |
| `G` | Sync logs (git add/commit/push); auto-syncs on quit |
| `n` | Scratch pad |
| `b` | Briefing screen |
| `:` | Command palette (sync, config, tags, projects, update, weekly, events) |
| `?` | Help |
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
| #27 | ~~Search / filter across tables~~ ✓ (global tag + project filters across all widgets) |
| #28 | ~~Carry-forward indicator for rolled-over tasks~~ ✓ |
| —  | ~~`feature/metadata-parity`~~ ✓ — full tags + project parity across all object types |
| —  | ~~`refactor/parser-split`~~ ✓ — monolithic parser.py split into parser/ package |
| —  | ~~`refactor/log-format`~~ ✓ — pipe-delimited named fields across all object types; migration script included |

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
