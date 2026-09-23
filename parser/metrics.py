import re
from datetime import date
from models import Accomplishment
from parser._core import extract_tags, _get_logs_path
from parser.tasks import get_tasks
from parser.dependencies import get_dependencies
from parser.risks import get_risks
from parser.accomplishments import get_accomplishments
from parser.daily import get_all_daily_entries
from parser.projects import get_project_meta


def get_metrics():
    today = date.today()
    tasks = get_tasks()
    deps = get_dependencies()
    risks = get_risks()
    accomplishments = get_accomplishments()
    overdue = sum(1 for t in tasks if t.due_date and date.fromisoformat(t.due_date) < today)
    oldest_dep = max((d.age for d in deps), default=0)
    oldest_task = max(
        ((today - date.fromisoformat(t.created)).days for t in tasks if t.created),
        default=0
    )
    high_risks = sum(1 for r in risks if r.severity.upper() == "H")
    month_wins = sum(1 for a in accomplishments if a.completed.startswith(today.strftime("%Y-%m")))
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


def get_update_data(since_date: str) -> dict:
    all_accomplishments = []
    all_resolved_deps = []
    all_resolved_risks = []
    for path in sorted(_get_logs_path().glob("*-Director-Log.md")):
        content = path.read_text(encoding="utf-8")
        for task, outcome, completed in re.findall(
            r"- Task: (.*?)\n  Outcome: (.*?)\n  Completed: (.*?)\n", content, re.MULTILINE
        ):
            parts = [p.strip() for p in task.split(" | ")]
            fields = {k: v for p in parts[1:] if ": " in p for k, v in [p.split(": ", 1)]}
            all_accomplishments.append(Accomplishment(
                task=parts[0],
                outcome=outcome,
                completed=completed,
                tags=extract_tags(task),
                mgr=fields.get("Mgr") == "true",
                personal=fields.get("Personal") == "true",
                project=fields.get("Project"),
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
    entries = [e for e in get_all_daily_entries() if e.date >= since_date]
    blocked = [(e.date, b) for e in entries for b in e.blocked]
    return {
        "since": since_date,
        "accomplished": accomplishments,
        "tasks": get_tasks(),
        "deps": get_dependencies(),
        "risks": get_risks(),
        "blocked": blocked,
        "resolved_deps": all_resolved_deps,
        "resolved_risks": all_resolved_risks,
    }


def save_update(since_date: str, data: dict) -> str:
    meta = get_project_meta()
    tasks = data.get("tasks", [])
    accomplishments = data.get("accomplished", [])
    deps = data.get("deps", [])
    risks = data.get("risks", [])

    all_projects = sorted(
        {i.project for i in [*tasks, *accomplishments, *deps, *risks] if i.project},
        key=str.lower
    )

    lines = [f"## Update — Since {since_date}\n"]

    for project in [*all_projects, None]:
        pt = [i for i in tasks if i.project == project]
        pa = [i for i in accomplishments if i.project == project]
        pd = [i for i in deps if i.project == project]
        pr = [i for i in risks if i.project == project]
        if not any([pt, pa, pd, pr]):
            continue
        if project:
            m = meta.get(project, {})
            display = m.get("display") or project
            description = m.get("description", "")
            open_count = len(pt)
            done_count = len(pa)
            due_dates = sorted(t.due_date for t in pt if t.due_date)
            due_str = f"next due {due_dates[0]}" if due_dates else "no due dates"
            lines.append(f"### {display}  [{open_count} open · {done_count} done · {due_str}]")
            if description:
                lines.append(f"_{description}_\n")
        else:
            lines.append("### General")
        if pa:
            lines.append("**Accomplished**")
            for a in pa:
                label = f"{a.task} — {a.outcome}" if a.outcome else a.task
                tags = f" {' '.join(f'#{t}' for t in a.tags)}" if a.tags else ""
                lines.append(f"- {label}{tags}")
        if pt:
            lines.append("\n**In Progress**")
            for t in sorted(pt, key=lambda t: t.due_date or "9999"):
                due = f" (due {t.due_date})" if t.due_date else ""
                tags = f" {' '.join(f'#{tag}' for tag in t.tags)}" if t.tags else ""
                lines.append(f"- {t.title}{due}{tags}")
        if pd:
            lines.append("\n**Waiting On**")
            for d in pd:
                tags = f" {' '.join(f'#{t}' for t in d.tags)}" if d.tags else ""
                lines.append(f"- {d.item} — {d.owner} ({d.age}d){tags}")
        if pr:
            lines.append("\n**Risks**")
            for r in pr:
                tags = f" {' '.join(f'#{t}' for t in r.tags)}" if r.tags else ""
                lines.append(f"- [{r.severity}] {r.description} (owner: {r.owner}){tags}")
        lines.append("")

    lines.append("\n### Resolved Dependencies")
    if data.get("resolved_deps"):
        for d in data["resolved_deps"]:
            lines.append(f"- {d['item']} — {d['owner']} (resolved {d['resolved']})")
            if d["notes"]: lines.append(f"  Notes: {d['notes']}")
    else:
        lines.append("- None")

    lines.append("\n### Resolved Risks")
    if data.get("resolved_risks"):
        for r in data["resolved_risks"]:
            lines.append(f"- {r['item']} [{r['severity']}] — {r['owner']} (resolved {r['resolved']})")
            if r["notes"]: lines.append(f"  Notes: {r['notes']}")
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
