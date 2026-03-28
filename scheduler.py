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


# ── форматирование одного дня ────────────────────────────────
def format_day(day_name: str) -> str:
    lessons = SCHEDULE.get(day_name)
    if not lessons:
        return "🏖 Выходной. Пар нет."

    lines = []
    for i, lesson in enumerate(lessons, start=4):
        lines.append(
            f"┌ <b>{i} пара</b>  ·  {lesson['start']} – {lesson['end']}\n"
            f"│ 📖 {lesson['name']}\n"
            f"│ 👨‍🏫 {lesson['teacher']}\n"
            f"└ 🏫 {lesson['room']}"
        )
    return "\n\n".join(lines)


# ── форматирование недели ────────────────────────────────────
def format_week() -> str:
    parts = []
    for eng, rus in DAYS_RU.items():
        lessons = SCHEDULE.get(eng)
        if not lessons:
            continue
        header = f"━━━  <b>{rus}</b>  ━━━"
        items = []
        for i, lesson in enumerate(lessons, start=4):
            items.append(
                f"  {i}. {lesson['start']}–{lesson['end']}  "
                f"<b>{lesson['name']}</b>\n"
                f"      {lesson['teacher']} · {lesson['room']}"
            )
        parts.append(header + "\n" + "\n".join(items))
    return "\n\n".join(parts) if parts else "Расписание пусто."


# ── текущая пара ─────────────────────────────────────────────
def current_lesson(day_name: str, current_minutes: int) -> dict | None:
    for i, lesson in enumerate(SCHEDULE.get(day_name, []), start=4):
        start = _to_minutes(lesson["start"])
        end = _to_minutes(lesson["end"])
        if start <= current_minutes <= end:
            elapsed = current_minutes - start
            total = end - start
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
    for i, lesson in enumerate(SCHEDULE.get(day_name, []), start=4):
        start = _to_minutes(lesson["start"])
        if start > current_minutes:
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
    for i, lesson in enumerate(SCHEDULE.get(day_name, []), start=4):
        start = _to_minutes(lesson["start"])
        remind_at = start - before_min
        if remind_at < 0:
            continue
        h, m = divmod(remind_at, 60)
        result.append({
            "time_hhmm": f"{h:02d}:{m:02d}",
            "lesson_name": lesson["name"],
            "lesson_num": i,
            "start_time": lesson["start"],
            "room": lesson["room"],
        })
    return result
