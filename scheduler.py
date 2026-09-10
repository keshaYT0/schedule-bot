import json
from datetime import datetime
from pathlib import Path
from config import TZ, DAYS_RU, DAYS_SHORT

_data_path = Path(__file__).parent / "schedule.json"

with open(_data_path, encoding="utf-8") as f:
    SCHEDULE = json.load(f)


def _to_minutes(time_str: str) -> int:
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def now_almaty() -> datetime:
    return datetime.now(TZ)


# ── визуальный прогресс-бар ──────────────────────────────────
def progress_bar(current: int, total: int, length: int = 10) -> str:
    if total <= 0:
        return "░" * length
    ratio = min(max(current / total, 0.0), 1.0)
    filled = round(length * ratio)
    bar = "▓" * filled + "░" * (length - filled)
    pct = round(ratio * 100)
    return f"{bar} {pct}%"


def get_lesson_num(start_time: str) -> int:
    """Определяет номер пары по времени ее начала на основе BELLS из config.py."""
    from config import BELLS
    for name, start, _ in BELLS:
        parts = name.split()
        if parts and parts[0].isdigit() and start == start_time:
            return int(parts[0])
    return 4  # фоллбек по умолчанию


def get_shift_info(day_name: str) -> dict:
    """Определяет смену дня (1 смена - с утра / 2 смена - с обеда)."""
    lessons = SCHEDULE.get(day_name, [])
    if not lessons:
        return {"shift": 0, "name": "Выходной", "start": None, "label": "Выходной день"}
    first_start = lessons[0]["start"]
    h = int(first_start.split(":")[0])
    if h < 12:
        return {
            "shift": 1,
            "name": "1 смена",
            "start": first_start,
            "label": "1 смена (с утра)",
        }
    else:
        return {
            "shift": 2,
            "name": "2 смена",
            "start": first_start,
            "label": "2 смена (с обеда)",
        }


# ── форматирование одного дня ────────────────────────────────
def format_day(day_name: str) -> str:
    lessons = SCHEDULE.get(day_name)
    if not lessons:
        return "<blockquote>Выходной день. Занятий нет.</blockquote>"

    shift_info = get_shift_info(day_name)
    shift_badge = f"<blockquote><b>{shift_info['label'].upper()}</b> · Начало в {shift_info['start']}</blockquote>\n\n" if shift_info.get("shift") else ""

    lines = []
    for lesson in lessons:
        i = lesson.get("num") or get_lesson_num(lesson["start"])
        room = f" · {lesson['room']}" if lesson.get("room") and lesson["room"] != "—" else ""
        lines.append(
            f"<blockquote><b>{i} ПАРА</b>  <code>[{lesson['start']} – {lesson['end']}]</code>\n"
            f"<b>{lesson['name']}</b>\n"
            f"▸ {lesson['teacher']}{room}</blockquote>"
        )
    return shift_badge + "\n".join(lines)



# ── форматирование недели ────────────────────────────────────
def format_week() -> str:
    parts = []
    for eng, rus in DAYS_RU.items():
        lessons = SCHEDULE.get(eng)
        if not lessons:
            continue
        shift_info = get_shift_info(eng)
        shift_str = f" · {shift_info['name']}" if shift_info.get("shift") else ""
        header = f"━━━  <b>{rus}{shift_str}</b>  ━━━"
        items = []
        for lesson in lessons:
            i = get_lesson_num(lesson["start"])
            items.append(
                f"  {i}. {lesson['start']}–{lesson['end']}  "
                f"<b>{lesson['name']}</b>\n"
                f"      {lesson['teacher']} · {lesson['room']}"
            )
        parts.append(header + "\n" + "\n".join(items))
    return "\n\n".join(parts) if parts else "Расписание пусто."


# ── текущая пара ─────────────────────────────────────────────
def current_lesson(day_name: str, current_minutes: int) -> dict | None:
    for lesson in SCHEDULE.get(day_name, []):
        start = _to_minutes(lesson["start"])
        end = _to_minutes(lesson["end"])
        if start <= current_minutes <= end:
            elapsed = current_minutes - start
            total = end - start
            i = get_lesson_num(lesson["start"])
            return {
                **lesson,
                "num": i,
                "left": end - current_minutes,
                "elapsed": elapsed,
                "total": total,
                "bar": progress_bar(elapsed, total),
            }
    return None


# ── следующая пара ───────────────────────────────────────────
def next_lesson(day_name: str, current_minutes: int) -> dict | None:
    for lesson in SCHEDULE.get(day_name, []):
        start = _to_minutes(lesson["start"])
        if start > current_minutes:
            i = get_lesson_num(lesson["start"])
            return {
                **lesson,
                "num": i,
                "until": start - current_minutes,
            }
    return None


# ── все точки напоминаний на день ────────────────────────────
def get_reminder_times(day_name: str, before_min: int) -> list[dict]:
    """Возвращает список {time_hhmm, lesson_name, lesson_num}."""
    result = []
    for lesson in SCHEDULE.get(day_name, []):
        start = _to_minutes(lesson["start"])
        remind_at = start - before_min
        if remind_at < 0:
            continue
        h, m = divmod(remind_at, 60)
        i = get_lesson_num(lesson["start"])
        result.append({
            "time_hhmm": f"{h:02d}:{m:02d}",
            "lesson_name": lesson["name"],
            "lesson_num": i,
            "start_time": lesson["start"],
            "room": lesson["room"],
        })
    return result


def get_status() -> dict:
    now = now_almaty()
    day_name = now.strftime("%A")
    day_ru = DAYS_RU.get(day_name, day_name)
    current_minutes = now.hour * 60 + now.minute
    is_weekend = day_name in ("Saturday", "Sunday")

    curr = current_lesson(day_name, current_minutes) if not is_weekend else None
    nxt = next_lesson(day_name, current_minutes) if not is_weekend else None

    if nxt:
        nxt = {**nxt, "starts_in": nxt.get("until", 0)}

    return {
        "day_name": day_name,
        "day_ru": day_ru,
        "date_str": now.strftime("%d.%m.%Y"),
        "time_str": now.strftime("%H:%M"),
        "is_weekend": is_weekend,
        "shift": get_shift_info(day_name),
        "current_lesson": curr,
        "next_lesson": nxt,
    }

