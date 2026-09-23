import re
from datetime import date
from models import Accomplishment
from parser._core import extract_tags, _clean, load_log, save_log


def _strip_pipe_fields(text):
    return re.sub(r"\s*\|.*", "", text).strip()


def _find_accomplishment_block(content, task_title):
    pattern = re.compile(r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n", re.S)
    for match in pattern.finditer(content):
        if _strip_pipe_fields(match.group(1)) == task_title:
            return match
    return None


def get_accomplishments():
    content = load_log()
    results = []
    for task, outcome, completed in re.findall(
        r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n",
        content, re.MULTILINE,
    ):
        parts = [p.strip() for p in task.split(" | ")]
        fields = {}
        for p in parts[1:]:
            if ": " in p:
                k, v = p.split(": ", 1)
                fields[k] = v
        results.append(Accomplishment(
            task=parts[0],
            outcome=outcome,
            completed=completed,
            tags=extract_tags(task),
            mgr=fields.get("Mgr") == "true",
            personal=fields.get("Personal") == "true",
            project=fields.get("Project"),
        ))
    return results


def _build_task_header(task, mgr=False, personal=False, project="", tags=None):
    line = task
    if mgr:
        line += " | Mgr: true"
    if personal:
        line += " | Personal: true"
    if project:
        line += f" | Project: {project}"
    if tags:
        line += f" | Tags: {' '.join(tags)}"
    return line


def add_accomplishment(task, outcome="", tags=None, project=""):
    content = load_log()
    header = _build_task_header(_clean(task), project=project, tags=tags)
    block = (
        f"- Task: {header}\n"
        f"  Outcome: {outcome}\n"
        f"  Completed: {date.today()}\n\n"
    )
    content = content.replace("### Wins Worth Mentioning", block + "### Wins Worth Mentioning", 1)
    save_log(content)


def edit_accomplishment(old_task, new_task, outcome, tags=None, project=""):
    content = load_log()
    match = _find_accomplishment_block(content, old_task)
    if not match:
        return
    completed = match.group(3)
    header = _build_task_header(new_task, project=project, tags=tags)
    new_block = (
        f"- Task: {header}\n"
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
    full_block = re.compile(re.escape(match.group(0)) + r"\n?")
    content = full_block.sub("", content, count=1)
    save_log(content)


def toggle_mgr_accomplishment(task_title):
    content = load_log()
    pattern = re.compile(r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n", re.S)
    for match in pattern.finditer(content):
        raw = match.group(1)
        if _strip_pipe_fields(raw) == task_title:
            if " | Mgr: true" in raw:
                new_raw = raw.replace(" | Mgr: true", "")
            else:
                new_raw = raw + " | Mgr: true"
            content = content.replace(match.group(0), match.group(0).replace(raw, new_raw, 1), 1)
            save_log(content)
            return


def toggle_personal_accomplishment(task_title):
    content = load_log()
    pattern = re.compile(r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n", re.S)
    for match in pattern.finditer(content):
        raw = match.group(1)
        if _strip_pipe_fields(raw) == task_title:
            if " | Personal: true" in raw:
                new_raw = raw.replace(" | Personal: true", "")
            else:
                new_raw = raw + " | Personal: true"
            content = content.replace(match.group(0), match.group(0).replace(raw, new_raw, 1), 1)
            save_log(content)
            return
