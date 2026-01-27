import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# ТВОЙ ТОКЕН
TOKEN = "8444997622:AAGjmBYxYq79JxGT9kf8bu1n9lKmw5y_Ko0"

# 👇 СЮДА ВСТАВЬ СВОЙ CHAT_ID (узнать через @userinfobot)
YOUR_CHAT_ID = 1380431564  # Например: 123456789

bot = Bot(
    token=TOKEN, 
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# Расписание пар
SCHEDULE = {
    "Monday": "<b>📅 ПОНЕДЕЛЬНИК</b>\n\n"
              "4️⃣ 13:30 - 15:00 | ООП (Зейнулла Ж.А., 301 к1)\n"
              "5️⃣ 15:10 - 16:40 | Предпринимательство (Кусманова А.Ж., 403 к2) / Этика (Акумбаева Д.Б., 504 к2)\n"
              "6️⃣ 16:50 - 18:10 | Базы данных (Сычева Е.А., 413 к2)",
              
    "Tuesday": "<b>📅 ВТОРНИК</b>\n\n"
               "4️⃣ 13:30 - 15:00 | Микропроцессоры (Сычева Е.А., 413 к2)\n"
               "5️⃣ 15:10 - 16:40 | ООП (Зейнулла Ж.А., 410 к2)\n"
               "6️⃣ 16:50 - 18:10 | Философия (Каримова М.К., 211 к2)",
               
    "Wednesday": "<b>📅 СРЕДА</b>\n\n"
                 "4️⃣ 13:30 - 15:00 | Микропроцессоры (Сычева Е.А., 413 к2)\n"
                 "5️⃣ 15:10 - 16:40 | Микропроцессоры (Сычева Е.А., 413 к2)\n"
                 "6️⃣ 16:50 - 18:10 | Культурология (Айтпаева А.Ж., 409 к1)\n"
                 "7️⃣ 18:15 - 19:35 | Политология (Капсалямова Г.Т., 131 к1)",
                 
    "Thursday": "<b>📅 ЧЕТВЕРГ</b>\n\n"
                "4️⃣ 13:30 - 15:00 | Основы права (Канапина А.А., 406 к2)\n"
                "5️⃣ 15:10 - 16:40 | Прогр. в офисе (Наурызбай М.М., 301 к1)\n"
                "6️⃣ 16:50 - 18:10 | Web-дизайн (Наурызбай М.М., 301 к1)\n"
                "7️⃣ 18:15 - 19:35 | Физра (Паненков А.В.)",
                
    "Friday": "<b>📅 ПЯТНИЦА</b>\n\n"
              "4️⃣ 13:30 - 15:00 | Мобильная робототехника (Маликов В.В., 413 к2)\n"
              "5️⃣ 15:10 - 16:40 | Мобильная робототехника (Маликов В.В., 413 к2)\n"
              "6️⃣ 16:50 - 18:10 | MySQL (Сабирханова А.О., 412 к2)\n"
              "7️⃣ 18:15 - 19:35 | MySQL (Сабирханова А.О., 412 к2)"
}

# Расписание напоминалок
REMINDERS = {
    "12:50": "Бро, 12:50. Ты в курсе, что пара через 40 минут? Давай, чай допивай, хавай че-нить и выдвигайся.",
    "18:05": "Жив там еще? 5 минут осталось до конца пары... Держись, почти свободен.",
}

sent_today = set()

# Кнопки
def get_main_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📅 На сегодня")
    builder.button(text="⏩ На завтра")
    builder.button(text="🔔 Звонки")
    builder.button(text="📍 Что сейчас?")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Выбирай кнопку:", 
        reply_markup=get_main_kb()
    )

@dp.message(F.text == "🔔 Звонки")
async def send_calls(message: types.Message):
    calls_text = (
        "<b>🔔 РАСПИСАНИЕ ЗВОНКОВ:</b>\n\n"
        "1 ПАРА: 08:00 — 09:30\n"
        "2 ПАРА: 09:40 — 11:10\n"
        "3 ПАРА: 11:20 — 12:50\n"
        "─── Большая перемена ───\n"
        "4 ПАРА: 13:30 — 15:00\n"
        "5 ПАРА: 15:10 — 16:40\n"
        "6 ПАРА: 16:50 — 18:10\n"
        "7 ПАРА: 18:15 — 19:35"
    )
    await message.answer(calls_text)

@dp.message(F.text.in_(["📅 На сегодня", "⏩ На завтра"]))
async def send_sched(message: types.Message):
    days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    idx = datetime.now().weekday()
    
    if message.text == "⏩ На завтра":
        idx = (idx + 1) % 7
        
    day_name = days_map[idx]
    text = SCHEDULE.get(day_name, "<b>Пар нет!</b> Сегодня отдыхаем. 😎")
    await message.answer(text)

@dp.message(F.text == "📍 Что сейчас?")
async def current_lesson(message: types.Message):
    now = datetime.now()
    hour, minute = now.hour, now.minute
    current_time = hour * 60 + minute
    
    lessons = [
        (480, 570, "1-я пара (08:00-09:30)"),
        (580, 670, "2-я пара (09:40-11:10)"),
        (680, 770, "3-я пара (11:20-12:50)"),
        (810, 900, "4-я пара (13:30-15:00)"),
        (910, 1000, "5-я пара (15:10-16:40)"),
        (1010, 1090, "6-я пара (16:50-18:10)"),
        (1095, 1175, "7-я пара (18:15-19:35)"),
    ]
    
    for start, end, name in lessons:
        if start <= current_time <= end:
            await message.answer(f"Сейчас идет <b>{name}</b>")
            return
    
    await message.answer("Щас пар нет, расслабься 😎")

# Веб-сервер для Render (чтобы не засыпал)
async def handle_health(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Web server started on port 8080")

# Фоновая задача для напоминаний
async def reminder_loop():
    global sent_today
    
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        if current_time == "00:00":
            sent_today.clear()
        
        if current_time in REMINDERS:
            reminder_key = f"{current_date}_{current_time}"
            
            if reminder_key not in sent_today and YOUR_CHAT_ID:
                try:
                    await bot.send_message(YOUR_CHAT_ID, REMINDERS[current_time])
                    sent_today.add(reminder_key)
                    print(f"✅ Отправлено напоминание: {current_time}")
                except Exception as e:
                    print(f"❌ Ошибка отправки: {e}")
        
        await asyncio.sleep(60)

async def main():
    asyncio.create_task(start_web_server())
    asyncio.create_task(reminder_loop())
    
    print("✅ Бот запущен и ждет команд!")
    print("🔔 Напоминания активны!")
    
    if not YOUR_CHAT_ID:
        print("⚠️ ВНИМАНИЕ: YOUR_CHAT_ID не установлен!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())