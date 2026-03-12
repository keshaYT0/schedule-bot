import json
from datetime import datetime
from pathlib import Path
from config import TZ, DAYS_RU

_data_path = Path(__file__).parent / "data" / "schedule.json"

with open(_data_path, encoding="utf-8") as f:
    SCHEDULE = json.load(f)


def _to_minutes(time_str: str) -> int:
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def now_almaty() -> datetime:
    return datetime.now(TZ)


def format_day(day_name: str) -> str:
    lessons = SCHEDULE.get(day_name)
    if not lessons:
        return "Выходной. Пар нет."

    lines = []
    for i, lesson in enumerate(lessons, start=4):
        lines.append(
            f"{i} пара · {lesson['start']}–{lesson['end']}\n"
            f"{lesson['name']} — {lesson['teacher']} · {lesson['room']}"
        )
    return "\n\n".join(lines)


def current_lesson(day_name: str, current_minutes: int) -> dict | None:
    for lesson in SCHEDULE.get(day_name, []):
        start = _to_minutes(lesson["start"])
        end = _to_minutes(lesson["end"])
        if start <= current_minutes <= end:
            return {**lesson, "left": end - current_minutes}
    return None
