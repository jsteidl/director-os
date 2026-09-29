import tomllib
from datetime import datetime, date, timezone, timedelta
from pathlib import Path


WINDOWS_TZ_OFFSETS = {
    "Pacific Standard Time":  -8,
    "Pacific Daylight Time":  -7,
    "Mountain Standard Time": -7,
    "Mountain Daylight Time": -6,
    "Central Standard Time":  -6,
    "Central Daylight Time":  -5,
    "Eastern Standard Time":  -5,
    "Eastern Daylight Time":  -4,
    "UTC":                     0,
}


def _get_ics_path() -> Path | None:
    config_path = Path(__file__).parent.parent / "config.toml"
    if not config_path.exists():
        return None
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    p = config.get("calendar_ics_path")
    return Path(p) if p else None


def _resolve_dt(dt_prop) -> datetime | None:
    if dt_prop is None:
        return None
    dt = dt_prop.dt
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    if dt.tzinfo is not None:
        return dt.astimezone(tz=None).replace(tzinfo=None)
    tzid = str(dt_prop.params.get("TZID", "")).strip('"')
    if tzid:
        offset_hours = WINDOWS_TZ_OFFSETS.get(tzid)
        if offset_hours is not None:
            tz = timezone(timedelta(hours=offset_hours))
            return dt.replace(tzinfo=tz).astimezone(tz=None).replace(tzinfo=None)
    return dt


def get_agenda(target_date: date | None = None) -> list[dict]:
    ics_path = _get_ics_path()
    if not ics_path or not ics_path.exists():
        return []

    try:
        from icalendar import Calendar
    except ImportError:
        return []

    if target_date is None:
        target_date = date.today()

    try:
        cal = Calendar.from_ical(ics_path.read_bytes())
    except Exception:
        return []

    events = []
    for component in cal.walk():
        if component.name != "VEVENT":
            continue
        busy = str(component.get("X-MICROSOFT-CDO-BUSYSTATUS", "BUSY")).upper()
        if busy == "FREE":
            continue
        start = _resolve_dt(component.get("DTSTART"))
        end   = _resolve_dt(component.get("DTEND"))
        if start is None or start.date() != target_date:
            continue
        summary = str(component.get("SUMMARY", "")).split(";")[0].strip()
        location = str(component.get("LOCATION", "")).strip()
        all_day = (start.hour == 0 and start.minute == 0
                   and (end is None or (end.hour == 0 and end.minute == 0)))
        events.append({
            "summary":  summary,
            "start":    start,
            "end":      end,
            "location": location,
            "all_day":  all_day,
            "tentative": busy == "TENTATIVE",
        })

    events.sort(key=lambda e: e["start"])
    return events


def format_agenda_line(e: dict) -> str:
    if e["all_day"]:
        time_str = "All day"
        dur_str = ""
    else:
        time_str = e["start"].strftime("%I:%M %p").lstrip("0")
        if e["end"]:
            mins = int((e["end"] - e["start"]).total_seconds() / 60)
            if mins > 0:
                h, m = divmod(mins, 60)
                dur_str = f" ({h}h{m:02d}m)" if h else f" ({m}m)"
            else:
                dur_str = ""
        else:
            dur_str = ""
    tent = " [dim]~[/dim]" if e["tentative"] else ""
    loc = f" [dim]{e['location']}[/dim]" if e["location"] else ""
    return f"  {time_str}{dur_str}  {e['summary']}{loc}{tent}"
