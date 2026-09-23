import re
from datetime import date
from models import Risk
from parser._core import extract_tags, _clean, load_log, save_log


def get_risks():
    content = load_log()
    match = re.search(r"### Risks(.*?)###", content, re.S)
    if not match:
        return []
    risks = []
    for description, owner, since, severity, rest in re.findall(
        r"- (.*?) \| Owner:\s*(.*?) \| Since:\s*(\d{4}-\d{2}-\d{2}) \| Severity:\s*([HML])(.*)",
        match.group(1),
    ):
        personal = "Personal:true" in rest
        rest_clean = rest.replace(" Personal:true", "").replace(" Mgr:true", "")
        mgr = "Mgr:true" in rest
        tags = extract_tags(rest_clean)
        project_match = re.search(r"\+([\w]+)", rest_clean)
        project = project_match.group(1) if project_match else None
        risks.append(Risk(
            description=description, owner=owner, since=since, severity=severity,
            tags=tags, personal=personal, project=project, mgr=mgr,
        ))
    return risks


def add_risk(description, owner, severity, tags=None, personal=False, project="", mgr=False):
    content = load_log()
    description, owner = _clean(description), _clean(owner)
    personal_str = " Personal:true" if personal else ""
    mgr_str = " Mgr:true" if mgr else ""
    project_str = f" +{project}" if project else ""
    tag_str = " " + " ".join(f"#{t}" for t in tags) if tags else ""
    line = (
        f"- {description} | Owner: {owner} "
        f"| Since: {date.today()} "
        f"| Severity: {severity.upper()}{personal_str}{mgr_str}{project_str}{tag_str}\n"
    )
    content = content.replace("### Risks\n", f"### Risks\n{line}", 1)
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
    new_line = f"- {new_description} | Owner: {owner} | Since: {since} | Severity: {severity.upper()}"
    if "Personal:true" in match.group(0):
        new_line += " Personal:true"
    if "Mgr:true" in match.group(0):
        new_line += " Mgr:true"
    if project:
        new_line += f" +{project}"
    if tags:
        new_line += " " + " ".join(f"#{t}" for t in tags)
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
    content = content.replace("### Accomplishments\n", resolved_entry + "### Accomplishments\n", 1)
    save_log(content)


def toggle_mgr_risk(description):
    content = load_log()
    pattern = re.compile(
        r"- " + re.escape(description) + r" \| Owner:\s*.*? \| Since:\s*\d{4}-\d{2}-\d{2} \| Severity:\s*[HML].*"
    )
    match = pattern.search(content)
    if not match:
        return
    line = match.group(0)
    new_line = line.replace(" Mgr:true", "") if "Mgr:true" in line else line + " Mgr:true"
    content = content.replace(line, new_line, 1)
    save_log(content)


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
