import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import TOKEN, CHAT_ID, REMINDER_BEFORE, MORNING_SUMMARY_TIME, DAYS_RU
from scheduler import now_almaty, format_day, get_reminder_times
from handlers.schedule import router

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.include_router(router)

sent_today: set[str] = set()


async def reminder_loop():
    """Умный цикл напоминаний:
    1. За N минут до каждой пары — напоминание
    2. Утренняя сводка расписания на день
    """
    while True:
        try:
            if CHAT_ID is None:
                await asyncio.sleep(60)
                continue

            now = now_almaty()
            cur = now.strftime("%H:%M")
            day_name = now.strftime("%A")

            # Сброс списка отправленных в полночь
            if cur == "00:00":
                sent_today.clear()

            # ── Утренняя сводка ──────────────────────────────
            morning_key = f"{now.strftime('%d')}_morning"
            if cur == MORNING_SUMMARY_TIME and morning_key not in sent_today:
                day_ru = DAYS_RU.get(day_name, day_name)
                date_str = now.strftime("%d.%m")
                content = format_day(day_name)
                await bot.send_message(
                    CHAT_ID,
                    f"☀️ <b>Доброе утро!</b>\n\n"
                    f"📅 <b>{day_ru}  ·  {date_str}</b>\n\n"
                    f"{content}",
                )
                sent_today.add(morning_key)

            # ── Напоминания перед парами ──────────────────────
            reminders = get_reminder_times(day_name, REMINDER_BEFORE)
            for r in reminders:
                key = f"{now.strftime('%d')}_r_{r['time_hhmm']}"
                if cur == r["time_hhmm"] and key not in sent_today:
                    await bot.send_message(
                        CHAT_ID,
                        f"🔔 <b>Напоминание!</b>\n\n"
                        f"📚 <b>{r['lesson_num']} пара — {r['lesson_name']}</b>\n"
                        f"🏫 {r['room']}\n"
                        f"⏰ Начало в {r['start_time']}  "
                        f"(через {REMINDER_BEFORE} мин.)",
                    )
                    sent_today.add(key)

        except Exception as e:
            logging.error(f"Reminder loop error: {e}")

        await asyncio.sleep(30)


async def health(request):
    return web.Response(text="ok")


async def start_server():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))  # Рендер выдает порт через переменную окружения
    await web.TCPSite(runner, "0.0.0.0", port).start()


async def main():
    logging.info(f"Bot starting on port {os.environ.get('PORT', 8080)}...")
    asyncio.create_task(start_server())
    asyncio.create_task(reminder_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    import os
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
    )
    asyncio.run(main())
