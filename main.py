import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import TOKEN, CHAT_ID, TZ
from scheduler import now_almaty
from handlers.schedule import router

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.include_router(router)

sent_today: set[str] = set()


async def reminder_loop():
    while True:
        now = now_almaty()
        cur = now.strftime("%H:%M")

        if cur == "00:00":
            sent_today.clear()

        if cur in ("12:50", "18:05"):
            key = f"{now.strftime('%d')}_{cur}"
            if key not in sent_today:
                try:
                    msg = "Пара через 40 минут." if cur == "12:50" else "До конца пары 5 минут."
                    await bot.send_message(CHAT_ID, msg)
                    sent_today.add(key)
                except Exception as e:
                    logging.error(f"Reminder error: {e}")

        await asyncio.sleep(60)


async def health(request):
    return web.Response(text="ok")


async def start_server():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 8080).start()


async def main():
    asyncio.create_task(start_server())
    asyncio.create_task(reminder_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
