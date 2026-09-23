import re
from datetime import date
from models import Event
from parser._core import _clean, load_log, save_log
from parser._files import get_events_file


def get_events() -> list:
    path = get_events_file()
    if not path.exists():
        path.write_text("# Events\n\n", encoding="utf-8")
    content = path.read_text(encoding="utf-8")
    events = []
    for m in re.finditer(
        r"- (.*?) \| Date: (\d{4}-\d{2}-\d{2}) \| Type: (.*?) \| Location: (.*?) \| RemindDays: (\d+)",
        content,
    ):
        events.append(Event(
            title=m.group(1), date=m.group(2), type=m.group(3),
            location=m.group(4), remind_days=int(m.group(5)),
        ))
    return events


def add_event(title, event_date, type_, location, remind_days=0):
    path = get_events_file()
    content = path.read_text(encoding="utf-8")
    title, location = _clean(title), _clean(location)
    line = f"- {title} | Date: {event_date} | Type: {type_} | Location: {location} | RemindDays: {remind_days}\n"
    content += line
    path.write_text(content, encoding="utf-8")


def edit_event(old_title, old_date, title, event_date, type_, location, remind_days=0):
    path = get_events_file()
    content = path.read_text(encoding="utf-8")
    title, location = _clean(title), _clean(location)
    pattern = re.compile(
        r"- " + re.escape(old_title) + r" \| Date: " + re.escape(old_date) + r" \| Type: .*? \| Location: .*? \| RemindDays: \d+\n"
    )
    new_line = f"- {title} | Date: {event_date} | Type: {type_} | Location: {location} | RemindDays: {remind_days}\n"
    content = pattern.sub(new_line, content, count=1)
    path.write_text(content, encoding="utf-8")


def delete_event(title, event_date):
    path = get_events_file()
    content = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"- " + re.escape(title) + r" \| Date: " + re.escape(event_date) + r" \| Type: .*? \| Location: .*? \| RemindDays: \d+\n"
    )
    content = pattern.sub("", content, count=1)
    path.write_text(content, encoding="utf-8")


def check_event_notifications():
    today = date.today()
    events = get_events()
    notes_to_add = []
    for e in events:
        try:
            event_date = date.fromisoformat(e.date)
        except ValueError:
            continue
        days_away = (event_date - today).days
        if days_away == 0:
            notes_to_add.append(f"[Event] {e.title} ({e.type}, {e.location})")
        elif 0 < days_away <= e.remind_days:
            notes_to_add.append(f"[Reminder] {e.title} in {days_away}d ({e.type}, {e.location})")
    if not notes_to_add:
        return
    content = load_log()
    today_str = today.isoformat()
    for note in notes_to_add:
        if note in content:
            continue
        pattern = re.compile(
            r"(#### " + re.escape(today_str) + r".*?##### Notes\n)(.*?)(?=\n#### |\Z)", re.S,
        )
        match = pattern.search(content)
        if match:
            content = content[:match.end(2)] + f"- {note}\n" + content[match.end(2):]
        else:
            entry = (
                f"\n\n#### {today_str}\n\n"
                f"##### Priorities\n\n"
                f"##### Accomplished\n\n"
                f"##### Blocked\n\n"
                f"##### Notes\n\n"
                f"- {note}\n"
            )
            content += entry
    save_log(content)
