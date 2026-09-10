from datetime import timedelta
from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart

from config import BELLS, DAYS_RU
from keyboards import weekday_inline_kb, web_app_inline_kb

from scheduler import (
    now_almaty, format_day, format_week,
    current_lesson, next_lesson,
)
from settings import are_reminders_enabled, set_reminders_enabled
from ai_assistant import ask_ai, clear_user_history

router = Router()



# ── /start ───────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "🔷 <b>Расписание занятий</b>\n\n"
        "<blockquote>Актуальный таймлайн пар, расписание звонков и персональный ИИ-ассистент.</blockquote>\n\n"
        "Выберите действие ниже:",
        reply_markup=web_app_inline_kb(),
    )


# ── /app ─────────────────────────────────────────────────────
@router.message(Command("app"))
async def cmd_app(message: types.Message):
    await message.answer(
        "🔷 <b>Расписание занятий</b>\n\n"
        "<blockquote>Интерактивная веб-версия доступна по кнопке ниже:</blockquote>",
        reply_markup=web_app_inline_kb(),
    )


# ── /help ────────────────────────────────────────────────────
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "🔷 <b>Справка и команды</b>\n\n"
        "<blockquote>Быстрый доступ к возможностям бота:</blockquote>\n\n"
        "• <code>/app</code> — открыть интерактивное расписание\n"
        "• <code>/ai &lt;вопрос&gt;</code> — задать вопрос ИИ-помощнику\n"
        "• <code>/clear_ai</code> — очистить историю диалога с ИИ\n"
        "• <code>/mute</code> — отключить напоминания о парах\n"
        "• <code>/unmute</code> — включить напоминания о парах\n"
        "• <code>/status</code> — статус подсистемы уведомлений\n\n"
        "<i>💡 В личных сообщениях боту можно просто писать вопросы текстом — ИИ ответит!</i>",
        reply_markup=web_app_inline_kb(),
    )


# ── Callback-кнопки ──────────────────────────────────────────
@router.callback_query(F.data == "btn_bells")
async def cb_bells(call: types.CallbackQuery):
    await call.answer()
    header = (
        "🔔 <b>Расписание звонков</b>\n\n"
    )
    table = "<pre>"
    table += "┌──────┬───────┬───────┐\n"
    table += "│ Пара │ Начало│ Конец │\n"
    table += "├──────┼───────┼───────┤\n"
    for name, start, end in BELLS:
        num = name.split()[0]
        table += f"│  {num}   │ {start} │ {end} │\n"
    table += "└──────┴───────┴───────┘"
    table += "</pre>"
    await call.message.answer(header + table)


@router.callback_query(F.data == "btn_ai_hint")
async def cb_ai_hint(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "💬 <b>ИИ-помощник</b>\n\n"
        "<blockquote>Напишите любой вопрос по расписанию или учёбе прямо в этот чат.</blockquote>"
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


# ── Управление уведомлениями (Режим практики) ────────────────
async def is_user_admin(message: types.Message) -> bool:
    if message.chat.type == "private":
        return True
    try:
        member = await message.chat.get_member(message.from_user.id)
        return member.status in ("creator", "administrator")
    except Exception:
        return True


@router.message(Command("mute", "silent"))
async def cmd_mute(message: types.Message):
    if not await is_user_admin(message):
        await message.answer("⚠️ Требуются права администратора.")
        return
    set_reminders_enabled(False)
    await message.answer("🔕 Автоматические напоминания и утренние сводки отключены.")


@router.message(Command("unmute", "active"))
async def cmd_unmute(message: types.Message):
    if not await is_user_admin(message):
        await message.answer("⚠️ Требуются права администратора.")
        return
    set_reminders_enabled(True)
    await message.answer("🔔 Автоматические напоминания и утренние сводки включены.")


@router.message(Command("status"))
async def cmd_status(message: types.Message):
    status = "включены" if are_reminders_enabled() else "отключены"
    await message.answer(f"🔔 Статус авто-напоминаний: <b>{status}</b>")


# ── ИИ-Помощник (Groq) ───────────────────────────────────────
async def _send_ai_reply(message: types.Message, prompt: str):
    await message.bot.send_chat_action(message.chat.id, action="typing")
    reply = await ask_ai(message.from_user.id, prompt)
    try:
        await message.answer(reply, parse_mode="Markdown")
    except Exception:
        try:
            await message.answer(reply, parse_mode="HTML")
        except Exception:
            await message.answer(reply, parse_mode=None)


@router.message(Command("ai"))
async def cmd_ai(message: types.Message):
    args = message.text.partition(" ")[2].strip()
    if not args:
        await message.answer(
            "💬 <b>ИИ-помощник</b>\n\n"
            "<blockquote>Напишите вопрос после команды: <code>/ai ваш вопрос</code>\n"
            "В личке с ботом можно писать напрямую без команды.</blockquote>"
        )
        return
    await _send_ai_reply(message, args)


@router.message(Command("clear_ai", "reset_ai"))
async def cmd_clear_ai(message: types.Message):
    clear_user_history(message.from_user.id)
    await message.answer("💬 История диалога с ИИ очищена.")



# ── Свободный текст в личных сообщениях ──────────────────────
@router.message(F.text, F.chat.type == "private")
async def handle_private_free_text(message: types.Message):
    text = message.text.strip()
    if text.startswith("/"):
        return
    button_texts = {
        "📅 Сегодня", "📅 Завтра", "📚 Сейчас",
        "⏭ След. пара", "📋 Неделя", "🔔 Звонки", "📱 Mini App"
    }
    if text in button_texts:
        return
    await _send_ai_reply(message, text)