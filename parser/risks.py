import re
from datetime import date
from models import Risk
from parser._core import extract_tags, _clean, load_log, save_log


def _parse_risk_line(line):
    parts = [p.strip() for p in line.lstrip("- ").split(" | ")]
    fields = {}
    for p in parts[1:]:
        if ": " in p:
            k, v = p.split(": ", 1)
            fields[k] = v
    return Risk(
        description=parts[0],
        owner=fields.get("Owner", ""),
        since=fields.get("Since", ""),
        severity=fields.get("Severity", ""),
        tags=extract_tags(line),
        personal=fields.get("Personal") == "true",
        project=fields.get("Project"),
        mgr=fields.get("Mgr") == "true",
    )


def _build_risk_line(description, owner, since, severity, mgr=False,
                     personal=False, project="", tags=None):
    line = f"- {description} | Owner: {owner} | Since: {since} | Severity: {severity.upper()}"
    if mgr:
        line += " | Mgr: true"
    if personal:
        line += " | Personal: true"
    if project:
        line += f" | Project: {project}"
    if tags:
        line += f" | Tags: {' '.join(tags)}"
    return line


def get_risks():
    content = load_log()
    match = re.search(r"### Risks(.*?)###", content, re.S)
    if not match:
        return []
    risks = []
    for line in match.group(1).splitlines():
        if re.match(r"- .+ \| Owner:", line):
            risks.append(_parse_risk_line(line))
    return risks


def add_risk(description, owner, severity, tags=None, personal=False, project="", mgr=False):
    content = load_log()
    line = _build_risk_line(_clean(description), _clean(owner), date.today(),
                            severity, mgr, personal, project, tags) + "\n"
    content = content.replace("### Risks\n", f"### Risks\n{line}", 1)
    save_log(content)


def edit_risk(old_description, new_description, owner, severity, tags=None, project=""):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(old_description) + r" \| Owner:.*")
    match = pattern.search(content)
    if not match:
        return
    old = _parse_risk_line(match.group(0))
    new_line = _build_risk_line(_clean(new_description), _clean(owner), old.since,
                                severity, old.mgr, old.personal, project, tags)
    content = content.replace(match.group(0), new_line, 1)
    save_log(content)


def delete_risk(description):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(description) + r" \| Owner:.*\n")
    content = pattern.sub("", content, count=1)
    save_log(content)


def resolve_risk(description, notes):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(description) + r" \| Owner:\s*(.*?) \| Since:\s*(\d{4}-\d{2}-\d{2}) \| Severity:\s*([HML]).*")
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
    pattern = re.compile(r"- " + re.escape(description) + r" \| Owner:.*")
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


def toggle_personal_risk(description):
    content = load_log()
    pattern = re.compile(r"- " + re.escape(description) + r" \| Owner:.*")
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
