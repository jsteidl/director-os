# director_os — Ideas & Future Direction

## v2 Architecture

### Core Change: SQLite Backend
- Replace monthly markdown log files with a single SQLite database
- Proper IDs (UUID or incrementing) on all objects — tasks, deps, risks, someday, accomplishments
- Foreign keys enable real linking between objects
- Cross-month queries without scanning multiple files
- Export to markdown on demand for portability/readability
- Git sync still works — just syncing a `.db` file instead of `.md` files

### Object Linking
- Task → Dependency: completing a task and handing off carries the task ID into the dep
- Dependency → Task: resolving a dep and reopening as task carries the dep ID
- Full lineage tracing: origin task → dep → resolution → new task
- `HandoffFrom:` becomes a real foreign key, not a text match
- Manager update becomes a narrative chain, not just a snapshot

### Quick Capture CLI
- `python app.py --add "task title"` — no TUI, just appends and exits
- Supports `--priority`, `--due`, `--project`, `--tags`, `--someday`
- Alias to something short (e.g. `dos`) for speed
- Solves the "coffee shop capture" problem without opening a full session
- No sync conflict risk — in/out fast

### Cross-Month History
- Accomplishments, resolved deps, risks across all time queryable in one place
- `:update` can generate narrative chains not just flat bullets
- Performance on large history (file scanning gets slow over time)

### 1:1 Note Integration
- Structured 1:1 log format (per-person, dated entries)
- Action items in 1:1 notes promotable to tasks directly
- Review "last session" before a meeting
- Scratch pad convention: use `- [ ]` for action items during note-taking

### Quick Capture GUI
- Small floating window — title, priority, project — hit enter, done
- Cross-platform (Mac + Windows)
- For non-terminal moments (coffee shop, phone-adjacent)
- Could be minimal Textual app, tkinter popup, or system tray

### Narrative Manager Updates
- `:update` follows linked chains to tell a story, not just list bullets:
  ```
  EDP
    ✓ Aligned on AIM architecture → handed off to Pavan/Scott → resolved 10/15
    ✓ Sent Snowflake MSA → waiting on Joel/Dipti → SOW review in progress
    ⚡ Connect pyspark ETL with AIM-V → blocked on TD migration completion
  ```
- Manager sees causality and progress, not a flat snapshot

### Query & Visualization
- "Show me everything linked to `edp` across all time" — one query, no file scanning
- Dependency graph — visualize chains of tasks, deps, risks
- Timeline of completions — burndown, velocity, patterns
- Carried task burndown — how long do things linger before closing
- All trivial with a proper query layer; impossible with flat files

- `:export` command generates current markdown log format from DB
- Human-readable, portable, no lock-in
- Could also export CSV/JSON for other tools

---

## Open Issues (current v1)

| # | Title |
|---|-------|
| #5 | Copilot Prompt Generator |
| #13 | Dependency Aging Dashboard |
| #14 | Tag Analytics Dashboard |
| #16 | Package Director OS |

---

## Backlog (v1 improvements)

- Help screen missing `0` (clear filters) keybind
- `get_events_for_rollover()` not yet wired into `_scaffold.py`
- Reopen task from accomplishment doesn't carry tags/project/priority
- `r` key on dep table (dep → risk) could also offer dep → task directly
- Multi-machine: warn if remote is ahead on launch (another session may be active)

