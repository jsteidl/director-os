from datetime import date, timedelta

WEEK_PATTERN = [4, 5, 4]  # repeats across 4 quarters = 12 periods

_FY_STARTS = {
    2026: date(2026, 2, 1),
    2027: date(2027, 1, 31),
}


def fy_start(fy: int) -> date:
    if fy in _FY_STARTS:
        return _FY_STARTS[fy]
    anchor = date(fy, 2, 1)
    dow = anchor.weekday()  # Mon=0 ... Sun=6
    days_since_sun = (dow + 1) % 7
    prev_sun = anchor - timedelta(days=days_since_sun)
    next_sun = prev_sun + timedelta(weeks=1)
    return prev_sun if (anchor - prev_sun).days <= (next_sun - anchor).days else next_sun


def get_fiscal_info(d: date) -> dict:
    fy = d.year
    if d < fy_start(fy):
        fy -= 1
    start = fy_start(fy)
    week_num = (d - start).days // 7
    weeks_accum = 0
    for q in range(4):
        for p_in_q, weeks in enumerate(WEEK_PATTERN):
            if week_num < weeks_accum + weeks:
                period = q * 3 + p_in_q + 1
                week_start = start + timedelta(weeks=week_num)
                return {
                    "fy": fy,
                    "quarter": q + 1,
                    "period": period,
                    "week": week_num - weeks_accum + 1,
                    "week_start": week_start,
                    "week_end": week_start + timedelta(days=6),
                }
            weeks_accum += weeks
    # 53rd week
    week_start = start + timedelta(weeks=week_num)
    return {"fy": fy, "quarter": 4, "period": 12, "week": week_num - weeks_accum + 1,
            "week_start": week_start, "week_end": week_start + timedelta(days=6)}


def get_period_weeks(fy: int, period: int) -> list:
    start = fy_start(fy)
    week_offset = 0
    for q in range(4):
        for p_in_q, weeks in enumerate(WEEK_PATTERN):
            p = q * 3 + p_in_q + 1
            if p == period:
                return [
                    [start + timedelta(weeks=week_offset + w, days=d) for d in range(7)]
                    for w in range(weeks)
                ]
            week_offset += weeks
    return []


def period_label(fy: int, period: int) -> str:
    q = (period - 1) // 3 + 1
    weeks = WEEK_PATTERN[(period - 1) % 3]
    return f"FY{fy % 100}  Q{q}  P{period}  ({weeks}wk)"
