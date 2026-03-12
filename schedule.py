from datetime import timedelta
from aiogram import Router, types, F
from aiogram.filters import Command

from config import BELLS, DAYS_RU
from keyboards import main_kb
from scheduler import now_almaty, format_day, current_lesson

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}.",
        reply_markup=main_kb()
    )


@router.message(F.text == "Звонки")
async def cmd_bells(message: types.Message):
    lines = "\n".join(f"{name} — {start} · {end}" for name, start, end in BELLS)
    await message.answer(f"<b>Расписание звонков</b>\n\n{lines}")


@router.message(F.text.in_(["Сегодня", "Завтра"]))
async def cmd_schedule(message: types.Message):
    now = now_almaty()
    if message.text == "Завтра":
        now += timedelta(days=1)

    day_name = now.strftime("%A")
    day_ru = DAYS_RU.get(day_name, day_name)
    date_str = now.strftime("%d.%m")
    content = format_day(day_name)

    await message.answer(f"<b>{day_ru} · {date_str}</b>\n\n{content}")


@router.message(F.text == "Сейчас")
async def cmd_now(message: types.Message):
    now = now_almaty()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d.%m.%Y")
    current_minutes = now.hour * 60 + now.minute

    if day_name not in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"):
        await message.answer(f"<b>{date_str}</b>\n\nВыходной. Пар нет.")
        return

    lesson = current_lesson(day_name, current_minutes)
    if not lesson:
        await message.answer(f"<b>{date_str}</b>\n\nСейчас пар нет.")
        return

    await message.answer(
        f"<b>{date_str}</b>\n\n"
        f"<b>{lesson['name']}</b>\n"
        f"{lesson['teacher']} · {lesson['room']}\n\n"
        f"До конца — {lesson['left']} мин."
    )
