import re
from datetime import date
from models import Task
from parser._core import extract_tags, strip_tags, _clean, load_log, save_log


def _parse_task_line(title) -> Task:
    due_match = re.search(r"Due:(\d{4}-\d{2}-\d{2})", title)
    due_date = due_match.group(1) if due_match else None
    if due_date:
        title = title.replace(f" Due:{due_date}", "").strip()

    created_match = re.search(r"Created:(\d{4}-\d{2}-\d{2})", title)
    created = created_match.group(1) if created_match else None
    if created:
        title = title.replace(f" Created:{created}", "").strip()

    carried = "Carried:true" in title
    if carried:
        title = title.replace(" Carried:true", "").strip()

    mgr = "Mgr:true" in title
    if mgr:
        title = title.replace(" Mgr:true", "").strip()

    personal = "Personal:true" in title
    if personal:
        title = title.replace(" Personal:true", "").strip()

    priority = None
    priority_match = re.match(r"^\(([ABC])\)\s+(.*)$", title)
    if priority_match:
        priority = priority_match.group(1)
        title = priority_match.group(2)

    project_match = re.search(r"\+([\w]+)", title)
    project = project_match.group(1) if project_match else None
    if project:
        title = re.sub(r"\s*\+[\w]+", "", title).strip()

    tags = extract_tags(title)
    title = strip_tags(title)

    return Task(title=title, priority=priority, due_date=due_date,
                created=created, tags=tags, carried=carried, mgr=mgr,
                personal=personal, project=project)


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


def add_task(task_name, tag="", due_date="", priority="", project=""):
    content = load_log()
    task_name = _clean(task_name)
    title = f"({priority}) {task_name}" if priority else task_name
    line = f"- [ ] {title}"
    if due_date:
        line += f" Due:{due_date}"
    line += f" Created:{date.today()}"
    if project:
        line += f" +{project}"
    if tag:
        line += " " + " ".join(f"#{t}" for t in tag.split() if t)
    line += "\n"
    content = content.replace("### High-Priority\n", f"### High-Priority\n{line}", 1)
    save_log(content)


def edit_task(old_title, new_title, priority="", due_date="", tags=None, created=None, project=""):
    content = load_log()
    new_title = _clean(new_title)
    if created:
        search_text = re.escape(old_title.split(" @")[0].rstrip("…"))
        pattern = re.compile(r"- \[ \] .*" + search_text + r".*Created:" + re.escape(created) + r".*")
        if not pattern.search(content):
            pattern = re.compile(r"- \[ \] .*Created:" + re.escape(created) + r".*")
    else:
        search_text = old_title.split(" @")[0].rstrip("…")
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
    if "Mgr:true" in match.group(0):
        new_line += " Mgr:true"
    if "Personal:true" in match.group(0):
        new_line += " Personal:true"
    if project:
        new_line += f" +{project}"
    if tags:
        new_line += " " + " ".join(f"#{t}" for t in tags)
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_task(task_title, created=None):
    content = load_log()
    if created:
        search_text = re.escape(task_title.rstrip("…"))
        pattern = re.compile(r"- \[ \] .*" + search_text + r".*Created:" + re.escape(created) + r".*\n")
        if not pattern.search(content):
            pattern = re.compile(r"- \[ \] .*Created:" + re.escape(created) + r".*\n")
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
        search_text = re.escape(task_text.rstrip("…"))
        pattern = re.compile(r"- \[ \] .*" + search_text + r".*Created:" + re.escape(created) + r".*\n")
        if not pattern.search(content):
            pattern = re.compile(r"- \[ \] .*Created:" + re.escape(created) + r".*\n")
    else:
        pattern = re.compile(r"- \[ \] .*" + re.escape(task_text.rstrip("…")) + r".*\n")
    match = pattern.search(content)
    mgr = bool(match and "Mgr:true" in match.group(0))
    personal = bool(match and "Personal:true" in match.group(0))
    project_match = re.search(r"\+([\w]+)", match.group(0)) if match else None
    project = project_match.group(1) if project_match else None
    carried_tags = extract_tags(match.group(0)) if match else []
    content = pattern.sub("", content, count=1)
    clean_title = task_text.rstrip("…")
    flags = "".join([
        " Mgr:true" if mgr else "",
        " Personal:true" if personal else "",
        f" +{project}" if project else "",
        (" " + " ".join(f"#{t}" for t in carried_tags)) if carried_tags else "",
    ])
    accomplishment = (
        f"- Task: {clean_title}{flags}\n"
        f"  Outcome: {outcome}\n"
        f"  Completed: {date.today()}\n\n"
    )
    content = content.replace("### Wins Worth Mentioning", accomplishment + "### Wins Worth Mentioning", 1)
    save_log(content)


def reopen_task(task_title):
    content = load_log()
    pattern = re.compile(r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n\n", re.MULTILINE)
    for match in pattern.finditer(content):
        if strip_tags(match.group(1)).strip() == task_title:
            content = content.replace(match.group(0), "", 1)
            content = content.replace("### High-Priority\n", f"### High-Priority\n- [ ] {task_title}\n", 1)
            save_log(content)
            return


def toggle_mgr_task(task_title, created=None):
    content = load_log()
    if created:
        search_text = re.escape(task_title.split(" @")[0].rstrip("…"))
        pattern = re.compile(r"- \[ \] .*" + search_text + r".*Created:" + re.escape(created) + r".*")
        if not pattern.search(content):
            pattern = re.compile(r"- \[ \] .*Created:" + re.escape(created) + r".*")
    else:
        search_text = task_title.split(" @")[0].rstrip("…")
        pattern = re.compile(r"- \[ \] .*" + re.escape(search_text) + r".*")
    match = pattern.search(content)
    if not match:
        return
    line = match.group(0)
    new_line = line.replace(" Mgr:true", "") if "Mgr:true" in line else line + " Mgr:true"
    content = content.replace(line, new_line, 1)
    save_log(content)


def toggle_personal_task(task_title, created=None):
    content = load_log()
    if created:
        search_text = re.escape(task_title.split(" @")[0].rstrip("…"))
        pattern = re.compile(r"- \[ \] .*" + search_text + r".*Created:" + re.escape(created) + r".*")
        if not pattern.search(content):
            pattern = re.compile(r"- \[ \] .*Created:" + re.escape(created) + r".*")
    else:
        search_text = task_title.split(" @")[0].rstrip("…")
        pattern = re.compile(r"- \[ \] .*" + re.escape(search_text) + r".*")
    match = pattern.search(content)
    if not match:
        return
    line = match.group(0)
    new_line = line.replace(" Personal:true", "") if "Personal:true" in line else line + " Personal:true"
    content = content.replace(line, new_line, 1)
    save_log(content)
