from datetime import date, timedelta

DUE_SHORTHANDS = {
    "t": 0, "today": 0,
    "tm": 1, "tomorrow": 1,
    "w": 7, "week": 7,
    "2w": 14,
}

DUE_PLACEHOLDER = "YYYY-MM-DD · t · tm · w · 2w · +N"
DUE_ERROR = "Use YYYY-MM-DD, t, tm, w, 2w, or +N"


def resolve_due(value: str) -> tuple[str, bool]:
    """Return (resolved_date_str, is_valid). Empty string is valid (no due date)."""
    if not value:
        return "", True
    lower = value.strip().lower()
    if lower in DUE_SHORTHANDS:
        return (date.today() + timedelta(days=DUE_SHORTHANDS[lower])).isoformat(), True
    if lower.startswith("+"):
        try:
            return (date.today() + timedelta(days=int(lower[1:]))).isoformat(), True
        except ValueError:
            return value, False
    try:
        date.fromisoformat(value.strip())
        return value.strip(), True
    except ValueError:
        return value, False


SINCE_PLACEHOLDER = "YYYY-MM-DD · t · y · -N · -2w · lw"
SINCE_ERROR = "Use YYYY-MM-DD, t, y, -N, -2w, or lw"


def resolve_since(value: str) -> tuple[str, bool]:
    """Return (resolved_date_str, is_valid) for past-facing since-date inputs."""
    if not value:
        return "", False
    lower = value.strip().lower()
    today = date.today()
    if lower in ("t", "today"):
        return today.isoformat(), True
    if lower in ("y", "yesterday"):
        return (today - timedelta(days=1)).isoformat(), True
    if lower in ("lw", "lastweek"):
        return (today - timedelta(days=today.weekday())).isoformat(), True
    if lower.startswith("-"):
        rest = lower[1:]
        if rest.endswith("w"):
            try:
                return (today - timedelta(weeks=int(rest[:-1]))).isoformat(), True
            except ValueError:
                return value, False
        try:
            return (today - timedelta(days=int(rest))).isoformat(), True
        except ValueError:
            return value, False
    try:
        date.fromisoformat(value.strip())
        return value.strip(), True
    except ValueError:
        return value, False
