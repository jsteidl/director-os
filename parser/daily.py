import re
from datetime import date, timedelta
from models import DailyLogEntry
from parser._core import load_log, save_log
from parser._files import get_log_file
from parser._core import _get_logs_path


def _to_markdown_list(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(f"- {line}" for line in lines)


def parse_daily_log(content):
    entries = []
    current_entry = None
    current_section = None
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#### ") and not line.startswith("#####"):
            current_entry = DailyLogEntry(
                date=line.replace("#### ", "").strip(),
                priorities=[], accomplished=[], blocked=[], notes=[],
            )
            entries.append(current_entry)
            current_section = None
            continue
        if line.startswith("##### "):
            current_section = line.replace("##### ", "").strip().lower()
            continue
        if line.startswith("- ") and current_entry is not None and current_section is not None:
            item = line[2:].strip()
            if current_section == "priorities":
                current_entry.priorities.append(item)
            elif current_section == "accomplished":
                current_entry.accomplished.append(item)
            elif current_section == "blocked":
                current_entry.blocked.append(item)
            elif current_section == "notes":
                current_entry.notes.append(item)
    entries.sort(key=lambda e: e.date, reverse=True)
    return entries


def get_today_entry():
    content = load_log()
    today = date.today().isoformat()
    for entry in parse_daily_log(content):
        if entry.date == today:
            return entry
    return None


def get_all_daily_entries():
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


def add_daily_entry(priorities, accomplished, blocked, notes):
    content = load_log()
    today = date.today().isoformat()
    entry = f"""


#### {today}

##### Priorities

{_to_markdown_list(priorities)}

##### Accomplished

{_to_markdown_list(accomplished)}

##### Blocked

{_to_markdown_list(blocked)}

##### Notes

{_to_markdown_list(notes)}


"""
    content += entry
    save_log(content)
    return True


def edit_daily_entry(entry_date, priorities, accomplished, blocked, notes):
    content = load_log()
    pattern = re.compile(r"#### " + re.escape(entry_date) + r".*?(?=\n#### |\Z)", re.S)
    new_entry = f"""#### {entry_date}

##### Priorities

{_to_markdown_list(priorities)}

##### Accomplished

{_to_markdown_list(accomplished)}

##### Blocked

{_to_markdown_list(blocked)}

##### Notes

{_to_markdown_list(notes)}

"""
    content = pattern.sub(new_entry, content, count=1)
    save_log(content)


def get_daily_log_text():
    content = load_log()
    marker = "### Daily Log"
    if marker not in content:
        return "No daily log entries found."
    return "DAILY LOG\n=========\n\n" + content.split(marker, 1)[1].strip()


def get_weekly_summary():
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    content = load_log()
    from parser.tasks import get_tasks
    from parser.accomplishments import get_accomplishments
    week_entries = [e for e in parse_daily_log(content) if e.date >= week_start.isoformat()]
    accomplishments = [a for a in get_accomplishments() if a.completed >= week_start.isoformat()]
    return {
        "entries": week_entries,
        "accomplishments": accomplishments,
        "open_tasks": get_tasks(),
        "week_start": week_start.isoformat(),
        "week_end": today.isoformat(),
    }


def save_weekly_review(notes, week_start, week_end):
    content = load_log()
    entry = (
        f"\n\n#### Weekly Review: {week_start} to {week_end}\n\n"
        f"##### Notes\n\n"
        f"{_to_markdown_list(notes)}\n"
    )
    content += entry
    save_log(content)
