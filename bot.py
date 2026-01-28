import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# ТОКЕН И ID
TOKEN = "8444997622:AAGjmBYxYq79JxGT9kf8bu1n9lKmw5y_Ko0"
YOUR_CHAT_ID = 1380431564

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ПОЛНОЕ РАСПИСАНИЕ (ДЛЯ ЛОГИКИ "ЧТО СЕЙЧАС")
LESSONS_DATA = {
    "Monday": [
        (810, 900, "ООП", "Зейнулла Ж.А.", "301 к1"),
        (910, 1000, "Предпринимательство / Этика", "Кусманова А.Ж. / Акумбаева Д.Б.", "403 к2 / 504 к2"),
        (1010, 1090, "Базы данных", "Сычева Е.А.", "413 к2")
    ],
    "Tuesday": [
        (810, 900, "Микропроцессоры", "Сычева Е.А.", "413 к2"),
        (910, 1000, "ООП", "Зейнулла Ж.А.", "410 к2"),
        (1010, 1090, "Философия", "Каримова М.К.", "211 к2")
    ],
    "Wednesday": [
        (810, 900, "Микропроцессоры", "Сычева Е.А.", "413 к2"),
        (910, 1000, "Микропроцессоры", "Сычева Е.А.", "413 к2"),
        (1010, 1090, "Культурология", "Айтпаева А.Ж.", "409 к1"),
        (1095, 1175, "Политология", "Капсалямова Г.Т.", "131 к1")
    ],
    "Thursday": [
        (810, 900, "Основы права", "Канапина А.А.", "406 к2"),
        (910, 1000, "Прогр. в офисе", "Наурызбай М.М.", "301 к1"),
        (1010, 1090, "Web-дизайн", "Наурызбай М.М.", "301 к1"),
        (1095, 1175, "Физкультура", "Паненков А.В.", "Спортзал")
    ],
    "Friday": [
        (810, 900, "Мобильная робототехника", "Маликов В.В.", "413 к2"),
        (910, 1000, "Мобильная робототехника", "Маликов В.В.", "413 к2"),
        (1010, 1090, "MySQL", "Сабирханова А.О.", "412 к2"),
        (1095, 1175, "MySQL", "Сабирханова А.О.", "412 к2")
    ]
}

# ТЕКСТ ДЛЯ КНОПОК "НА СЕГОДНЯ / ЗАВТРА"
SCHEDULE_TEXT = {
    "Monday": "4️⃣ 13:30-15:00 | ООП (Зейнулла Ж.А., 301 к1)\n5️⃣ 15:10-16:40 | Предпр/Этика (403/504 к2)\n6️⃣ 16:50-18:10 | БД (Сычева Е.А., 413 к2)",
    "Tuesday": "4️⃣ 13:30-15:00 | Микропроцессоры (Сычева Е.А., 413 к2)\n5️⃣ 15:10-16:40 | ООП (Зейнулла Ж.А., 410 к2)\n6️⃣ 16:50-18:10 | Философия (Каримова М.К., 211 к2)",
    "Wednesday": "4️⃣ 13:30-15:00 | Микропроцессоры (Сычева Е.А., 413 к2)\n5️⃣ 15:10-16:40 | Микропроцессоры (Сычева Е.А., 413 к2)\n6️⃣ 16:50-18:10 | Культурология (Айтпаева А.Ж., 409 к1)\n7️⃣ 18:15-19:35 | Политология (Капсалямова Г.Т., 131 к1)",
    "Thursday": "4️⃣ 13:30-15:00 | Основы права (Канапина А.А., 406 к2)\n5️⃣ 15:10-16:40 | Прогр. в офисе (Наурызбай М.М., 301 к1)\n6️⃣ 16:50-18:10 | Web-дизайн (Наурызбай М.М., 301 к1)\n7️⃣ 18:15-19:35 | Физра (Паненков А.В.)",
    "Friday": "4️⃣ 13:30-15:00 | Мобильная робототехника (Маликов В.В., 413 к2)\n5️⃣ 15:10-16:40 | Мобильная робототехника (Маликов В.В., 413 к2)\n6️⃣ 16:50-18:10 | MySQL (Сабирханова А.О., 412 к2)\n7️⃣ 18:15-19:35 | MySQL (Сабирханова А.О., 412 к2)"
}

def get_main_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📅 На сегодня")
    builder.button(text="⏩ На завтра")
    builder.button(text="📍 Что сейчас?")
    builder.button(text="🔔 Звонки")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Жми на кнопки:", reply_markup=get_main_kb())

@dp.message(F.text == "🔔 Звонки")
async def send_calls(message: types.Message):
    await message.answer("<b>🔔 ЗВОНКИ (4-7 ПАРЫ):</b>\n4 ПАРА: 13:30 — 15:00\n5 ПАРА: 15:10 — 16:40\n6 ПАРА: 16:50 — 18:10\n7 ПАРА: 18:15 — 19:35")

@dp.message(F.text.in_(["📅 На сегодня", "⏩ На завтра"]))
async def send_sched(message: types.Message):
    days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    rus_days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]
    now = datetime.now()
    if message.text == "⏩ На завтра":
        now += timedelta(days=1)
    day_name = days_map[now.weekday()]
    day_rus = rus_days[now.weekday()]
    date_str = now.strftime("%d.%m")
    content = SCHEDULE_TEXT.get(day_name, "Пар нет, отдыхаем! 😎")
    await message.answer(f"<b>📅 {day_rus} ({date_str})</b>\n\n{content}")

@dp.message(F.text == "📍 Что сейчас?")
async def current_lesson(message: types.Message):
    now = datetime.now()
    current_time = now.hour * 60 + now.minute
    day_name = now.strftime("%A")
    date_str = now.strftime("%d.%m.%Y")
    
    if day_name not in LESSONS_DATA:
        await message.answer(f"📅 Сегодня {date_str}\nВыходной! Пар нет.")
        return

    for start, end, name, teacher, room in LESSONS_DATA[day_name]:
        if start <= current_time <= end:
            left = end - current_time
            text = (
                f"📅 <b>Дата:</b> {date_str}\n\n"
                f"🎓 <b>Пара:</b> {name}\n"
                f"👨‍🏫 <b>Преподаватель:</b> {teacher}\n"
                f"🚪 <b>Кабинет:</b> {room}\n\n"
                f"⏳ Бро, не переживай, пара закончится через <b>{left}</b> мин!"
            )
            await message.answer(text)
            return

    await message.answer(f"📅 <b>Дата:</b> {date_str}\nСейчас пар нет. Свобода! 🍻")

# --- СЛУЖЕБНЫЕ ЧАСТИ (БЕЗ ИЗМЕНЕНИЙ) ---
async def handle_health(request): return web.Response(text="Alive")
async def start_web_server():
    app = web.Application(); app.router.add_get('/', handle_health)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 8080).start()

async def reminder_loop():
    global sent_today
    while True:
        now = datetime.now(); cur = now.strftime("%H:%M")
        if cur == "00:00": sent_today.clear()
        if cur in ["12:50", "18:05"]:
            key = f"{now.strftime('%d')}_{cur}"
            if key not in sent_today:
                try: 
                    msg = "Бро, пара через 40 мин!" if cur == "12:50" else "5 мин до конца!"
                    await bot.send_message(YOUR_CHAT_ID, msg)
                    sent_today.add(key)
                except: pass
        await asyncio.sleep(60)

async def main():
    asyncio.create_task(start_web_server())
    asyncio.create_task(reminder_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())