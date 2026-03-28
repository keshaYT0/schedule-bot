from datetime import timedelta
from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart

from config import BELLS, DAYS_RU
from keyboards import main_kb, weekday_inline_kb
from scheduler import (
    now_almaty, format_day, format_week,
    current_lesson, next_lesson,
)

router = Router()


# ── /start ───────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
        "Я бот расписания твоей группы.\n"
        "Используй кнопки, чтобы узнать:\n\n"
        "📅  <b>Сегодня / Завтра</b> — расписание пар\n"
        "📚  <b>Сейчас</b> — текущая пара с прогрессом\n"
        "⏭  <b>След. пара</b> — что будет дальше\n"
        "📋  <b>Неделя</b> — вся неделя целиком\n"
        "🔔  <b>Звонки</b> — расписание звонков\n\n"
        "Удачного дня! 🎓",
        reply_markup=main_kb(),
    )


# ── /help ────────────────────────────────────────────────────
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📖 <b>Список команд</b>\n\n"
        "/start — перезапустить бота\n"
        "/help — эта справка\n\n"
        "<b>Кнопки:</b>\n"
        "📅 Сегодня / Завтра — расписание\n"
        "📚 Сейчас — текущая пара\n"
        "⏭ След. пара — следующая пара\n"
        "📋 Неделя — расписание Пн–Пт\n"
        "🔔 Звонки — расписание звонков\n\n"
        "💡 Бот автоматически присылает напоминания\n"
        "за 10 мин. до каждой пары и сводку утром.",
    )


# ── Звонки ───────────────────────────────────────────────────
@router.message(F.text == "🔔 Звонки")
async def cmd_bells(message: types.Message):
    header = "🔔 <b>Расписание звонков</b>\n\n"
    table = "<code>"
    table += "┌──────┬───────┬───────┐\n"
    table += "│ Пара │ Начало│ Конец │\n"
    table += "├──────┼───────┼───────┤\n"
    for name, start, end in BELLS:
        num = name.split()[0]
        table += f"│  {num}   │ {start} │ {end} │\n"
    table += "└──────┴───────┴───────┘"
    table += "</code>"
    await message.answer(header + table)


# ── Сегодня / Завтра ─────────────────────────────────────────
@router.message(F.text.in_(["📅 Сегодня", "📅 Завтра"]))
async def cmd_schedule(message: types.Message):
    now = now_almaty()
    if message.text == "📅 Завтра":
        now += timedelta(days=1)

    day_name = now.strftime("%A")
    day_ru = DAYS_RU.get(day_name, day_name)
    date_str = now.strftime("%d.%m")
    content = format_day(day_name)

    await message.answer(
        f"📅 <b>{day_ru}  ·  {date_str}</b>\n\n{content}"
    )


# ── Сейчас ───────────────────────────────────────────────────
@router.message(F.text == "📚 Сейчас")
async def cmd_now(message: types.Message):
    now = now_almaty()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d.%m.%Y")
    current_minutes = now.hour * 60 + now.minute

    if day_name in ("Saturday", "Sunday"):
        await message.answer(
            f"📅 <b>{date_str}</b>\n\n🏖 Выходной. Отдыхай!"
        )
        return

    lesson = current_lesson(day_name, current_minutes)
    if not lesson:
        nxt = next_lesson(day_name, current_minutes)
        if nxt:
            await message.answer(
                f"📅 <b>{date_str}</b>\n\n"
                f"Сейчас пар нет.\n\n"
                f"⏭ Следующая — <b>{nxt['name']}</b>\n"
                f"Через {nxt['until']} мин. · {nxt['start']} · 🏫 {nxt['room']}"
            )
        else:
            await message.answer(
                f"📅 <b>{date_str}</b>\n\n✅ Пары на сегодня закончились!"
            )
        return

    await message.answer(
        f"📅 <b>{date_str}</b>\n\n"
        f"📚 <b>{lesson['num']} пара  ·  {lesson['name']}</b>\n"
        f"👨‍🏫 {lesson['teacher']}\n"
        f"🏫 {lesson['room']}\n\n"
        f"⏱ {lesson['start']} – {lesson['end']}\n"
        f"<code>{lesson['bar']}</code>\n"
        f"До конца — <b>{lesson['left']} мин.</b>",
    )


# ── След. пара ───────────────────────────────────────────────
@router.message(F.text == "⏭ След. пара")
async def cmd_next(message: types.Message):
    now = now_almaty()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d.%m")
    current_minutes = now.hour * 60 + now.minute

    if day_name in ("Saturday", "Sunday"):
        await message.answer(
            f"📅 <b>{date_str}</b>\n\n🏖 Выходной. Пар нет."
        )
        return

    nxt = next_lesson(day_name, current_minutes)
    if not nxt:
        await message.answer(
            f"📅 <b>{date_str}</b>\n\n✅ Больше пар сегодня нет!"
        )
        return

    await message.answer(
        f"📅 <b>{date_str}</b>\n\n"
        f"⏭ <b>Следующая пара</b>\n\n"
        f"┌ <b>{nxt['num']} пара</b>  ·  {nxt['start']}\n"
        f"│ 📖 {nxt['name']}\n"
        f"│ 👨‍🏫 {nxt['teacher']}\n"
        f"└ 🏫 {nxt['room']}\n\n"
        f"⏳ Через <b>{nxt['until']} мин.</b>",
    )


# ── Неделя ───────────────────────────────────────────────────
@router.message(F.text == "📋 Неделя")
async def cmd_week(message: types.Message):
    text = format_week()
    # Telegram лимит 4096 символов — на всякий случай разобьём
    if len(text) > 3800:
        await message.answer(
            "📋 <b>Расписание на неделю</b>\n\n"
            "Используй кнопки, чтобы посмотреть\n"
            "расписание на конкретный день 👇",
            reply_markup=weekday_inline_kb(),
        )
    else:
        await message.answer(
            f"📋 <b>Расписание на неделю</b>\n\n{text}",
            reply_markup=weekday_inline_kb(),
        )


# ── Inline: выбор дня недели ─────────────────────────────────
@router.callback_query(F.data.startswith("day:"))
async def cb_day(callback: types.CallbackQuery):
    day_name = callback.data.split(":")[1]
    day_ru = DAYS_RU.get(day_name, day_name)
    content = format_day(day_name)

    await callback.message.edit_text(
        f"📅 <b>{day_ru}</b>\n\n{content}",
        reply_markup=weekday_inline_kb(),
    )
    await callback.answer()