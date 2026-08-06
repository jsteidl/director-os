# director_os — AI Context File

This file provides full context for AI-assisted development on director_os. Read this before making any changes.

## What It Is

A terminal-based productivity OS for technology leaders, built with Python and [Textual](https://github.com/Textualize/textual). All data is stored as structured markdown in monthly log files. No database.

## Stack

- Python 3.11+
- Textual (TUI framework)
- Rich (text styling inside Textual widgets)
- No external data dependencies — all state lives in `logs/YYYY-MM-Director-Log.md`

## Project Structure

```
app.py                        # Entry point
parser.py                     # All read/write logic against the log file
models.py                     # Dataclasses: Task, Dependency, Risk, SomedayItem, Accomplishment, DailyLogEntry
quotes.py                     # Douglas Adams quotes, get_random_quote()
logs/                         # Monthly markdown log files
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

### Tag handling
- The log stores raw tags inline (e.g. `- [ ] Fix bug ##Support`)
- `parser.py` strips tags into a separate `tags: list[str]` field on each model via `strip_tags()` and `extract_tags()`
- All display, lookup, edit, and delete operations must use `strip_tags()` for comparison — never match raw log text against a display value
- The widget viewer re-appends tags when displaying full content

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

- All DataTables have `zebra_stripes = True`
- Text fields truncated to 50 chars with `…` via `_t()` helper in each widget file
- Risk severity color-coded: H=red, M=yellow, L=green using `rich.text.Text`
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
| `t` | Tag manager |
| `w` | Add dependency |
| `x` | Resolve dependency |
| `i` | Add risk |
| `s` | Add someday item |
| `p` | Promote someday item to task |
| `l` | Open daily log navigator |
| `W` | Weekly review |
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
| #12 | Weekly Review Screen |
| #14 | Tag Analytics Dashboard |
| #15 | Export Manager Update |
| #16 | Package Director OS |
| #24 | Portable log storage via configurable logs path |
| #25 | Confirmation dialog on delete |
| #26 | Task aging color coding |
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
