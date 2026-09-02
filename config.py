import os
import sys
import logging
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.critical("BOT_TOKEN не задан в переменных окружения!")
    sys.exit(1)

_chat_id_raw = os.getenv("CHAT_ID")
CHAT_ID = int(_chat_id_raw) if _chat_id_raw else None

TZ = ZoneInfo("Asia/Almaty")

REMINDER_BEFORE = 10          # напоминание за N минут до пары
MORNING_SUMMARY_TIME = "07:45"  # утренняя сводка расписания

DAYS_RU = {
    "Monday":    "Понедельник",
    "Tuesday":   "Вторник",
    "Wednesday": "Среда",
    "Thursday":  "Четверг",
    "Friday":    "Пятница",
    "Saturday":  "Суббота",
    "Sunday":    "Воскресенье",
}

DAYS_SHORT = {
    "Monday":    "Пн",
    "Tuesday":   "Вт",
    "Wednesday": "Ср",
    "Thursday":  "Чт",
    "Friday":    "Пт",
}

BELLS = [
    ("1 пара", "08:30", "10:00"),
    ("2 пара", "10:10", "11:40"),
    ("3 пара", "11:50", "13:20"),
    ("4 пара", "13:30", "15:00"),
    ("5 пара", "15:10", "16:40"),
    ("6 пара", "16:50", "18:10"),
    ("7 пара", "18:15", "19:35"),
]

# ── Render keep-alive & WebApp ──────────────────────────────
#  RENDER_EXTERNAL_URL — the public URL assigned by Render,
#  e.g. "https://schedule-bot-xxxx.onrender.com".
RENDER_EXTERNAL_URL: str | None = os.getenv("RENDER_EXTERNAL_URL")

#  WEBAPP_URL — URL for Telegram Mini App
WEBAPP_URL: str = os.getenv("WEBAPP_URL") or RENDER_EXTERNAL_URL or "http://localhost:8080"

#  Ping interval — must be shorter than Render's 15-min idle timeout.
KEEPALIVE_INTERVAL_SEC: int = int(os.getenv("KEEPALIVE_INTERVAL_SEC", "600"))

