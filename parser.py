import re
import tomllib
from datetime import date, timedelta
from pathlib import Path
from models import Task, Dependency, Accomplishment, ResolvedDependency, DailyLogEntry, Risk, SomedayItem, Event


def _load_config() -> dict:
    config_path = Path(__file__).parent / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}


def _get_logs_path() -> Path:
    config = _load_config()
    logs_path = config.get("logs_path", "logs")
    p = Path(logs_path)
    return p if p.is_absolute() else Path(__file__).parent / p


def get_terminal_size() -> tuple[int, int] | None:
    config = _load_config()
    size = config.get("terminal_size")
    if isinstance(size, list) and len(size) == 2:
        return (int(size[0]), int(size[1]))
    return None


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

    # Carry over open dependencies (full line preserved)
    dep_match = re.search(
        r"### Waiting On(.*?)### Resolved Dependencies",
        prev_content,
        re.S,
    )
    carried_deps = ""
    if dep_match:
        carried_deps = "\n".join(
            line for line in dep_match.group(1).splitlines()
            if re.match(r"- .+ \| Owner:", line.strip())
        )

    # Carry over someday items
    someday_match = re.search(
        r"### Someday/Future(.*?)### Risks",
        prev_content,
        re.S,
    )
    carried_someday = ""
    if someday_match:
        carried_someday = "\n".join(
            line for line in someday_match.group(1).splitlines()
            if re.match(r"- .+ \| Owner:", line.strip())
        )

    # Carry over risks
    risk_match = re.search(
        r"### Risks(.*?)### Accomplishments",
        prev_content,
        re.S,
    )
    carried_risks = ""
    if risk_match:
        carried_risks = "\n".join(
            line for line in risk_match.group(1).splitlines()
            if re.match(r"- .+ \| Owner:.+ \| Severity:", line.strip())
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
    if carried_someday:
        content = content.replace(
            "### Someday/Future\n",
            f"### Someday/Future\n{carried_someday}\n",
            1,
        )
    if carried_risks:
        content = content.replace(
            "### Risks\n",
            f"### Risks\n{carried_risks}\n",
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
                created=created, tags=tags, carried=carried, mgr=mgr, personal=personal, project=project)


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

    marker = "### High-Priority\n"

    content = content.replace(
        marker,
        marker + line,
        1,
    )

    save_log(content)


def edit_task(old_title, new_title, priority="", due_date="", tags=None, created=None, project=""):

    content = load_log()

    new_title = _clean(new_title)
    if created:
        search_text = re.escape(old_title.split(" @")[0].rstrip("…"))
        pattern = re.compile(r"- \[ \] .*" + search_text + r".*Created:" + re.escape(created) + r".*")
        if not pattern.search(content):
            # fallback: match by created date only
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

    if match and "Mgr:true" in match.group(0):
        new_line += " Mgr:true"

    if match and "Personal:true" in match.group(0):
        new_line += " Personal:true"

    if project:
        new_line += f" +{project}"

    if tags:
        new_line += " " + " ".join(f"#{t}" for t in tags)

    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


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


def toggle_personal_accomplishment(task_title):
    content = load_log()
    pattern = re.compile(
        r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n",
        re.S,
    )
    for match in pattern.finditer(content):
        raw = match.group(1)
        if strip_tags(raw.replace(" Mgr:true", "").replace(" Personal:true", "")).strip() == task_title:
            new_raw = raw.replace(" Personal:true", "") if "Personal:true" in raw else raw + " Personal:true"
            new_block = match.group(0).replace(raw, new_raw, 1)
            content = content.replace(match.group(0), new_block, 1)
            save_log(content)
            return


def toggle_mgr_accomplishment(task_title):
    content = load_log()
    pattern = re.compile(
        r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n",
        re.S,
    )
    for match in pattern.finditer(content):
        raw = match.group(1)
        if strip_tags(raw.replace(" Mgr:true", "")).strip() == task_title:
            if "Mgr:true" in raw:
                new_raw = raw.replace(" Mgr:true", "")
            else:
                new_raw = raw + " Mgr:true"
            new_block = match.group(0).replace(raw, new_raw, 1)
            content = content.replace(match.group(0), new_block, 1)
            save_log(content)
            return


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
        r"- (.*?) \| Owner:\s*(.*?) \| Since:\s*(\d{4}-\d{2}-\d{2})(.*)",
        match.group(1),
    )

    dependencies = []

    for item, owner, since, rest in matches:

        since_date = date.fromisoformat(since)
        # amazonq-ignore-next-line
        age = (date.today() - since_date).days
        tags = extract_tags(rest)
        clean_item = strip_tags(item)

        handoff_match = re.search(r"HandoffFrom:([^|\n]+)", rest)
        handoff_from = handoff_match.group(1).strip() if handoff_match else None

        expected_match = re.search(r"Expected:\s*(\d{4}-\d{2}-\d{2})", rest)
        expected_date = expected_match.group(1) if expected_match else None

        project_match = re.search(r"\+([\w]+)", rest)
        project = project_match.group(1) if project_match else None

        dependencies.append(
            Dependency(
                clean_item,
                owner,
                since,
                age,
                tags,
                handoff_from=handoff_from,
                expected_date=expected_date,
                project=project,
            )
        )

    return dependencies


def add_dependency(item, owner, handoff_from=None, expected_date=None, tags=None, project=""):

    content = load_log()

    item, owner = _clean(item), _clean(owner)

    line = f"- {item} | Owner: {owner} | Since: {date.today()}"
    if handoff_from:
        line += f" | HandoffFrom: {handoff_from}"
    if expected_date:
        line += f" | Expected: {expected_date}"
    if project:
        line += f" +{project}"
    if tags:
        line += " " + " ".join(f"#{t}" for t in tags)
    line += "\n"

    marker = "### Waiting On\n"
    content = content.replace(marker, marker + line, 1)
    save_log(content)


def edit_dependency(old_item, new_item, owner, expected_date=None, tags=None, project=""):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(old_item) + r" \| Owner:\s*.*? \| Since:\s*(\d{4}-\d{2}-\d{2}).*"
    )
    match = pattern.search(content)

    if not match:
        return

    since = match.group(1)
    new_item, owner = _clean(new_item), _clean(owner)
    handoff_match = re.search(r"HandoffFrom:([^|\n]+)", match.group(0))
    new_line = f"- {new_item} | Owner: {owner} | Since: {since}"
    if handoff_match:
        new_line += f" | HandoffFrom: {handoff_match.group(1).strip()}"
    if expected_date:
        new_line += f" | Expected: {expected_date}"
    if project:
        new_line += f" +{project}"
    if tags:
        new_line += " " + " ".join(f"#{t}" for t in tags)
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
        # amazonq-ignore-next-line
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
        personal = "Personal:true" in rest
        rest_clean = rest.replace(" Personal:true", "")
        tags = extract_tags(rest_clean)
        project_match = re.search(r"\+([\w]+)", rest_clean)
        project = project_match.group(1) if project_match else None

        risks.append(
            Risk(
                description=description,
                owner=owner,
                since=since,
                severity=severity,
                tags=tags,
                personal=personal,
                project=project,
            )
        )

    return risks


def add_risk(description, owner, severity, tags=None, personal=False, project=""):

    content = load_log()

    description, owner = _clean(description), _clean(owner)

    personal_str = " Personal:true" if personal else ""
    project_str = f" +{project}" if project else ""
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""

    line = (
        f"- {description} | Owner: {owner} "
        f"| Since: {date.today()} "
        f"| Severity: {severity.upper()}{personal_str}{project_str}{tag_str}\n"
    )

    content = content.replace(
        "### Risks\n",
        f"### Risks\n{line}",
        1,
    )

    save_log(content)


def edit_risk(old_description, new_description, owner, severity, tags=None, project=""):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(old_description) + r" \| Owner:\s*.*? \| Since:\s*(\d{4}-\d{2}-\d{2}) \| Severity:\s*[HML].*"
    )
    match = pattern.search(content)

    if not match:
        return

    since = match.group(1)
    new_description, owner = _clean(new_description), _clean(owner)
    project_str = f" +{project}" if project else ""
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""
    new_line = (
        f"- {new_description} | Owner: {owner} "
        f"| Since: {since} "
        f"| Severity: {severity.upper()}"
    )
    if match and "Personal:true" in match.group(0):
        new_line += " Personal:true"
    new_line += project_str + tag_str
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
        personal = "Personal:true" in rest
        rest_clean = rest.replace(" Personal:true", "")
        tags = extract_tags(rest_clean)
        project_match = re.search(r"\+([\w]+)", rest_clean)
        project = project_match.group(1) if project_match else None

        items.append(
            SomedayItem(
                item=item,
                owner=owner,
                since=since,
                tags=tags,
                personal=personal,
                project=project,
            )
        )

    return items


def toggle_personal_risk(description):
    content = load_log()
    pattern = re.compile(
        r"- " + re.escape(description) + r" \| Owner:\s*.*? \| Since:\s*\d{4}-\d{2}-\d{2} \| Severity:\s*[HML].*"
    )
    match = pattern.search(content)
    if not match:
        return
    line = match.group(0)
    new_line = line.replace(" Personal:true", "") if "Personal:true" in line else line + " Personal:true"
    content = content.replace(line, new_line, 1)
    save_log(content)


def add_someday_item(item, owner, tags=None, personal=False, project=""):

    content = load_log()

    item, owner = _clean(item), _clean(owner)

    personal_str = " Personal:true" if personal else ""
    project_str = f" +{project}" if project else ""
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""

    line = (
        f"- {item} | Owner: {owner} "
        f"| Since: {date.today()}{personal_str}{project_str}{tag_str}\n"
    )

    content = content.replace(
        "### Someday/Future\n",
        f"### Someday/Future\n{line}",
        1,
    )

    save_log(content)


def edit_someday_item(old_item, new_item, owner, tags=None, project=""):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(old_item) + r" \| Owner:\s*.*? \| Since:\s*(\d{4}-\d{2}-\d{2}).*"
    )
    match = pattern.search(content)

    if not match:
        return

    since = match.group(1)
    new_item, owner = _clean(new_item), _clean(owner)
    project_str = f" +{project}" if project else ""
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""
    new_line = f"- {new_item} | Owner: {owner} | Since: {since}"
    if match and "Personal:true" in match.group(0):
        new_line += " Personal:true"
    new_line += project_str + tag_str
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_someday_item(item_text):

    content = load_log()

    pattern = re.compile(
        r"- " + re.escape(item_text) + r" \| Owner:\s*.*? \| Since:\s*\d{4}-\d{2}-\d{2}.*\n"
    )
    content = pattern.sub("", content, count=1)
    save_log(content)


def toggle_personal_someday(item_text):
    content = load_log()
    pattern = re.compile(
        r"- " + re.escape(item_text) + r" \| Owner:\s*.*? \| Since:\s*\d{4}-\d{2}-\d{2}.*"
    )
    match = pattern.search(content)
    if not match:
        return
    line = match.group(0)
    new_line = line.replace(" Personal:true", "") if "Personal:true" in line else line + " Personal:true"
    content = content.replace(line, new_line, 1)
    save_log(content)


def promote_someday_item(item_text, priority="", due_date="", tags=None, project=""):

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
                # amazonq-ignore-next-line
                task_line += f" Due:{due_date}"
            task_line += f" Created:{date.today()}"
            if project:
                task_line += f" +{project}"
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
            task=strip_tags(re.sub(r"\s*\+[\w]+", "", task.replace(" Mgr:true", "").replace(" Personal:true", ""))),
            outcome=outcome,
            completed=completed,
            tags=extract_tags(task),
            mgr="Mgr:true" in task,
            personal="Personal:true" in task,
            project=re.search(r"\+([\w]+)", task).group(1) if re.search(r"\+([\w]+)", task) else None,
        )
        for task, outcome, completed in matches
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

    content = content.replace(
        "### Wins Worth Mentioning",
        block + "### Wins Worth Mentioning",
        1,
    )
    save_log(content)


def _find_accomplishment_block(content, task_title):
    """Find accomplishment block where stripped task title matches."""
    pattern = re.compile(
        r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n",
        re.S,
    )
    for match in pattern.finditer(content):
        if strip_tags(re.sub(r"\s*\+[\w]+", "", match.group(1).replace(" Mgr:true", "").replace(" Personal:true", ""))).strip() == task_title:
            return match
    return None


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

    # Remove the block plus the trailing blank line
    full_block = re.compile(
        re.escape(match.group(0)) + r"\n?"
    )
    content = full_block.sub("", content, count=1)
    save_log(content)


# ==========================================================
# COMPLETE TASK
# ==========================================================

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
    flags = ("".join([
        " Mgr:true" if mgr else "",
        " Personal:true" if personal else "",
        f" +{project}" if project else "",
        (" " + " ".join(f"#{t}" for t in carried_tags)) if carried_tags else "",
    ]))
    accomplishment = (
        f"- Task: {clean_title}{flags}\n"
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
        if t.due_date and date.fromisoformat(t.due_date) < today
    )

    oldest_dep = max((d.age for d in deps), default=0)

    oldest_task = max(
        ((today - date.fromisoformat(t.created)).days
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


def get_tag_counts() -> dict[str, int]:
    """Return {tag: count} across all objects."""
    counts: dict[str, int] = {}
    for obj in [*get_tasks(), *get_dependencies(), *get_risks(), *get_someday_items(), *get_accomplishments()]:
        for tag in obj.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return counts


def delete_tag(tag: str):
    """Remove all occurrences of #tag from the log file."""
    path = get_log_file()
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"\s*#" + re.escape(tag) + r"\b", "", content)
    path.write_text(content, encoding="utf-8")


def get_all_projects():
    """Return sorted list of unique project names across all objects."""
    projects = set()
    for obj in [*get_tasks(), *get_dependencies(), *get_risks(), *get_someday_items(), *get_accomplishments()]:
        if obj.project:
            projects.add(obj.project)
    return sorted(projects, key=str.lower)


def get_project_counts() -> dict[str, dict[str, int]]:
    """Return {project: {tasks, deps, risks, high_risks, someday, accomplishments}} counts."""
    counts: dict[str, dict[str, int]] = {}
    def _inc(project, key):
        if project:
            counts.setdefault(project, {"tasks": 0, "deps": 0, "risks": 0, "high_risks": 0, "someday": 0, "accomplishments": 0})
            counts[project][key] += 1
    for t in get_tasks(): _inc(t.project, "tasks")
    for d in get_dependencies(): _inc(d.project, "deps")
    for r in get_risks():
        _inc(r.project, "risks")
        if r.severity.upper() == "H":
            _inc(r.project, "high_risks")
    for s in get_someday_items(): _inc(s.project, "someday")
    for a in get_accomplishments(): _inc(a.project, "accomplishments")
    return counts


def rename_project(old: str, new: str):
    """Rename all occurrences of +old to +new in the log file."""
    path = get_log_file()
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"\+" + re.escape(old) + r"\b", f"+{new}", content)
    path.write_text(content, encoding="utf-8")


def rename_tag(old_tag, new_tag):
    """Rename all occurrences of #old_tag to #new_tag in the log file."""
    path = get_log_file()
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"#" + re.escape(old_tag) + r"\b", f"#{new_tag}", content)
    path.write_text(content, encoding="utf-8")


def get_update_data(since_date: str) -> dict:
    tasks = get_tasks()
    all_accomplishments = []
    all_resolved_deps = []
    all_resolved_risks = []
    for path in sorted(_get_logs_path().glob("*-Director-Log.md")):
        content = path.read_text(encoding="utf-8")
        for task, outcome, completed in re.findall(
            r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n", content, re.MULTILINE
        ):
            all_accomplishments.append(Accomplishment(
                task=strip_tags(task.replace(" Mgr:true", "")),
                outcome=outcome,
                completed=completed,
                tags=extract_tags(task),
                mgr="Mgr:true" in task,
            ))
        for item, owner, resolved, notes in re.findall(
            r"- Dependency: (.*?)\n  Owner: (.*?)\n  Resolved: (\d{4}-\d{2}-\d{2})\n  Notes: (.*?)\n",
            content, re.MULTILINE
        ):
            if resolved >= since_date:
                all_resolved_deps.append({"item": item, "owner": owner, "resolved": resolved, "notes": notes})
        for item, owner, severity, resolved, notes in re.findall(
            r"- Risk: (.*?)\n  Owner: (.*?)\n  Severity: ([HML])\n  Resolved: (\d{4}-\d{2}-\d{2})\n  Notes: (.*?)\n",
            content, re.MULTILINE
        ):
            if resolved >= since_date:
                all_resolved_risks.append({"item": item, "owner": owner, "severity": severity, "resolved": resolved, "notes": notes})
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
        "resolved_deps": all_resolved_deps,
        "resolved_risks": all_resolved_risks,
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

    lines.append("\n### Resolved Dependencies")
    if data.get("resolved_deps"):
        for d in data["resolved_deps"]:
            lines.append(f"- {d['item']} — {d['owner']} (resolved {d['resolved']})")
            if d["notes"]:
                lines.append(f"  Notes: {d['notes']}")
    else:
        lines.append("- None")

    lines.append("\n### Resolved Risks")
    if data.get("resolved_risks"):
        for r in data["resolved_risks"]:
            lines.append(f"- {r['item']} [{r['severity']}] — {r['owner']} (resolved {r['resolved']})")
            if r["notes"]:
                lines.append(f"  Notes: {r['notes']}")
    else:
        lines.append("- None")

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
    week_start = today - timedelta(days=today.weekday())
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
            event_date = date.fromisoformat(e.date)
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


# ==========================================================
# SCRATCH PAD
# ==========================================================

def get_scratch_file():
    return _get_logs_path() / "scratch.md"


def get_scratch() -> str:
    path = get_scratch_file()
    return path.read_text(encoding="utf-8") if path.exists() else ""


def save_scratch(text: str):
    get_scratch_file().write_text(text, encoding="utf-8")
