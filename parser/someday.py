import re
from datetime import date
from models import SomedayItem
from parser._core import extract_tags, _clean, load_log, save_log


def _parse_someday_line(line):
    parts = [p.strip() for p in line.lstrip("- ").split(" | ")]
    fields = {}
    for p in parts[1:]:
        if ": " in p:
            k, v = p.split(": ", 1)
            fields[k] = v
    return SomedayItem(
        item=parts[0],
        owner=fields.get("Owner", ""),
        since=fields.get("Since", ""),
        tags=extract_tags(line),
        personal=fields.get("Personal") == "true",
        project=fields.get("Project"),
    )


def _build_someday_line(item, owner, since, personal=False, project="", tags=None):
    line = f"- {item} | Owner: {owner} | Since: {since}"
    if personal:
        line += " | Personal: true"
    if project:
        line += f" | Project: {project}"
    if tags:
        line += f" | Tags: {' '.join(tags)}"
    return line


def get_someday_items():
    content = load_log()
    match = re.search(r"### Someday/Future(.*?)### Risks", content, re.S)
    if not match:
        return []
    items = []
    for line in match.group(1).splitlines():
        if re.match(r"- .+ \| Owner:", line):
            items.append(_parse_someday_line(line))
    return items


def add_someday_item(item, owner, tags=None, personal=False, project=""):
    content = load_log()
    line = _build_someday_line(_clean(item), _clean(owner), date.today(),
                               personal, project, tags) + "\n"
    content = content.replace("### Someday/Future\n", f"### Someday/Future\n{line}", 1)
    save_log(content)


def edit_someday_item(old_item, new_item, owner, tags=None, project=""):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(old_item) + r" \| Owner:.*")
    match = pattern.search(content)
    if not match:
        return
    old = _parse_someday_line(match.group(0))
    new_line = _build_someday_line(_clean(new_item), _clean(owner), old.since,
                                   old.personal, project, tags)
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_someday_item(item_text):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(item_text) + r" \| Owner:.*\n")
    content = pattern.sub("", content, count=1)
    save_log(content)


def toggle_personal_someday(item_text):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(item_text) + r" \| Owner:.*")
    match = pattern.search(content)
    if not match:
        return
    line = match.group(0)
    if " | Personal: true" in line:
        new_line = line.replace(" | Personal: true", "")
    else:
        new_line = line + " | Personal: true"
    content = content.replace(line, new_line, 1)
    save_log(content)


def promote_someday_item(item_text, priority="", due_date="", tags=None, project=""):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(item_text) + r" \| Owner:.*")
    match = pattern.search(content)
    if not match:
        return
    content = content.replace(match.group(0) + "\n", "", 1)
    title = f"({priority}) {item_text}" if priority else item_text
    task_line = f"- [ ] {title} | Created: {date.today()}"
    if due_date:
        task_line += f" | Due: {due_date}"
    if project:
        task_line += f" | Project: {project}"
    if tags:
        task_line += f" | Tags: {' '.join(tags)}"
    content = content.replace("### High-Priority\n", f"### High-Priority\n{task_line}\n", 1)
    save_log(content)
