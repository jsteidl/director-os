import re
from datetime import date
from models import Accomplishment
from parser._core import extract_tags, strip_tags, _get_logs_path
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
                task=strip_tags(re.sub(r"\s*\+[\w]+", "", task.replace(" Mgr:true", "").replace(" Personal:true", ""))),
                outcome=outcome,
                completed=completed,
                tags=extract_tags(task),
                mgr="Mgr:true" in task,
                personal="Personal:true" in task,
                project=re.search(r"\+([\w]+)", task).group(1) if re.search(r"\+([\w]+)", task) else None,
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
        "tasks": tasks,
        "deps": get_dependencies(),
        "risks": get_risks(),
        "blocked": blocked,
        "resolved_deps": all_resolved_deps,
        "resolved_risks": all_resolved_risks,
    }


def save_update(since_date: str, data: dict) -> str:
    from widgets.tasks import PRIORITY_GLYPHS
    meta = get_project_meta()
    grouped = data.get("grouped", False)
    tasks = data.get("tasks", [])
    accomplishments = data.get("accomplished", [])
    deps = data.get("deps", [])
    risks = data.get("risks", [])

    lines = [f"## Update — Since {since_date}\n"]

    if grouped:
        all_projects = sorted(
            {i.project for i in [*tasks, *accomplishments, *deps, *risks] if i.project},
            key=str.lower
        )
        for project in all_projects:
            m = meta.get(project, {})
            display = m.get("display") or project
            description = m.get("description", "")
            pt = [i for i in tasks if i.project == project]
            pa = [i for i in accomplishments if i.project == project]
            pd = [i for i in deps if i.project == project]
            pr = [i for i in risks if i.project == project]
            if not any([pt, pa, pd, pr]):
                continue
            lines.append(f"### {display}")
            if description:
                lines.append(f"_{description}_\n")
            if pa:
                lines.append("**Accomplished**")
                for a in pa: lines.append(f"- {a.task}")
            if pt:
                lines.append("\n**In Progress**")
                for t in pt:
                    glyph = PRIORITY_GLYPHS.get(t.priority, "") + " " if t.priority else ""
                    due = f" (due {t.due_date})" if t.due_date else ""
                    lines.append(f"- {glyph}{t.title}{due}")
            if pd:
                lines.append("\n**Waiting On**")
                for d in pd: lines.append(f"- {d.item} — {d.owner} ({d.age}d)")
            if pr:
                lines.append("\n**Risks**")
                for r in pr: lines.append(f"- [{r.severity}] {r.description} (owner: {r.owner})")
            lines.append("")
        ut = [i for i in tasks if not i.project]
        ua = [i for i in accomplishments if not i.project]
        ud = [i for i in deps if not i.project]
        ur = [i for i in risks if not i.project]
        if any([ut, ua, ud, ur]):
            lines.append("### General")
            if ua:
                lines.append("**Accomplished**")
                for a in ua: lines.append(f"- {a.task}")
            if ut:
                lines.append("\n**In Progress**")
                for t in ut:
                    glyph = PRIORITY_GLYPHS.get(t.priority, "") + " " if t.priority else ""
                    due = f" (due {t.due_date})" if t.due_date else ""
                    lines.append(f"- {glyph}{t.title}{due}")
            if ud:
                lines.append("\n**Waiting On**")
                for d in ud: lines.append(f"- {d.item} — {d.owner} ({d.age}d)")
            if ur:
                lines.append("\n**Risks**")
                for r in ur: lines.append(f"- [{r.severity}] {r.description} (owner: {r.owner})")
            lines.append("")
    else:
        lines.append("### Accomplished")
        for a in accomplishments: lines.append(f"- {a.task}") if accomplishments else lines.append("- Nothing completed in this period")
        lines.append("\n### In Progress")
        if tasks:
            for t in tasks:
                glyph = PRIORITY_GLYPHS.get(t.priority, "") + " " if t.priority else ""
                due = f" (due {t.due_date})" if t.due_date else ""
                lines.append(f"- {glyph}{t.title}{due}")
        else:
            lines.append("- No open tasks")
        lines.append("\n### Waiting On")
        for d in deps: lines.append(f"- {d.item} — {d.owner} ({d.age}d)") if deps else lines.append("- Nothing pending")
        lines.append("\n### Risks")
        for r in risks: lines.append(f"- [{r.severity}] {r.description} (owner: {r.owner})") if risks else lines.append("- No risks to surface")

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
