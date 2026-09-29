#!/usr/bin/env python3
"""
test_outlook.py — verify ICS calendar parsing before integrating into director_os

Run with:
    python test_outlook.py
    python test_outlook.py --file /path/to/calendar.ics
    python test_outlook.py --date 2026-09-29
"""

import argparse
from datetime import datetime, date, timezone
from pathlib import Path

try:
    from icalendar import Calendar
except ImportError:
    print("ERROR: icalendar not installed. Run: pip install icalendar")
    raise SystemExit(1)

# Windows timezone name → UTC offset (handles DST manually via tzdata)
# icalendar handles IANA names natively; Windows names need mapping
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


def _resolve_dt(dt_prop) -> datetime | None:
    """Normalize a DTSTART/DTEND property to a naive local datetime."""
    if dt_prop is None:
        return None
    dt = dt_prop.dt

    # All-day event — date object, not datetime
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime(dt.year, dt.month, dt.day, 0, 0, 0)

    # Already UTC-aware
    if dt.tzinfo is not None:
        return dt.astimezone(tz=None).replace(tzinfo=None)

    # Try to get TZID from the property parameters
    tzid = str(dt_prop.params.get("TZID", ""))
    if tzid:
        # Strip surrounding quotes if present
        tzid = tzid.strip('"')
        offset_hours = WINDOWS_TZ_OFFSETS.get(tzid)
        if offset_hours is not None:
            from datetime import timedelta
            tz = timezone(timedelta(hours=offset_hours))
            return dt.replace(tzinfo=tz).astimezone(tz=None).replace(tzinfo=None)

    return dt


def get_events_for_date(ics_path: Path, target_date: date) -> list[dict]:
    content = ics_path.read_bytes()
    cal = Calendar.from_ical(content)

    events = []
    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        busy_status = str(component.get("X-MICROSOFT-CDO-BUSYSTATUS", "BUSY")).upper()
        if busy_status == "FREE":
            continue

        start = _resolve_dt(component.get("DTSTART"))
        end   = _resolve_dt(component.get("DTEND"))
        if start is None:
            continue

        if start.date() != target_date:
            continue

        summary = str(component.get("SUMMARY", "")).split(";")[0].strip()
        location = str(component.get("LOCATION", "")).strip()
        all_day = start.hour == 0 and start.minute == 0 and (end is None or (end.hour == 0 and end.minute == 0))

        events.append({
            "summary":  summary,
            "start":    start,
            "end":      end,
            "location": location,
            "all_day":  all_day,
            "status":   busy_status,
        })

    events.sort(key=lambda e: e["start"])
    return events


def format_time(dt: datetime) -> str:
    return dt.strftime("%I:%M %p").lstrip("0")


def format_duration(start: datetime, end: datetime | None) -> str:
    if end is None:
        return ""
    mins = int((end - start).total_seconds() / 60)
    if mins <= 0:
        return ""
    h, m = divmod(mins, 60)
    if h == 0:
        return f"{m}m"
    return f"{h}h" if m == 0 else f"{h}h{m}m"


def main():
    parser = argparse.ArgumentParser(description="Test ICS calendar parsing")
    parser.add_argument("--file", default=None, help="Path to .ics file (default: auto-detect from config.toml)")
    parser.add_argument("--date", default=None, help="Date to show (YYYY-MM-DD, default: today)")
    args = parser.parse_args()

    # Resolve ICS path
    if args.file:
        ics_path = Path(args.file)
    else:
        # Try to read from config.toml
        try:
            import tomllib
            config_path = Path(__file__).parent / "config.toml"
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
            cal_path = config.get("calendar_ics_path")
            if not cal_path:
                print("ERROR: No --file specified and no calendar_ics_path in config.toml")
                raise SystemExit(1)
            ics_path = Path(cal_path)
        except FileNotFoundError:
            print("ERROR: config.toml not found. Use --file to specify the ICS path.")
            raise SystemExit(1)

    if not ics_path.exists():
        print(f"ERROR: File not found: {ics_path}")
        raise SystemExit(1)

    target = date.fromisoformat(args.date) if args.date else date.today()
    print(f"\nCalendar: {ics_path.name}")
    print(f"Date:     {target.strftime('%A, %B %d %Y')}\n")

    events = get_events_for_date(ics_path, target)

    if not events:
        print("No events found for this date.")
        return

    for e in events:
        if e["all_day"]:
            time_str = "All day "
            dur_str  = ""
        else:
            time_str = f"{format_time(e['start']):8}"
            dur_str  = f" ({format_duration(e['start'], e['end'])})"

        loc = f"  [{e['location']}]" if e["location"] else ""
        tent = " ~" if e["status"] == "TENTATIVE" else ""
        print(f"  {time_str}{dur_str}  {e['summary']}{loc}{tent}")

    print(f"\n{len(events)} event(s)")


if __name__ == "__main__":
    main()
