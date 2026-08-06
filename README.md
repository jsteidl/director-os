# director_os

A terminal-based operating system for technology leaders. Built with [Textual](https://github.com/Textualize/textual).

## Features

- **Executive Summary** — live status bar showing tasks, overdue count, waiting-on count, oldest dependency age, high risk count, and wins this month — color-coded red/green by health
- **Task tracking** — add, edit, complete, delete, and reopen tasks with priority (A/B/C), due dates, and tags
- **Dependency tracking** — track what you're waiting on, by owner and age
- **Risk tracking** — log risks with severity (H/M/L), owner, and date — severity color-coded in the dashboard
- **Someday / Future** — capture ideas and future work, promote to active tasks when ready
- **Accomplishments** — auto-logged when tasks are completed, editable, reopenable
- **Daily check-in** — structured daily log with priorities, accomplished, blocked, and notes
- **Daily log navigator** — browse and review past daily log entries
- **Today panel** — shows today's check-in priorities, accomplished, and blocked at a glance
- **Widget viewer** — press `v` on any table to open a full-screen read-only expanded view
- **Monthly log files** — one markdown file per month, auto-scaffolded and rolled over with open tasks and dependencies carried forward

## Layout

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
├───────────────────────────────── [date & time] ───────────┤
```

Left column = immediate action. Right column = situational awareness.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `a` | Add task |
| `e` | Edit selected row |
| `d` | Complete task |
| `u` | Reopen accomplishment as task |
| `delete` | Delete selected row |
| `t` | Daily check-in |
| `w` | Add dependency |
| `x` | Resolve dependency |
| `i` | Add risk |
| `s` | Add someday item |
| `p` | Promote someday item to task |
| `l` | Open daily log navigator |
| `v` | View focused widget full-screen |
| `r` | Refresh data |
| `?` | Help |
| `q` | Quit |

## Log Format

Logs are stored as markdown files in `logs/YYYY-MM-Director-Log.md`. Each month auto-scaffolds with sections for tasks, dependencies, risks, someday items, accomplishments, and daily log entries. Open tasks and dependencies are carried forward on rollover.

## Running

```bash
pip install -r requirements.txt
python app.py
```
