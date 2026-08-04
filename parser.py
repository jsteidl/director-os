import re
from datetime import date
from pathlib import Path


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

    get_log_file().write_text(
        content,
        encoding="utf-8",
    )


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
        accomplishment
        + "### Wins Worth Mentioning",
        1,
    )

    get_log_file().write_text(
        content,
        encoding="utf-8",
    )


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

    get_log_file().write_text(
        content,
        encoding="utf-8",
    )