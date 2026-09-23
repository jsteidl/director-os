import re
from parser._files import get_log_file, get_projects_file
from parser.tasks import get_tasks
from parser.dependencies import get_dependencies
from parser.risks import get_risks
from parser.someday import get_someday_items
from parser.accomplishments import get_accomplishments


def get_all_projects():
    projects = set()
    for obj in [*get_tasks(), *get_dependencies(), *get_risks(), *get_someday_items(), *get_accomplishments()]:
        if obj.project:
            projects.add(obj.project)
    return sorted(projects, key=str.lower)


def get_project_counts() -> dict[str, dict[str, int]]:
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


def get_project_meta() -> dict[str, dict[str, str]]:
    path = get_projects_file()
    if not path.exists():
        return {}
    meta = {}
    for m in re.finditer(
        r"- (\S+) \| Display: (.*?) \| Description: (.*)",
        path.read_text(encoding="utf-8"),
    ):
        meta[m.group(1)] = {"display": m.group(2).strip(), "description": m.group(3).strip()}
    return meta


def save_project_meta(tag: str, display: str, description: str):
    path = get_projects_file()
    content = path.read_text(encoding="utf-8") if path.exists() else "# Projects\n\n"
    line = f"- {tag} | Display: {display} | Description: {description}\n"
    pattern = re.compile(r"- " + re.escape(tag) + r" \| Display:.*\n")
    content = pattern.sub(line, content, count=1) if pattern.search(content) else content + line
    path.write_text(content, encoding="utf-8")


def delete_project_meta(tag: str):
    path = get_projects_file()
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"- " + re.escape(tag) + r" \| Display:.*\n", "", content)
    path.write_text(content, encoding="utf-8")


def rename_project(old: str, new: str):
    path = get_log_file()
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"(\| Project: )" + re.escape(old) + r"(\s*(?:\||\n|$))", r"\g<1>" + new + r"\2", content)
    path.write_text(content, encoding="utf-8")
    meta = get_project_meta()
    if old in meta:
        m = meta[old]
        delete_project_meta(old)
        save_project_meta(new, m["display"], m["description"])


def delete_project(tag: str):
    path = get_log_file()
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"\s*\| Project: " + re.escape(tag) + r"(\s*(?=\||\n|$))", r"\1", content)
    path.write_text(content, encoding="utf-8")
    delete_project_meta(tag)
