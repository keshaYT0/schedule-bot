import os
import sys
import logging
from zoneinfo import ZoneInfo

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.critical("BOT_TOKEN не задан в переменных окружения!")
    sys.exit(1)

_chat_id_raw = os.getenv("CHAT_ID")
CHAT_ID = int(_chat_id_raw) if _chat_id_raw else None

TZ = ZoneInfo("Asia/Almaty")

REMINDER_BEFORE = 10          # напоминание за N минут до пары
MORNING_SUMMARY_TIME = "12:00"  # утренняя сводка расписания

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
    ("4 пара", "13:30", "15:00"),
    ("5 пара", "15:10", "16:40"),
    ("6 пара", "16:50", "18:10"),
    ("7 пара", "18:15", "19:35"),
]
