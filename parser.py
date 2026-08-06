import re
from datetime import datetime, date
from pathlib import Path
from models import Task, Dependency, Accomplishment, ResolvedDependency, DailyLogEntry


# ==========================================================
# FILE HELPERS
# ==========================================================

def get_log_file():

    filename = (
        f"{date.today():%Y-%m}-Director-Log.md"
    )

    return (
        Path(__file__).parent
        / "logs"
        / filename
    )


def get_prev_log_file():

    today = date.today()

    if today.month == 1:
        prev = today.replace(year=today.year - 1, month=12, day=1)
    else:
        prev = today.replace(month=today.month - 1, day=1)

    filename = f"{prev:%Y-%m}-Director-Log.md"

    return (
        Path(__file__).parent
        / "logs"
        / filename
    )


def scaffold_log(path):

    month_label = date.today().strftime("%B %Y")

    template = f"""# {month_label}

## Active To-Dos

### High-Priority

### Waiting On

### Resolved Dependencies

### Someday/Future

### Risks

### Accomplishments

### Wins Worth Mentioning

### Daily Log
"""

    path.write_text(template, encoding="utf-8")


def rollover_log():

    current = get_log_file()
    previous = get_prev_log_file()

    if not previous.exists():
        scaffold_log(current)
        return

    prev_content = previous.read_text(encoding="utf-8")

    # Carry over incomplete tasks
    task_match = re.search(
        r"### High-Priority(.*?)### Waiting On",
        prev_content,
        re.S,
    )

    carried_tasks = ""

    if task_match:
        carried_tasks = "\n".join(
            line for line in task_match.group(1).splitlines()
            if re.match(r"- \[ \]", line.strip())
        )

    # Carry over open dependencies
    dep_matches = re.findall(
        r"- (.*?) \| Owner: (.*?) \| Since: (\d{4}-\d{2}-\d{2})",
        prev_content,
    )

    carried_deps = "\n".join(
        f"- {item} | Owner: {owner} | Since: {since}"
        for item, owner, since in dep_matches
    )

    scaffold_log(current)

    content = current.read_text(encoding="utf-8")

    if carried_tasks:
        content = content.replace(
            "### High-Priority\n",
            f"### High-Priority\n{carried_tasks}\n",
            1,
        )

    if carried_deps:
        content = content.replace(
            "### Waiting On\n",
            f"### Waiting On\n{carried_deps}\n",
            1,
        )

    current.write_text(content, encoding="utf-8")


def load_log():

    path = get_log_file()

    if not path.exists():
        rollover_log()

    return path.read_text(
        encoding="utf-8"
    )


def save_log(content):

    get_log_file().write_text(
        content,
        encoding="utf-8"
    )


# ==========================================================
# TASKS
# ==========================================================

def get_tasks():

    content = load_log()

    match = re.search(
        r"### High-Priority(.*?)### Waiting On",
        content,
        re.S,
    )

    if not match:
        return []

    tasks = []

    for title in re.findall(
        r"- \[ \] (.*)",
        match.group(1),
    ):
        priority = None
        due_date = None
        due_match = re.search(
            r"Due:(\d{4}-\d{2}-\d{2})",
            title,
        )
        if due_match:
            due_date = due_match.group(1)
            title = title.replace(
                f" Due:{due_date}", ""
            ).strip()

        priority_match = re.match(r"^\(([ABC])\)\s+(.*)$", title)

        if priority_match:
            priority = priority_match.group(1)
            title = priority_match.group(2)

        tasks.append(
            Task(
                title=title,
                priority=priority,
                due_date=due_date,
            )
        )
    return tasks


def add_task(task_name, tag="", due_date="", priority=""):

    content = load_log()

    title = f"({priority}) {task_name}" if priority else task_name

    line = f"- [ ] {title}"

    if due_date:
        line += f" Due:{due_date}"

    if tag:
        line += f" #{tag}"

    line += "\n"

    marker = "### High-Priority\n"

    content = content.replace(
        marker,
        marker + line,
        1,
    )

    save_log(content)


# ==========================================================
# DEPENDENCIES
# ==========================================================


def get_dependencies():

    content = load_log()

    matches = re.findall(
        r"- (.*?) \| Owner: (.*?) \| Since: (\d{4}-\d{2}-\d{2})",
        content,
    )

    dependencies = []

    for item, owner, since in matches:

        since_date = datetime.strptime(
            since,
            "%Y-%m-%d"
        ).date()

        age = (
            date.today() - since_date
        ).days

        dependencies.append(
            Dependency(
                item,
                owner,
                since,
                age,
            )
        )

    return dependencies


def add_dependency(
    item,
    owner,
):

    content = load_log()

    line = (
        f"- {item} | Owner: {owner} "
        f"| Since: {date.today()}\n"
    )

    marker = "### Waiting On\n"

    content = content.replace(
        marker,
        marker + line,
        1,
    )

    save_log(content)

def resolve_dependency(
    dependency_name,
    resolution_notes,
):

    content = load_log()

    pattern = (
        r"- (.*?) \| Owner: (.*?) "
        r"\| Since: (\d{4}-\d{2}-\d{2})"
    )

    matches = re.findall(
        pattern,
        content,
    )

    target = None

    for item, owner, since in matches:

        if item == dependency_name:

            target = (
                item,
                owner,
                since,
            )

            break

    if not target:
        return

    item, owner, since = target

    original_line = (
        f"- {item} | Owner: {owner} | Since: {since}"
    )

    content = content.replace(
        original_line,
        "",
        1,
    )

    resolved_entry = (
        f"- Dependency: {item}\n"
        f"  Owner: {owner}\n"
        f"  Resolved: {date.today()}\n"
        f"  Notes: {resolution_notes}\n\n"
    )

    content = content.replace(
        "### Someday/Future",
        resolved_entry +
        "### Someday/Future",
        1,
    )

    save_log(content)


# ==========================================================
# ACCOMPLISHMENTS
# ==========================================================

def get_accomplishments():

    content = load_log()

    pattern = (
        r"- Task: (.*?)\n"
        r"  Outcome: (.*?)\n"
        r"  Completed: (.*?)\n"
    )

    matches = re.findall(
        pattern,
        content,
        re.MULTILINE,
    )

    return [
        Accomplishment(
            task,
            outcome,
            completed,
        )
        for task, outcome, completed in matches
    ]


# ==========================================================
# COMPLETE TASK
# ==========================================================

def complete_task(
    task_text,
    outcome,
):

    content = load_log()

    task_line = (
        f"- [ ] {task_text}"
    )

    content = content.replace(
        task_line,
        "",
        1,
    )

    accomplishment = (
        f"- Task: {task_text}\n"
        f"  Outcome: {outcome}\n"
        f"  Completed: {date.today()}\n\n"
    )

    content = content.replace(
        "### Wins Worth Mentioning",
        accomplishment +
        "### Wins Worth Mentioning",
        1,
    )

    save_log(content)


# ==========================================================
# REOPEN TASK
# ==========================================================

def reopen_task(task_title):

    content = load_log()

    pattern = (
        r"- Task: (.*?)\n"
        r"  Outcome: (.*?)\n"
        r"  Completed: (.*?)\n\n"
    )

    matches = list(
        re.finditer(
            pattern,
            content,
            re.MULTILINE,
        )
    )

    target = None

    for match in matches:

        if match.group(1) == task_title:
            target = match
            break

    if not target:
        return

    content = content.replace(
        target.group(0),
        "",
        1,
    )

    content = content.replace(
        "### High-Priority\n",
        f"### High-Priority\n- [ ] {task_title}\n",
        1,
    )

    save_log(content)


# ==========================================================
# DAILY ENTRY
# ==========================================================

def add_daily_entry(
    priorities,
    accomplished,
    blocked,
    notes,
):

    content = load_log()

    today = date.today().isoformat()

    entry = f"""

#### {today}

##### Priorities

{to_markdown_list(priorities)}

##### Accomplished

{to_markdown_list(accomplished)}

##### Blocked

{to_markdown_list(blocked)}

##### Notes

{to_markdown_list(notes)}


"""

    content += entry

    save_log(content)

    return True

def to_markdown_list(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(
        f"- {line}"
        for line in lines
    )
def parse_daily_log(content):
    """Parse Daily Log entries into DailyLogEntry objects."""

    entries = []

    current_entry = None
    current_section = None

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # --------------------------------------------------
        # Date Header
        # Example:
        # #### 2026-08-05
        # --------------------------------------------------
        if line.startswith("#### ") and not line.startswith("#####"):
            date_text = line.replace("#### ", "").strip()

            current_entry = DailyLogEntry(
                date=date_text,
                priorities=[],
                accomplished=[],
                blocked=[],
                notes=[],
            )

            entries.append(current_entry)
            current_section = None
            continue

        # --------------------------------------------------
        # Section Header
        # Example:
        # ##### Priorities
        # --------------------------------------------------
        if line.startswith("##### "):
            current_section = (
                line.replace("##### ", "")
                .strip()
                .lower()
            )
            continue

        # --------------------------------------------------
        # List Item
        # Example:
        # - Review roadmap
        # --------------------------------------------------
        if (
            line.startswith("- ")
            and current_entry is not None
            and current_section is not None
        ):
            item = line[2:].strip()

            if current_section == "priorities":
                current_entry.priorities.append(item)

            elif current_section == "accomplished":
                current_entry.accomplished.append(item)

            elif current_section == "blocked":
                current_entry.blocked.append(item)

            elif current_section == "notes":
                current_entry.notes.append(item)

    # Newest first
    entries.sort(
        key=lambda entry: entry.date,
        reverse=True,
    )

    return entries
# ==========================================================
# DAILY LOG VIEWER
# ==========================================================

def get_daily_log_text():

    content = load_log()

    marker = "### Daily Log"

    if marker not in content:
        return "No daily log entries found."

    log_text = content.split(
        marker,
        1
    )[1].strip()

    return (
        "DAILY LOG\n"
        "=========\n\n"
        + log_text
    )