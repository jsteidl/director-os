import re
from datetime import date
from models import Accomplishment
from parser._core import extract_tags, strip_tags, _clean, load_log, save_log


def _find_accomplishment_block(content, task_title):
    pattern = re.compile(r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n", re.S)
    for match in pattern.finditer(content):
        if strip_tags(re.sub(r"\s*\+[\w]+", "", match.group(1).replace(" Mgr:true", "").replace(" Personal:true", ""))).strip() == task_title:
            return match
    return None


def get_accomplishments():
    content = load_log()
    return [
        Accomplishment(
            task=strip_tags(re.sub(r"\s*\+[\w]+", "", task.replace(" Mgr:true", "").replace(" Personal:true", ""))),
            outcome=outcome,
            completed=completed,
            tags=extract_tags(task),
            mgr="Mgr:true" in task,
            personal="Personal:true" in task,
            project=re.search(r"\+([\w]+)", task).group(1) if re.search(r"\+([\w]+)", task) else None,
        )
        for task, outcome, completed in re.findall(
            r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n",
            content, re.MULTILINE,
        )
    ]


def add_accomplishment(task, outcome="", tags=None, project=""):
    content = load_log()
    task = _clean(task)
    project_str = f" +{project}" if project else ""
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""
    block = (
        f"- Task: {task}{project_str}{tag_str}\n"
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
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""
    project_str = f" +{project}" if project else ""
    new_block = (
        f"- Task: {new_task}{project_str}{tag_str}\n"
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
        if strip_tags(raw.replace(" Mgr:true", "")).strip() == task_title:
            new_raw = raw.replace(" Mgr:true", "") if "Mgr:true" in raw else raw + " Mgr:true"
            new_block = match.group(0).replace(raw, new_raw, 1)
            content = content.replace(match.group(0), new_block, 1)
            save_log(content)
            return


def toggle_personal_accomplishment(task_title):
    content = load_log()
    pattern = re.compile(r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n", re.S)
    for match in pattern.finditer(content):
        raw = match.group(1)
        if strip_tags(raw.replace(" Mgr:true", "").replace(" Personal:true", "")).strip() == task_title:
            new_raw = raw.replace(" Personal:true", "") if "Personal:true" in raw else raw + " Personal:true"
            new_block = match.group(0).replace(raw, new_raw, 1)
            content = content.replace(match.group(0), new_block, 1)
            save_log(content)
            return
