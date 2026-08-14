# director_os

A terminal-based productivity OS for technology leaders. Built with [Textual](https://github.com/Textualize/textual).

director_os is a low-friction way to manage your work, stay on top of what matters, and report out on status and accomplishments — without leaving the terminal. All data is stored in plain markdown files, one per month. No database, no sync service, no lock-in.

## Screenshot

![director_os dashboard](screenshots/dashboard.svg)

## Features

- **Executive Summary** — live status bar showing overdue count, high risk count, oldest task age, and wins this month
- **Task tracking** — add, edit, complete, delete, and reopen tasks with priority (A/B/C), due dates, and tags
- **Dependency tracking** — track what you're waiting on, by owner and age; hand off from completed tasks
- **Risk tracking** — log risks with severity (H/M/L), owner, and date
- **Someday / Future** — capture ideas and future work; promote to active tasks or demote tasks to someday
- **Accomplishments** — auto-logged when tasks are completed; flag with `m` to surface in manager updates
- **Manager update** — generate a structured bullet update since a given date; written to `updates/` in your logs directory
- **Daily check-in** — structured daily log with priorities, accomplished, blocked, and notes
- **Today panel** — shows today's check-in at a glance
- **Weekly review** — structured weekly summary
- **Calendar** — Gregorian and NRF 4-5-4 fiscal calendar with due date and event markers
- **Events** — track holidays, deadlines, OOO with configurable reminders
- **Personal flag** — mark items as personal (♦); cycle dashboard between All / Personal / Work views
- **Tag manager** — rename and merge tags across all objects
- **Log sync** — push logs to any git remote with `g`; auto-syncs on quit

Press `?` in the app for a full keyboard shortcut reference.

## Installation

```bash
pip install -r requirements.txt
cp config.toml.example config.toml  # then edit logs_path
python app.py
```

## Configuration

Set your logs path in `config.toml`:

```toml
logs_path = "/path/to/your/logs"
```

`config.toml` is gitignored — each machine has its own. The app falls back to `logs/` if no config is present. Theme is hardcoded to `gruvbox`.

The logs directory can be any local or synced path (e.g. a private git repo, OneDrive folder). If the path is missing on startup, a clear error screen is shown.

## Built With AI Assistance

This project was developed with the help of AI coding assistants. Initial scaffolding and early features were built using [GitHub Copilot](https://github.com/features/copilot). The majority of the architecture, feature development, and refinement was done in collaboration with [Amazon Q Developer](https://aws.amazon.com/q/developer/), which proved to be the more robust and impactful tool for this kind of iterative, context-heavy development.
