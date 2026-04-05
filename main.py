"""
main.py — Application entry-point
===================================

Launches three concurrent subsystems via ``asyncio``:

1. **aiogram polling** — the Telegram bot itself.
2. **Health-check web server** — ``aiohttp`` on ``$PORT`` (Render requirement).
3. **Self-ping keep-alive loop** — prevents Render free-tier sleep.

The reminder loop (morning summary + pre-lesson alerts) is also
started as a background task.
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import TOKEN, CHAT_ID, REMINDER_BEFORE, MORNING_SUMMARY_TIME, DAYS_RU
from scheduler import now_almaty, format_day, get_reminder_times
from handlers.schedule import router
from infrastructure.keepalive import start_health_server, keepalive_loop

# ── Bot & Dispatcher ─────────────────────────────────────────
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.include_router(router)

# Tracks already-sent messages for the current day to avoid duplicates.
sent_today: set[str] = set()


# ── Reminder loop ────────────────────────────────────────────

async def reminder_loop() -> None:
    """Background task: morning summary + per-lesson reminders.

    Runs every 30 s, checks current time against schedule,
    and sends alerts via Telegram when appropriate.
    """
    while True:
        try:
            if CHAT_ID is None:
                await asyncio.sleep(60)
                continue

            now = now_almaty()
            cur = now.strftime("%H:%M")
            day_name = now.strftime("%A")

            # Reset at midnight
            if cur == "00:00":
                sent_today.clear()

            # ── Morning summary ─────────────────────────────
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

            # ── Pre-lesson reminders ────────────────────────
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
            logging.error("Reminder loop error: %s", e)

        await asyncio.sleep(30)


# ── Main ─────────────────────────────────────────────────────

async def main() -> None:
    """Start all subsystems concurrently with controlled lifecycle."""
    logging.info(
        "Bot starting  ·  PORT=%s  ·  polling mode",
        os.getenv("PORT", "8080"),
    )

    health_runner = None
    try:
        # Start core components
        health_runner = await start_health_server()
        asyncio.create_task(keepalive_loop())
        asyncio.create_task(reminder_loop())

        # Main polling loop (blocking)
        await dp.start_polling(bot)

    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        logging.info("Bot is shutting down...")
    except Exception as exc:
        logging.exception("Fatal error during bot execution: %s", exc)
    finally:
        # Graceful shutdown of the health server
        if health_runner:
            logging.info("Stopping health-check server...")
            await health_runner.cleanup()
            logging.info("Health-check server stopped.")

        logging.info("Bot stopped.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)-28s  %(message)s",
    )
    asyncio.run(main())
