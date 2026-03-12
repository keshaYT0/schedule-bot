import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
TZ = ZoneInfo("Asia/Almaty")

DAYS_RU = {
    "Monday":    "Понедельник",
    "Tuesday":   "Вторник",
    "Wednesday": "Среда",
    "Thursday":  "Четверг",
    "Friday":    "Пятница",
    "Saturday":  "Суббота",
    "Sunday":    "Воскресенье",
}

BELLS = [
    ("4 пара", "13:30", "15:00"),
    ("5 пара", "15:10", "16:40"),
    ("6 пара", "16:50", "18:10"),
    ("7 пара", "18:15", "19:35"),
]
