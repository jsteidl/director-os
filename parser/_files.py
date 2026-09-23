from datetime import date
from parser._core import _get_logs_path


def get_log_file():
    filename = f"{date.today():%Y-%m}-Director-Log.md"
    return _get_logs_path() / filename


def get_prev_log_file():
    today = date.today()
    if today.month == 1:
        prev = today.replace(year=today.year - 1, month=12, day=1)
    else:
        prev = today.replace(month=today.month - 1, day=1)
    return _get_logs_path() / f"{prev:%Y-%m}-Director-Log.md"


def get_events_file():
    return _get_logs_path() / "events.md"


def get_projects_file():
    return _get_logs_path() / "projects.md"


def get_scratch_file():
    return _get_logs_path() / "scratch.md"
