import re
from datetime import date
from models import Dependency
from parser._core import extract_tags, _clean, load_log, save_log


def _parse_dep_line(line):
    parts = [p.strip() for p in line.lstrip("- ").split(" | ")]
    fields = {}
    for p in parts[1:]:
        if ": " in p:
            k, v = p.split(": ", 1)
            fields[k] = v
    item = parts[0]
    since = fields.get("Since", "")
    since_date = date.fromisoformat(since) if since else date.today()
    # amazonq-ignore-next-line
    age = (date.today() - since_date).days
    tags = extract_tags(line)
    return Dependency(
        item=item,
        owner=fields.get("Owner", ""),
        since=since,
        age=age,
        tags=tags,
        handoff_from=fields.get("HandoffFrom"),
        expected_date=fields.get("Expected"),
        project=fields.get("Project"),
        mgr=fields.get("Mgr") == "true",
    )


def _build_dep_line(item, owner, since, handoff_from=None, expected_date=None,
                    mgr=False, project="", tags=None):
    line = f"- {item} | Owner: {owner} | Since: {since}"
    if handoff_from:
        line += f" | HandoffFrom: {handoff_from}"
    if expected_date:
        line += f" | Expected: {expected_date}"
    if mgr:
        line += " | Mgr: true"
    if project:
        line += f" | Project: {project}"
    if tags:
        line += f" | Tags: {' '.join(tags)}"
    return line


def get_dependencies():
    content = load_log()
    match = re.search(r"### Waiting On(.*?)### Resolved Dependencies", content, re.S)
    if not match:
        return []
    deps = []
    for line in match.group(1).splitlines():
        if re.match(r"- .+ \| Owner:", line):
            deps.append(_parse_dep_line(line))
    return deps


def add_dependency(item, owner, handoff_from=None, expected_date=None, tags=None, project="", mgr=False):
    content = load_log()
    line = _build_dep_line(_clean(item), _clean(owner), date.today(),
                           handoff_from, expected_date, mgr, project, tags) + "\n"
    content = content.replace("### Waiting On\n", f"### Waiting On\n{line}", 1)
    save_log(content)


def edit_dependency(old_item, new_item, owner, expected_date=None, tags=None, project=""):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(old_item) + r" \| Owner:.*")
    match = pattern.search(content)
    if not match:
        return
    old = _parse_dep_line(match.group(0))
    new_line = _build_dep_line(_clean(new_item), _clean(owner), old.since,
                               old.handoff_from, expected_date, old.mgr, project, tags)
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_dependency(item_text):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(item_text) + r" \| Owner:.*\n")
    content = pattern.sub("", content, count=1)
    save_log(content)


def resolve_dependency(dependency_name, resolution_notes):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(dependency_name) + r" \| Owner:\s*(.*?) \| Since:\s*(\d{4}-\d{2}-\d{2}).*")
    match = pattern.search(content)
    if not match:
        return
    content = pattern.sub("", content, count=1)
    resolved_entry = (
        f"- Dependency: {dependency_name}\n"
        f"  Owner: {match.group(1)}\n"
        f"  Resolved: {date.today()}\n"
        # amazonq-ignore-next-line
        f"  Notes: {resolution_notes}\n\n"
    )
    content = content.replace("### Someday/Future", resolved_entry + "### Someday/Future", 1)
    save_log(content)


def toggle_mgr_dependency(item_text):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(item_text) + r" \| Owner:.*")
    match = pattern.search(content)
    if not match:
        return
    line = match.group(0)
    if " | Mgr: true" in line:
        new_line = line.replace(" | Mgr: true", "")
    else:
        new_line = line + " | Mgr: true"
    content = content.replace(line, new_line, 1)
    save_log(content)
