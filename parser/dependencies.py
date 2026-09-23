import re
from datetime import date
from models import Dependency
from parser._core import extract_tags, strip_tags, _clean, load_log, save_log


def get_dependencies():
    content = load_log()
    match = re.search(r"### Waiting On(.*?)### Resolved Dependencies", content, re.S)
    if not match:
        return []
    dependencies = []
    for item, owner, since, rest in re.findall(
        r"- (.*?) \| Owner:\s*(.*?) \| Since:\s*(\d{4}-\d{2}-\d{2})(.*)",
        match.group(1),
    ):
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
        mgr = "Mgr:true" in rest
        dependencies.append(Dependency(
            clean_item, owner, since, age, tags,
            handoff_from=handoff_from, expected_date=expected_date,
            project=project, mgr=mgr,
        ))
    return dependencies


def add_dependency(item, owner, handoff_from=None, expected_date=None, tags=None, project="", mgr=False):
    content = load_log()
    item, owner = _clean(item), _clean(owner)
    line = f"- {item} | Owner: {owner} | Since: {date.today()}"
    if handoff_from:
        line += f" | HandoffFrom: {handoff_from}"
    if expected_date:
        line += f" | Expected: {expected_date}"
    if mgr:
        line += " Mgr:true"
    if project:
        line += f" +{project}"
    if tags:
        line += " " + " ".join(f"#{t}" for t in tags)
    line += "\n"
    content = content.replace("### Waiting On\n", f"### Waiting On\n{line}", 1)
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
    mgr = "Mgr:true" in match.group(0)
    new_line = f"- {new_item} | Owner: {owner} | Since: {since}"
    if handoff_match:
        new_line += f" | HandoffFrom: {handoff_match.group(1).strip()}"
    if expected_date:
        new_line += f" | Expected: {expected_date}"
    if mgr:
        new_line += " Mgr:true"
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


def resolve_dependency(dependency_name, resolution_notes):
    content = load_log()
    matches = re.findall(r"- (.*?) \| Owner:\s*(.*?) \| Since:\s*(\d{4}-\d{2}-\d{2})", content)
    target = next(((i, o, s) for i, o, s in matches if i == dependency_name), None)
    if not target:
        return
    item, owner, since = target
    content = content.replace(f"- {item} | Owner: {owner} | Since: {since}", "", 1)
    resolved_entry = (
        f"- Dependency: {item}\n"
        f"  Owner: {owner}\n"
        f"  Resolved: {date.today()}\n"
        # amazonq-ignore-next-line
        f"  Notes: {resolution_notes}\n\n"
    )
    content = content.replace("### Someday/Future", resolved_entry + "### Someday/Future", 1)
    save_log(content)


def toggle_mgr_dependency(item_text):
    content = load_log()
    pattern = re.compile(
        r"- " + re.escape(item_text) + r" \| Owner:\s*.*? \| Since:\s*\d{4}-\d{2}-\d{2}.*"
    )
    match = pattern.search(content)
    if not match:
        return
    line = match.group(0)
    new_line = line.replace(" Mgr:true", "") if "Mgr:true" in line else line + " Mgr:true"
    content = content.replace(line, new_line, 1)
    save_log(content)
