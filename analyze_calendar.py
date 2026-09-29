"""
analyze_calendar.py — Meeting time analysis from ICS file.

Usage:
    python analyze_calendar.py              # current month
    python analyze_calendar.py 2026-09      # specific month
    python analyze_calendar.py 2026-09 2026-10  # date range
"""

import sys
import html
import tomllib
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


NOISE_PATTERNS = [
    "ooo", "pto", "out of office", "out of the office", "vacation",
    "lunch", "focus", "me time", "busy", "work", "stuff to do",
    "this, that", "pay day", "private appointment",
]


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
    config_path = Path(__file__).parent / "config.toml"
    if not config_path.exists():
        return None
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    p = config.get("calendar_history_ics_path") or config.get("calendar_ics_path")
    return Path(p) if p else None


def _resolve_dt(dt_prop):
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


def _component_to_event(component) -> dict | None:
    busy = str(component.get("X-MICROSOFT-CDO-BUSYSTATUS", "BUSY")).upper()
    if busy in ("FREE", "OOF"):
        return None
    start = _resolve_dt(component.get("DTSTART"))
    end   = _resolve_dt(component.get("DTEND"))
    if start is None:
        return None
    duration_mins = int((end - start).total_seconds() / 60) if end else 0
    if duration_mins <= 0 or duration_mins >= 480:
        return None
    raw_summary = component.get("SUMMARY", "")
    summary = html.unescape(str(raw_summary).split(";")[0].strip())
    summary_lower = summary.lower()
    if not summary_lower:
        return None
    if any(p in summary_lower for p in NOISE_PATTERNS):
        return None
    if summary_lower.startswith(("following:", "declined:")):
        return None
    return {
        "date":          start.date(),
        "summary":       summary,
        "start":         start,
        "duration_mins": duration_mins,
        "tentative":     busy == "TENTATIVE",
    }


def _load_cal(ics_path: Path):
    from icalendar import Calendar
    return Calendar.from_ical(ics_path.read_bytes())


def load_events(start_date: date, end_date: date, include_tentative: bool = True, min_duration: int = 0) -> list[dict]:
    ics_path = _get_ics_path()
    if not ics_path or not ics_path.exists():
        print(f"ICS file not found: {ics_path}")
        print("Export from Outlook: File > Save Calendar > More Options > set date range.")
        sys.exit(1)

    try:
        import recurring_ical_events
        cal = _load_cal(ics_path)
        components = recurring_ical_events.of(cal).between(
            datetime(start_date.year, start_date.month, start_date.day),
            datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59),
        )
    except ImportError:
        cal = _load_cal(ics_path)
        components = [c for c in cal.walk() if c.name == "VEVENT"]

    events = []
    for component in components:
        e = _component_to_event(component)
        if e and start_date <= e["date"] <= end_date:
            events.append(e)

    # deduplicate — Outlook exports sometimes include organizer + attendee copies
    seen = set()
    deduped = []
    for e in events:
        key = (e["date"], e["start"].hour, e["start"].minute, e["summary"])
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    deduped.sort(key=lambda e: e["start"])
    return deduped


def fmt_duration(mins: int) -> str:
    h, m = divmod(mins, 60)
    return f"{h}h {m:02d}m" if h else f"{m}m"


def analyze(events: list[dict], start_date: date, end_date: date):
    if not events:
        print("No meetings found in this period.")
        return

    # --- aggregate by day ---
    by_day: dict[date, list[dict]] = defaultdict(list)
    for e in events:
        by_day[e["date"]].append(e)

    # work days in range (Mon–Fri)
    work_days = [start_date + timedelta(days=i)
                 for i in range((end_date - start_date).days + 1)
                 if (start_date + timedelta(days=i)).weekday() < 5]
    days_with_meetings = sorted(by_day.keys())

    total_mins = sum(e["duration_mins"] for e in events)
    total_meetings = len(events)
    avg_mins_per_work_day = total_mins / len(work_days) if work_days else 0
    avg_meetings_per_day = total_meetings / len(work_days) if work_days else 0

    # --- by weekday ---
    weekday_mins: dict[int, int] = defaultdict(int)
    weekday_count: dict[int, int] = defaultdict(int)
    weekday_days: dict[int, set] = defaultdict(set)
    for e in events:
        wd = e["date"].weekday()
        weekday_mins[wd] += e["duration_mins"]
        weekday_count[wd] += 1
        weekday_days[wd].add(e["date"])

    # --- by week ---
    week_mins: dict[date, int] = defaultdict(int)
    week_count: dict[date, int] = defaultdict(int)
    for e in events:
        week_start = e["date"] - timedelta(days=e["date"].weekday())
        week_mins[week_start] += e["duration_mins"]
        week_count[week_start] += 1

    # --- top recurring meetings ---
    meeting_totals: dict[str, int] = defaultdict(int)
    meeting_counts: dict[str, int] = defaultdict(int)
    for e in events:
        meeting_totals[e["summary"]] += e["duration_mins"]
        meeting_counts[e["summary"]] += 1

    top_meetings = sorted(meeting_totals.items(), key=lambda x: x[1], reverse=True)[:10]

    # --- busiest / lightest days ---
    day_totals = {d: sum(e["duration_mins"] for e in evts) for d, evts in by_day.items()}
    busiest_day = max(day_totals, key=day_totals.get)
    lightest_day = min(day_totals, key=day_totals.get)

    # --- tentative ---
    tentative = [e for e in events if e["tentative"]]

    # ===================== OUTPUT =====================

    print(f"\n{'='*60}")
    print(f"  MEETING ANALYSIS  {start_date} → {end_date}")
    print(f"{'='*60}")

    print(f"\n── SUMMARY ──────────────────────────────────────────────")
    print(f"  Total meetings:        {total_meetings}")
    print(f"  Total meeting time:    {fmt_duration(total_mins)}")
    print(f"  Work days in period:   {len(work_days)}")
    print(f"  Days with meetings:    {len(days_with_meetings)}")
    print(f"  Avg meetings/work day: {avg_meetings_per_day:.1f}")
    print(f"  Avg time/work day:     {fmt_duration(int(avg_mins_per_work_day))}")
    if len(work_days) > 0:
        pct = (total_mins / (len(work_days) * 8 * 60)) * 100
        print(f"  % of 8h day in mtgs:   {pct:.0f}%")
    tentative_note = " (excluded; use --include-tentative to show)" if not tentative else ""
    print(f"  Tentative meetings:    {len(tentative)}{tentative_note}")

    print(f"\n── BY WEEKDAY ───────────────────────────────────────────")
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    for wd in range(5):
        if wd not in weekday_mins:
            continue
        n_days = len(weekday_days[wd])
        avg = weekday_mins[wd] // n_days if n_days else 0
        bar = "█" * (weekday_mins[wd] // 60)
        print(f"  {day_names[wd]}  {fmt_duration(weekday_mins[wd]):>10}  avg {fmt_duration(avg)}/day  {weekday_count[wd]} mtgs  {bar}")

    print(f"\n── BY WEEK ──────────────────────────────────────────────")
    for week_start in sorted(week_mins):
        bar = "█" * (week_mins[week_start] // 60)
        print(f"  w/o {week_start}  {fmt_duration(week_mins[week_start]):>10}  {week_count[week_start]:2d} mtgs  {bar}")

    print(f"\n── BUSIEST / LIGHTEST DAYS ──────────────────────────────")
    print(f"  Busiest:  {busiest_day}  {fmt_duration(day_totals[busiest_day])}  ({len(by_day[busiest_day])} meetings)")
    print(f"  Lightest: {lightest_day}  {fmt_duration(day_totals[lightest_day])}  ({len(by_day[lightest_day])} meetings)")

    print(f"\n── TOP MEETINGS BY TIME ─────────────────────────────────")
    for summary, mins in top_meetings:
        count = meeting_counts[summary]
        avg = mins // count
        print(f"  {fmt_duration(mins):>10}  ({count}x, avg {fmt_duration(avg)})  {summary[:50]}")

    print()


def parse_date_arg(s: str) -> tuple[date, date]:
    """Parse 'YYYY-MM' or 'YYYY-MM-DD'. Returns (start, end) of that month or day."""
    if len(s) == 7:  # YYYY-MM
        y, m = int(s[:4]), int(s[5:7])
        start = date(y, m, 1)
        # last day of month
        if m == 12:
            end = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(y, m + 1, 1) - timedelta(days=1)
        return start, end
    else:
        d = date.fromisoformat(s)
        return d, d


def dump_raw(start_date: date, end_date: date):
    ics_path = _get_ics_path()
    if not ics_path or not ics_path.exists():
        print(f"ICS file not found: {ics_path}")
        print("Export from Outlook: File > Save Calendar > More Options > set date range.")
        return
    try:
        import recurring_ical_events
        cal = _load_cal(ics_path)
        components = recurring_ical_events.of(cal).between(
            datetime(start_date.year, start_date.month, start_date.day),
            datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59),
        )
    except ImportError:
        cal = _load_cal(ics_path)
        components = [c for c in cal.walk() if c.name == "VEVENT"]
    for component in components:
        start = _resolve_dt(component.get("DTSTART"))
        end   = _resolve_dt(component.get("DTEND"))
        if start is None or not (start_date <= start.date() <= end_date):
            continue
        busy = str(component.get("X-MICROSOFT-CDO-BUSYSTATUS", "BUSY")).upper()
        dur = int((end - start).total_seconds() / 60) if end else 0
        summary = html.unescape(str(component.get("SUMMARY", "")).split(";")[0].strip()[:50])
        summary_lower = summary.lower()
        if not summary_lower or any(p in summary_lower for p in NOISE_PATTERNS):
            continue
        if summary_lower.startswith(("following:", "declined:")):
            continue
        print(f"  {start.date()}  {start.strftime('%H:%M')}  {dur:4d}m  busy={busy:<10}  {summary}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    include_tentative = "--include-tentative" in sys.argv
    dump_raw_flag = "--raw" in sys.argv

    if len(args) == 0:
        today = date.today()
        start = date(today.year, today.month, 1)
        if today.month == 12:
            end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    elif len(args) == 1:
        start, end = parse_date_arg(args[0])
    else:
        start, _ = parse_date_arg(args[0])
        _, end   = parse_date_arg(args[1])

    if dump_raw_flag:
        print(f"\nRAW EVENTS (after noise filter) {start} -> {end}")
        dump_raw(start, end)
        sys.exit(0)

    events = load_events(start, end)
    if not include_tentative:
        events = [e for e in events if not e["tentative"]]
    analyze(events, start, end)
