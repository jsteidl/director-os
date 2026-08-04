import re
from datetime import date
from pathlib import Path


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


def load_log():

    path = get_log_file()

    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8"
    )


def save_log(content):

    get_log_file().write_text(
        content,
        encoding="utf-8"
    )


# ==========================================================
# MODELS
# ==========================================================

class Task:

    def __init__(self, title):
        self.title = title


class Dependency:

    def __init__(
        self,
        item,
        owner,
        since,
    ):
        self.item = item
        self.owner = owner
        self.since = since


class Accomplishment:

    def __init__(
        self,
        task,
        outcome,
        completed,
    ):
        self.task = task
        self.outcome = outcome
        self.completed = completed


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

    return [
        Task(title)
        for title in re.findall(
            r"- \[ \] (.*)",
            match.group(1),
        )
    ]


def add_task(task_name, tag=""):

    content = load_log()

    line = f"- [ ] {task_name}"

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

    return [
        Dependency(
            item,
            owner,
            since,
        )
        for item, owner, since in matches
    ]


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