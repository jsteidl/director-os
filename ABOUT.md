# What is director_os?

director_os is a terminal-based productivity system built specifically for technology leaders — engineering managers, directors, VPs, and anyone who spends their day context-switching between execution, communication, and strategy.

It runs entirely in your terminal. All data is stored as plain markdown files on your machine. There is no cloud service, no account, no subscription, and no lock-in.

---

## The problem it solves

Technology leaders carry a particular kind of cognitive load. On any given day you might be:

- Tracking a dozen open tasks across multiple projects
- Waiting on decisions or deliverables from five different people
- Managing risks that could derail a quarter
- Preparing a status update for your manager
- Trying to remember what you actually accomplished this week

Most tools are built for one of these things. director_os is built for all of them, in one place, with minimal friction.

---

## How it works

When you open director_os, you see a single dashboard with everything that matters:

- **Tasks** — what you need to do, sorted by due date and priority
- **Dependencies** — what you're waiting on, who owns it, and how long it's been open
- **Risks** — what could go wrong, with severity and owner
- **Someday / Future** — ideas and future work that aren't active yet
- **Accomplishments** — a running log of what you've completed
- **Today** — your daily check-in at a glance

Everything is keyboard-driven. Adding a task, completing it, flagging it for your manager update, or moving it to someday are all single keystrokes.

---

## The manager update

One of the most useful features is the manager update generator. When you need to report out — to your manager, in a staff meeting, or in a written update — you open `:update`, set a since-date, and get a structured summary of:

- What you accomplished (with outcomes)
- What's in progress
- What you're waiting on
- Risks on the radar
- What got resolved

Items are always grouped by project. Each project section opens with a programmatic summary — open count, done count, and next due date — so the health of each initiative is visible at a glance. Human-readable project names and descriptions serve as headers. You control what surfaces in the update by flagging items with `M` (the manager flag). The update is written to a markdown file you can paste anywhere.

---

## Projects and tags

Any item — task, dependency, risk, accomplishment — can be tagged with a project and one or more tags. Projects are initiative anchors (e.g. `edp`, `bi_discovery`). Tags are cross-cutting work types (e.g. `deployment`, `planning`, `hiring`, `budgeting`). This lets you:

- Filter the entire dashboard to a single project with `]`/`[`
- Filter by tag with `f`/`F`
- See per-project health at a glance in the project manager (`:projects`)
- Get project-grouped manager updates automatically

Projects have display names and descriptions, so your update reads "Data Platform" instead of `edp`.

---

## Your data, your way

All data lives in monthly markdown log files in a directory you control. You can:

- Store them in a private git repo and sync with `G`
- Keep them in a cloud-synced folder (OneDrive, Dropbox, etc.)
- Read and edit them directly in any text editor
- Back them up however you like

There is no proprietary format. If you stop using director_os tomorrow, your data is still readable.

---

## Who it's for

director_os is opinionated about its audience. It's designed for people who:

- Live in the terminal and prefer keyboard-driven tools
- Manage work across multiple projects and stakeholders simultaneously
- Need to report status regularly and want that to be low-effort
- Value data ownership and simplicity over feature bloat
- Are comfortable with a little setup in exchange for a tool that fits exactly how they work

It is not a team tool. It is not a project management system. It is a personal operating system for a technology leader's working day.

---

## Compared to other tools

**Jira / Linear / Asana**
These are team tools. They're built for visibility across an organization — sprint boards, ticket queues, roadmaps. They're excellent at what they do, but they don't help you manage *your* work as a leader. Your tasks, your dependencies, your risks, your status updates live outside those systems. director_os fills that gap.

**Notion / Obsidian**
Flexible, powerful, and popular with people who like to build their own systems. The tradeoff is that you spend time building and maintaining the system instead of using it. director_os is opinionated by design — the structure is already there, and it's tuned for how technology leaders actually work.

**Todo apps (Things, Todoist, OmniFocus)**
Great for personal task management, but they don't model the things that matter most to a technology leader: dependencies with owners and ages, risks with severity, accomplishments that feed directly into status updates, or the relationship between work and the projects it belongs to.

**A spreadsheet or plain text file**
Honestly, not a bad choice — and director_os respects that instinct. The data is plain markdown, the structure is simple, and you can read it without the app. What director_os adds is a fast, keyboard-driven interface that makes capture and retrieval nearly frictionless, plus the manager update generator, which is the feature most likely to save you real time every week.

**Apple Notes / OneNote / Google Docs**
Useful for freeform capture, but not structured enough to query. You can't ask "what are all my open H-severity risks?" or "what did I accomplish on the Data Platform project this month?" director_os can answer both in seconds.
