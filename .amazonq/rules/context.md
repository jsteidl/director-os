# director_os — AI Context File

This file provides full context for AI-assisted development on director_os. Read this before making any changes.

## What It Is

A terminal-based productivity OS for technology leaders, built with Python and [Textual](https://github.com/Textualize/textual). All data is stored as structured markdown in monthly log files. No database.

## Stack

- Python 3.11+
- Textual (TUI framework)
- Rich (text styling inside Textual widgets)
- `tomllib` (stdlib, Python 3.11+) — reads `config.toml`
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
  weekly_review.py            # WeeklyReviewScreen
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
- `strip_tags(text)` — removes all `#+word` patterns including double-hash

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
- `get_events()`, `add_event()`, `edit_event()`, `delete_event()` — CRUD for `events.md`
- `check_event_notifications()` — called on mount; appends reminders to today's daily log

### complete_task
Uses regex `re.compile(r"- \[ \] .*" + re.escape(task_text) + r".*\n")` — not literal string replace — because priority prefixes like `(A)` appear before the task title in the log line.

### Accomplishment blocks
Stored as structured blocks:
```
- Task: {title}
  Outcome: {outcome}
  Completed: {date}
```
Always use `_find_accomplishment_block()` to locate them — never raw string match.

## UI Conventions

- Priority glyphs: `▲/●/▼` color-coded red/yellow/cyan — stored as `A/B/C` in log, rendered in `tasks.py`
- Task rows age-colored after 7 days (yellow) and 14 days (red)
- All DataTables have `zebra_stripes = True`
- Text fields truncated to 50 chars with `…` via `_t()` helper in each widget file
- Risk severity color-coded: H=red, M=yellow, L=green using `rich.text.Text`
- `c` opens `CalendarScreen` — Gregorian + NRF 4-5-4 fiscal calendar; lazy imported
- `E` opens `EventsScreen` — lazy imported
- `v` opens `WidgetViewerScreen` — read-only, full content, no truncation, tags included
- `t` opens `TagManagerScreen` — rename/merge tags across all objects
- Title bar: `director_os` docked top, accent background, centered
- Footer: quote (left, `1fr`) + clock (right, `auto`) in a horizontal container docked bottom
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
| `p` | Promote someday item to task |
| `l` | Open daily log navigator |
| `c` | Calendar (Gregorian + NRF fiscal) |
| `E` | Events |
| `v` | View focused widget full-screen |
| `r` | Refresh data + new quote |
| `?` | Help |
| `q` | Quit |

## Open Issues

| # | Title |
|---|-------|
| #4 | Manager Update Generator |
| #5 | Copilot Prompt Generator |
| #8 | Accomplishment Details View |
| #11 | Theme Configuration |
| #14 | Tag Analytics Dashboard |
| #15 | Export Manager Update |
| #16 | Package Director OS |
| #27 | Search / filter across tables |
| #28 | Carry-forward indicator for rolled-over tasks |

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
