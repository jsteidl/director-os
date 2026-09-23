import re
from datetime import date
from models import SomedayItem
from parser._core import extract_tags, _clean, load_log, save_log


def get_someday_items():
    content = load_log()
    match = re.search(r"### Someday/Future(.*?)### Risks", content, re.S)
    if not match:
        return []
    items = []
    for item, owner, since, rest in re.findall(
        r"- (.*?) \| Owner:\s*(.*?) \| Since: (\d{4}-\d{2}-\d{2})(.*)",
        match.group(1),
    ):
        personal = "Personal:true" in rest
        rest_clean = rest.replace(" Personal:true", "")
        tags = extract_tags(rest_clean)
        project_match = re.search(r"\+([\w]+)", rest_clean)
        project = project_match.group(1) if project_match else None
        items.append(SomedayItem(item=item, owner=owner, since=since, tags=tags, personal=personal, project=project))
    return items


def add_someday_item(item, owner, tags=None, personal=False, project=""):
    content = load_log()
    item, owner = _clean(item), _clean(owner)
    personal_str = " Personal:true" if personal else ""
    project_str = f" +{project}" if project else ""
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""
    line = f"- {item} | Owner: {owner} | Since: {date.today()}{personal_str}{project_str}{tag_str}\n"
    content = content.replace("### Someday/Future\n", f"### Someday/Future\n{line}", 1)
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
    new_line = f"- {new_item} | Owner: {owner} | Since: {since}"
    if "Personal:true" in match.group(0):
        new_line += " Personal:true"
    if project:
        new_line += f" +{project}"
    if tags:
        new_line += " " + " ".join(f"#{t}" for t in tags)
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
    for item, owner, since, rest in re.findall(
        r"- (.*?) \| Owner: (.*?) \| Since: (\d{4}-\d{2}-\d{2})(.*)", content
    ):
        if item == item_text:
            original = f"- {item} | Owner: {owner} | Since: {since}{rest}"
            content = content.replace(original + "\n", "", 1)
            title = f"({priority}) {item_text}" if priority else item_text
            task_line = f"- [ ] {title}"
            if due_date:
                task_line += f" Due:{due_date}"
            task_line += f" Created:{date.today()}"
            if project:
                task_line += f" +{project}"
            if tags:
                task_line += " " + " ".join(f"#{t}" for t in tags)
            content = content.replace("### High-Priority\n", f"### High-Priority\n{task_line}\n", 1)
            save_log(content)
            return
