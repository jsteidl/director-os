import re
from datetime import date
from models import Task
from parser._core import _clean, load_log, save_log


def _parse_task_line(line) -> Task:
    parts = [p.strip() for p in line.split(" | ")]
    title_part = parts[0]
    fields = {k.strip(): v.strip() for k, v in (p.split(":", 1) for p in parts[1:] if ":" in p)}

    priority_match = re.match(r"^\(([ABC])\)\s+(.*)", title_part)
    if priority_match:
        priority = priority_match.group(1)
        title = priority_match.group(2)
    else:
        priority = None
        title = title_part

    return Task(
        title=title,
        priority=priority,
        due_date=fields.get("Due"),
        created=fields.get("Created"),
        carried=fields.get("Carried", "").lower() == "true",
        mgr=fields.get("Mgr", "").lower() == "true",
        personal=fields.get("Personal", "").lower() == "true",
        project=fields.get("Project") or None,
        tags=fields.get("Tags", "").split() if fields.get("Tags") else [],
    )


def get_tasks():
    content = load_log()
    match = re.search(r"### High-Priority(.*?)### Waiting On", content, re.S)
    if not match:
        return []
    tasks = [_parse_task_line(t) for t in re.findall(r"- \[ \] (.*)", match.group(1))]
    priority_order = {"A": 0, "B": 1, "C": 2, None: 3}
    tasks.sort(key=lambda t: (
        (0, t.due_date) if t.due_date else (1, ""),
        priority_order.get(t.priority, 3),
    ))
    return tasks


def _build_task_line(title, priority, due_date, created, mgr, personal, project, tags, carried=False):
    title_part = f"({priority}) {title}" if priority else title
    parts = [title_part]
    if due_date:
        parts.append(f"Due: {due_date}")
    parts.append(f"Created: {created}")
    if carried:
        parts.append("Carried: true")
    if mgr:
        parts.append("Mgr: true")
    if personal:
        parts.append("Personal: true")
    if project:
        parts.append(f"Project: {project}")
    if tags:
        parts.append(f"Tags: {' '.join(tags)}")
    return "- [ ] " + " | ".join(parts)


def add_task(task_name, tag="", due_date="", priority="", project=""):
    content = load_log()
    task_name = _clean(task_name)
    tags = [t.lstrip("#").lower() for t in tag.split() if t] if tag else []
    line = _build_task_line(task_name, priority, due_date, date.today().isoformat(),
                            False, False, project, tags) + "\n"
    content = content.replace("### High-Priority\n", f"### High-Priority\n{line}", 1)
    save_log(content)


def edit_task(old_title, new_title, priority="", due_date="", tags=None, created=None, project=""):
    content = load_log()
    new_title = _clean(new_title)
    if created:
        pattern = re.compile(r"- \[ \] .*Created: " + re.escape(created) + r".*")
    else:
        search_text = old_title.split(" @")[0].rstrip("…")
        pattern = re.compile(r"- \[ \] .*" + re.escape(search_text) + r".*")
    match = pattern.search(content)
    if not match:
        return
    old_task = _parse_task_line(match.group(0)[6:])  # strip "- [ ] "
    used_created = created or old_task.created or date.today().isoformat()
    new_line = _build_task_line(new_title, priority, due_date, used_created,
                                old_task.mgr, old_task.personal, project, tags or [])
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_task(task_title, created=None):
    content = load_log()
    if created:
        pattern = re.compile(r"- \[ \] .*Created: " + re.escape(created) + r".*\n")
    else:
        pattern = re.compile(r"- \[ \] .*" + re.escape(task_title.rstrip("…")) + r".*\n")
    if not pattern.search(content):
        return False
    content = pattern.sub("", content, count=1)
    save_log(content)
    return True


def complete_task(task_text, outcome, created=None):
    content = load_log()
    if created:
        pattern = re.compile(r"- \[ \] .*Created: " + re.escape(created) + r".*\n")
    else:
        pattern = re.compile(r"- \[ \] .*" + re.escape(task_text.rstrip("…")) + r".*\n")
    match = pattern.search(content)
    if not match:
        return
    task = _parse_task_line(match.group(0).strip()[6:])
    content = pattern.sub("", content, count=1)

    task_parts = [f"Task: {task_text.rstrip('…')}"]
    if task.mgr:
        task_parts.append("Mgr: true")
    if task.personal:
        task_parts.append("Personal: true")
    if task.project:
        task_parts.append(f"Project: {task.project}")
    if task.tags:
        task_parts.append(f"Tags: {' '.join(task.tags)}")

    accomplishment = (
        f"- {' | '.join(task_parts)}\n"
        f"  Outcome: {outcome}\n"
        f"  Completed: {date.today()}\n\n"
    )
    content = content.replace("### Wins Worth Mentioning", accomplishment + "### Wins Worth Mentioning", 1)
    save_log(content)


def reopen_task(task_title):
    content = load_log()
    pattern = re.compile(r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n\n", re.MULTILINE)
    for match in pattern.finditer(content):
        raw = match.group(1)
        clean = re.sub(r"\s*\|\s*(Mgr|Personal|Project|Tags):.*", "", raw).strip()
        if clean == task_title:
            content = content.replace(match.group(0), "", 1)
            content = content.replace("### High-Priority\n", f"### High-Priority\n- [ ] {task_title}\n", 1)
            save_log(content)
            return


def toggle_mgr_task(task_title, created=None):
    content = load_log()
    if created:
        pattern = re.compile(r"- \[ \] .*Created: " + re.escape(created) + r".*")
    else:
        search_text = task_title.split(" @")[0].rstrip("…")
        pattern = re.compile(r"- \[ \] .*" + re.escape(search_text) + r".*")
    match = pattern.search(content)
    if not match:
        return
    task = _parse_task_line(match.group(0)[6:])
    new_line = _build_task_line(task.title, task.priority, task.due_date, task.created,
                                not task.mgr, task.personal, task.project, task.tags)
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def toggle_personal_task(task_title, created=None):
    content = load_log()
    if created:
        pattern = re.compile(r"- \[ \] .*Created: " + re.escape(created) + r".*")
    else:
        search_text = task_title.split(" @")[0].rstrip("…")
        pattern = re.compile(r"- \[ \] .*" + re.escape(search_text) + r".*")
    match = pattern.search(content)
    if not match:
        return
    task = _parse_task_line(match.group(0)[6:])
    new_line = _build_task_line(task.title, task.priority, task.due_date, task.created,
                                task.mgr, not task.personal, task.project, task.tags)
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)
