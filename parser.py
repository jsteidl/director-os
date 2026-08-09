import re
import tomllib
from datetime import datetime, date
from pathlib import Path
from models import Task, Dependency, Accomplishment, ResolvedDependency, DailyLogEntry, Risk, SomedayItem, Event


def _get_logs_path() -> Path:
    config_path = Path(__file__).parent / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        logs_path = config.get("logs_path", "logs")
        p = Path(logs_path)
        return p if p.is_absolute() else Path(__file__).parent / p
    return Path(__file__).parent / "logs"


# ==========================================================
# TAG HELPERS
# ==========================================================

def extract_tags(text):
    return re.findall(r"#+([\w]+)", text)


def strip_tags(text):
    return re.sub(r"\s*#+\S+", "", text).strip()


def _clean(text: str) -> str:
    return text.replace("|", "").strip()


# ==========================================================
# FILE HELPERS
# ==========================================================

def get_log_file():
    filename = f"{date.today():%Y-%m}-Director-Log.md"
    return _get_logs_path() / filename


def get_prev_log_file():
    today = date.today()
    if today.month == 1:
        prev = today.replace(year=today.year - 1, month=12, day=1)
    else:
        prev = today.replace(month=today.month - 1, day=1)
    return _get_logs_path() / f"{prev:%Y-%m}-Director-Log.md"


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
            line + " Carried:true" if not line.strip().endswith("Carried:true") else line
            for line in task_match.group(1).splitlines()
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

    return path.read_text(encoding="utf-8")


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
        created = None
        due_match = re.search(
            r"Due:(\d{4}-\d{2}-\d{2})",
            title,
        )
        if due_match:
            due_date = due_match.group(1)
            title = title.replace(
                f" Due:{due_date}", ""
            ).strip()

        created_match = re.search(
            r"Created:(\d{4}-\d{2}-\d{2})",
            title,
        )
        if created_match:
            created = created_match.group(1)
            title = title.replace(
                f" Created:{created}", ""
            ).strip()

        carried = "Carried:true" in title
        if carried:
            title = title.replace(" Carried:true", "").strip()

        priority_match = re.match(r"^\(([ABC])\)\s+(.*)$", title)

        if priority_match:
            priority = priority_match.group(1)
            title = priority_match.group(2)

        tags = extract_tags(title)
        title = strip_tags(title)

        tasks.append(
            Task(
                title=title,
                priority=priority,
                due_date=due_date,
                created=created,
                tags=tags,
                carried=carried,
            )
        )
    priority_order = {"A": 0, "B": 1, "C": 2, None: 3}
    tasks.sort(key=lambda t: (
        (0, t.due_date) if t.due_date else (1, ""),
        priority_order.get(t.priority, 3),
    ))
    return tasks


def add_task(task_name, tag="", due_date="", priority=""):

    content = load_log()

    task_name = _clean(task_name)
    title = f"({priority}) {task_name}" if priority else task_name

    line = f"- [ ] {title}"

    if due_date:
        line += f" Due:{due_date}"

    line += f" Created:{date.today()}"

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


def edit_task(old_title, new_title, priority="", due_date="", tags=None):

    content = load_log()

    new_title = _clean(new_title)
    search_text = old_title.rstrip("…")
    pattern = re.compile(r"- \[ \] .*" + re.escape(search_text) + r".*")
    match = pattern.search(content)

    if not match:
        return

    created_match = re.search(r"Created:(\d{4}-\d{2}-\d{2})", match.group(0))
    created = created_match.group(1) if created_match else date.today().isoformat()

    new_line_title = f"({priority}) {new_title}" if priority else new_title
    new_line = f"- [ ] {new_line_title}"

    if due_date:
        new_line += f" Due:{due_date}"

    new_line += f" Created:{created}"

    if tags:
        new_line += " " + " ".join(f"#{t}" for t in tags)

    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_task(task_title):

    content = load_log()

    search_text = task_title.rstrip("…")
    pattern = re.compile(r"- \[ \] .*" + re.escape(search_text) + r".*\n")
    content = pattern.sub("", content, count=1)
    save_log(content)


# ==========================================================
# DEPENDENCIES
# ==========================================================


def get_dependencies():

    content = load_log()

    match = re.search(
        r"### Waiting On(.*?)### Resolved Dependencies",
        content,
        re.S,
    )

    if not match:
        return []

    matches = re.findall(
        r"- (.*?) \| Owner:\s*(.*?) \| Since:\s*(\d{4}-\d{2}-\d{2})",
        match.group(1),
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

        tags = extract_tags(item)
        clean_item = strip_tags(item)

        dependencies.append(
            Dependency(
                clean_item,
                owner,
                since,
                age,
                tags,
            )
        )

    return dependencies


def add_dependency(
    item,
    owner,
):

    content = load_log()

    item, owner = _clean(item), _clean(owner)

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


def edit_dependency(old_item, new_item, owner):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(old_item) + r" \| Owner:\s*.*? \| Since:\s*(\d{4}-\d{2}-\d{2}).*"
    )
    match = pattern.search(content)

    if not match:
        return

    since = match.group(1)
    new_item, owner = _clean(new_item), _clean(owner)
    new_line = f"- {new_item} | Owner: {owner} | Since: {since}"
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_dependency(item_text):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(item_text) + r" \| Owner:\s*.*? \| Since:\s*\d{4}-\d{2}-\d{2}.*\n"
    )
    content = pattern.sub("", content, count=1)
    save_log(content)

def resolve_dependency(
    dependency_name,
    resolution_notes,
):

    content = load_log()

    pattern = (
        r"- (.*?) \| Owner:\s*(.*?) "
        r"\| Since:\s*(\d{4}-\d{2}-\d{2})"
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
# RISKS
# ==========================================================

def get_risks():

    content = load_log()

    match = re.search(
        r"### Risks(.*?)###",
        content,
        re.S,
    )

    if not match:
        return []

    risks = []

    for line in re.findall(
        r"- (.*?) \| Owner:\s*(.*?) \| Since:\s*(\d{4}-\d{2}-\d{2}) \| Severity:\s*([HML])(.*)",
        match.group(1),
    ):
        description, owner, since, severity, rest = line
        tags = extract_tags(rest)

        risks.append(
            Risk(
                description=description,
                owner=owner,
                since=since,
                severity=severity,
                tags=tags,
            )
        )

    return risks


def add_risk(description, owner, severity, tags=None):

    content = load_log()

    description, owner = _clean(description), _clean(owner)

    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""

    line = (
        f"- {description} | Owner: {owner} "
        f"| Since: {date.today()} "
        f"| Severity: {severity.upper()}{tag_str}\n"
    )

    content = content.replace(
        "### Risks\n",
        f"### Risks\n{line}",
        1,
    )

    save_log(content)


def edit_risk(old_description, new_description, owner, severity, tags=None):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(old_description) + r" \| Owner:\s*.*? \| Since:\s*(\d{4}-\d{2}-\d{2}) \| Severity:\s*[HML].*"
    )
    match = pattern.search(content)

    if not match:
        return

    since = match.group(1)
    new_description, owner = _clean(new_description), _clean(owner)
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""
    new_line = (
        f"- {new_description} | Owner: {owner} "
        f"| Since: {since} "
        f"| Severity: {severity.upper()}{tag_str}"
    )
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_risk(description):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(description) + r" \| Owner:\s*.*? \| Since:\s*\d{4}-\d{2}-\d{2} \| Severity:\s*[HML].*\n"
    )
    content = pattern.sub("", content, count=1)
    save_log(content)


def resolve_risk(description, notes):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(description) + r" \| Owner:\s*(.*?) \| Since:\s*(\d{4}-\d{2}-\d{2}) \| Severity:\s*([HML]).*"
    )
    match = pattern.search(content)

    if not match:
        return

    content = pattern.sub("", content, count=1)

    resolved_entry = (
        f"- Risk: {description}\n"
        f"  Owner: {match.group(1)}\n"
        f"  Severity: {match.group(3)}\n"
        f"  Resolved: {date.today()}\n"
        f"  Notes: {notes}\n\n"
    )

    content = content.replace(
        "### Accomplishments\n",
        resolved_entry + "### Accomplishments\n",
        1,
    )
    save_log(content)


# ==========================================================
# SOMEDAY / FUTURE
# ==========================================================

def get_someday_items():

    content = load_log()

    match = re.search(
        r"### Someday/Future(.*?)### Risks",
        content,
        re.S,
    )

    if not match:
        return []

    items = []

    for line in re.findall(
        r"- (.*?) \| Owner:\s*(.*?) \| Since: (\d{4}-\d{2}-\d{2})(.*)",
        match.group(1),
    ):
        item, owner, since, rest = line
        tags = extract_tags(rest)

        items.append(
            SomedayItem(
                item=item,
                owner=owner,
                since=since,
                tags=tags,
            )
        )

    return items


def add_someday_item(item, owner, tags=None):

    content = load_log()

    item, owner = _clean(item), _clean(owner)

    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""

    line = (
        f"- {item} | Owner: {owner} "
        f"| Since: {date.today()}{tag_str}\n"
    )

    content = content.replace(
        "### Someday/Future\n",
        f"### Someday/Future\n{line}",
        1,
    )

    save_log(content)


def edit_someday_item(old_item, new_item, owner, tags=None):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(old_item) + r" \| Owner:\s*.*? \| Since:\s*(\d{4}-\d{2}-\d{2}).*"
    )
    match = pattern.search(content)

    if not match:
        return

    since = match.group(1)
    new_item, owner = _clean(new_item), _clean(owner)
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""
    new_line = f"- {new_item} | Owner: {owner} | Since: {since}{tag_str}"
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_someday_item(item_text):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(item_text) + r" \| Owner:\s*.*? \| Since:\s*\d{4}-\d{2}-\d{2}.*\n"
    )
    content = pattern.sub("", content, count=1)
    save_log(content)


def promote_someday_item(item_text, priority="", due_date="", tags=None):

    content = load_log()

    pattern = (
        r"- (.*?) \| Owner: (.*?) \| Since: (\d{4}-\d{2}-\d{2})(.*)"
    )

    for line in re.findall(pattern, content):
        item, owner, since, rest = line
        if item == item_text:
            original = f"- {item} | Owner: {owner} | Since: {since}{rest}"
            content = content.replace(original + "\n", "", 1)

            title = f"({priority}) {item_text}" if priority else item_text
            task_line = f"- [ ] {title}"
            if due_date:
                task_line += f" Due:{due_date}"
            task_line += f" Created:{date.today()}"
            if tags:
                task_line += " " + " ".join(f"#{t}" for t in tags)

            content = content.replace(
                "### High-Priority\n",
                f"### High-Priority\n{task_line}\n",
                1,
            )
            save_log(content)
            return


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
            task=strip_tags(task),
            outcome=outcome,
            completed=completed,
            tags=extract_tags(task),
        )
        for task, outcome, completed in matches
    ]


def _find_accomplishment_block(content, task_title):
    """Find accomplishment block where stripped task title matches."""
    pattern = re.compile(
        r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n",
        re.S,
    )
    for match in pattern.finditer(content):
        if strip_tags(match.group(1)).strip() == task_title:
            return match
    return None


def edit_accomplishment(old_task, new_task, outcome):

    content = load_log()
    match = _find_accomplishment_block(content, old_task)

    if not match:
        return

    completed = match.group(3)
    new_block = (
        f"- Task: {new_task}\n"
        f"  Outcome: {outcome}\n"
        f"  Completed: {completed}\n"
    )
    content = content.replace(match.group(0), new_block, 1)
    save_log(content)


def delete_accomplishment(task_title):

    content = load_log()
    match = _find_accomplishment_block(content, task_title)

    if not match:
        return

    # Remove the block plus the trailing blank line
    full_block = re.compile(
        re.escape(match.group(0)) + r"\n?"
    )
    content = full_block.sub("", content, count=1)
    save_log(content)


# ==========================================================
# COMPLETE TASK
# ==========================================================

def complete_task(
    task_text,
    outcome,
):

    content = load_log()

    search_text = task_text.rstrip("…")
    pattern = re.compile(r"- \[ \] .*" + re.escape(search_text) + r".*\n")
    content = pattern.sub("", content, count=1)

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

        if strip_tags(match.group(1)).strip() == task_title:
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


def edit_daily_entry(entry_date, priorities, accomplished, blocked, notes):

    content = load_log()

    pattern = re.compile(
        r"#### " + re.escape(entry_date) + r".*?(?=\n#### |\Z)",
        re.S,
    )

    new_entry = f"""#### {entry_date}

##### Priorities

{to_markdown_list(priorities)}

##### Accomplished

{to_markdown_list(accomplished)}

##### Blocked

{to_markdown_list(blocked)}

##### Notes

{to_markdown_list(notes)}

"""

    content = pattern.sub(new_entry, content, count=1)
    save_log(content)

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

def get_all_daily_entries():
    """Return all DailyLogEntry objects across all monthly log files, newest first."""
    logs_path = _get_logs_path()
    entries = []
    current_file = get_log_file()
    for path in sorted(logs_path.glob("*-Director-Log.md"), reverse=True):
        content = path.read_text(encoding="utf-8")
        file_entries = parse_daily_log(content)
        for entry in file_entries:
            entry._readonly = (path != current_file)
        entries.extend(file_entries)
    entries.sort(key=lambda e: e.date, reverse=True)
    return entries


def get_today_entry():
    """Return today's DailyLogEntry or None."""

    content = load_log()
    today = date.today().isoformat()
    entries = parse_daily_log(content)

    for entry in entries:
        if entry.date == today:
            return entry

    return None


def get_metrics():

    today = date.today()
    tasks = get_tasks()
    deps = get_dependencies()
    risks = get_risks()
    accomplishments = get_accomplishments()

    overdue = sum(
        1 for t in tasks
        if t.due_date and datetime.strptime(t.due_date, "%Y-%m-%d").date() < today
    )

    oldest_dep = max((d.age for d in deps), default=0)

    oldest_task = max(
        ((today - datetime.strptime(t.created, "%Y-%m-%d").date()).days
         for t in tasks if t.created),
        default=0
    )

    high_risks = sum(1 for r in risks if r.severity.upper() == "H")

    month_wins = sum(
        1 for a in accomplishments
        if a.completed.startswith(today.strftime("%Y-%m"))
    )

    return {
        "tasks": len(tasks),
        "overdue": overdue,
        "deps": len(deps),
        "oldest_dep": oldest_dep,
        "oldest_task": oldest_task,
        "high_risks": high_risks,
        "accomplishments": len(accomplishments),
        "month_wins": month_wins,
    }


def get_all_tags():
    """Return sorted list of unique tags across all objects."""
    tags = set()
    for t in get_tasks():
        tags.update(t.tags)
    for d in get_dependencies():
        tags.update(d.tags)
    for r in get_risks():
        tags.update(r.tags)
    for s in get_someday_items():
        tags.update(s.tags)
    for a in get_accomplishments():
        tags.update(a.tags)
    return sorted(tags, key=str.lower)


def rename_tag(old_tag, new_tag):
    """Rename all occurrences of #old_tag to #new_tag in the log file."""
    path = get_log_file()
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"#" + re.escape(old_tag) + r"\b", f"#{new_tag}", content)
    path.write_text(content, encoding="utf-8")


def get_update_data(since_date: str) -> dict:
    tasks = get_tasks()
    all_accomplishments = []
    for path in sorted(_get_logs_path().glob("*-Director-Log.md")):
        content = path.read_text(encoding="utf-8")
        pattern = (
            r"- Task: (.*?)\n"
            r"  Outcome: (.*?)\n"
            r"  Completed: (.*?)\n"
        )
        for task, outcome, completed in re.findall(pattern, content, re.MULTILINE):
            all_accomplishments.append(Accomplishment(
                task=strip_tags(task),
                outcome=outcome,
                completed=completed,
                tags=extract_tags(task),
            ))
    accomplishments = [a for a in all_accomplishments if a.completed >= since_date]
    deps = get_dependencies()
    risks = [r for r in get_risks() if r.severity.upper() == "H"]
    entries = [e for e in get_all_daily_entries() if e.date >= since_date]
    blocked = [(e.date, b) for e in entries for b in e.blocked]
    return {
        "since": since_date,
        "accomplished": accomplishments,
        "tasks": tasks,
        "deps": deps,
        "risks": risks,
        "blocked": blocked,
    }


def save_update(since_date: str, data: dict) -> str:
    lines = []
    lines.append(f"## Update — Since {since_date}\n")

    lines.append("### Accomplished")
    if data["accomplished"]:
        for a in data["accomplished"]:
            lines.append(f"- {a.task}")
    else:
        lines.append("- Nothing completed in this period")

    lines.append("\n### In Progress")
    if data["tasks"]:
        for t in data["tasks"]:
            from widgets.tasks import PRIORITY_GLYPHS
            glyph = PRIORITY_GLYPHS.get(t.priority, "") + " " if t.priority else ""
            due = f" (due {t.due_date})" if t.due_date else ""
            lines.append(f"- {glyph}{t.title}{due}")
    else:
        lines.append("- No open tasks")

    lines.append("\n### Waiting On")
    if data["deps"]:
        for d in data["deps"]:
            lines.append(f"- {d.item} — {d.owner} ({d.age}d)")
    else:
        lines.append("- Nothing pending")

    lines.append("\n### Risks")
    if data["risks"]:
        for r in data["risks"]:
            lines.append(f"- {r.description} (owner: {r.owner})")
    else:
        lines.append("- No high severity risks")

    lines.append("\n### Blocked / Notes")
    if data["blocked"]:
        seen = set()
        for d, b in data["blocked"]:
            if b not in seen:
                seen.add(b)
                lines.append(f"- {b} ({d})")
    else:
        lines.append("- Nothing blocked")

    content = "\n".join(lines) + "\n"
    filename = f"update-{date.today().isoformat()}.md"
    updates_dir = _get_logs_path() / "updates"
    updates_dir.mkdir(exist_ok=True)
    path = updates_dir / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


def get_weekly_summary():

    today = date.today()
    week_start = today - __import__('datetime').timedelta(days=today.weekday())
    week_ago = week_start
    content = load_log()
    entries = parse_daily_log(content)

    week_entries = [e for e in entries if e.date >= week_ago.isoformat()]

    accomplishments = [
        a for a in get_accomplishments()
        if a.completed >= week_ago.isoformat()
    ]

    tasks = get_tasks()

    return {
        "entries": week_entries,
        "accomplishments": accomplishments,
        "open_tasks": tasks,
        "week_start": week_ago.isoformat(),
        "week_end": today.isoformat(),
    }


def save_weekly_review(notes, week_start, week_end):

    content = load_log()

    entry = (
        f"\n\n#### Weekly Review: {week_start} to {week_end}\n\n"
        f"##### Notes\n\n"
        f"{to_markdown_list(notes)}\n"
    )

    content += entry
    save_log(content)


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


# ==========================================================
# EVENTS
# ==========================================================

def get_events_file():
    return _get_logs_path() / "events.md"


def get_events() -> list:
    path = get_events_file()
    if not path.exists():
        path.write_text("# Events\n\n", encoding="utf-8")
    content = path.read_text(encoding="utf-8")
    events = []
    for m in re.finditer(
        r"- (.*?) \| Date: (\d{4}-\d{2}-\d{2}) \| Type: (.*?) \| Location: (.*?) \| RemindDays: (\d+)",
        content,
    ):
        events.append(Event(
            title=m.group(1),
            date=m.group(2),
            type=m.group(3),
            location=m.group(4),
            remind_days=int(m.group(5)),
        ))
    return events


def add_event(title, event_date, type_, location, remind_days=0):
    path = get_events_file()
    content = path.read_text(encoding="utf-8")
    title, location = _clean(title), _clean(location)
    line = f"- {title} | Date: {event_date} | Type: {type_} | Location: {location} | RemindDays: {remind_days}\n"
    content += line
    path.write_text(content, encoding="utf-8")


def edit_event(old_title, old_date, title, event_date, type_, location, remind_days=0):
    path = get_events_file()
    content = path.read_text(encoding="utf-8")
    title, location = _clean(title), _clean(location)
    pattern = re.compile(
        r"- " + re.escape(old_title) + r" \| Date: " + re.escape(old_date) + r" \| Type: .*? \| Location: .*? \| RemindDays: \d+\n"
    )
    new_line = f"- {title} | Date: {event_date} | Type: {type_} | Location: {location} | RemindDays: {remind_days}\n"
    content = pattern.sub(new_line, content, count=1)
    path.write_text(content, encoding="utf-8")


def delete_event(title, event_date):
    path = get_events_file()
    content = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"- " + re.escape(title) + r" \| Date: " + re.escape(event_date) + r" \| Type: .*? \| Location: .*? \| RemindDays: \d+\n"
    )
    content = pattern.sub("", content, count=1)
    path.write_text(content, encoding="utf-8")


def check_event_notifications():
    """Append event/reminder notations to today's daily log if not already present."""
    today = date.today()
    events = get_events()
    notes_to_add = []

    for e in events:
        try:
            event_date = datetime.strptime(e.date, "%Y-%m-%d").date()
        except ValueError:
            continue
        days_away = (event_date - today).days
        if days_away == 0:
            notes_to_add.append(f"[Event] {e.title} ({e.type}, {e.location})")
        elif 0 < days_away <= e.remind_days:
            notes_to_add.append(f"[Reminder] {e.title} in {days_away}d ({e.type}, {e.location})")

    if not notes_to_add:
        return

    content = load_log()
    today_str = today.isoformat()

    for note in notes_to_add:
        # Skip if already present
        if note in content:
            continue
        # If today's entry exists, append to its Notes section
        pattern = re.compile(
            r"(#### " + re.escape(today_str) + r".*?##### Notes\n)(.*?)(?=\n#### |\Z)",
            re.S,
        )
        match = pattern.search(content)
        if match:
            content = content[:match.end(2)] + f"- {note}\n" + content[match.end(2):]
        else:
            # No entry yet — create a minimal one
            entry = (
                f"\n\n#### {today_str}\n\n"
                f"##### Priorities\n\n"
                f"##### Accomplished\n\n"
                f"##### Blocked\n\n"
                f"##### Notes\n\n"
                f"- {note}\n"
            )
            content += entry

    save_log(content)
