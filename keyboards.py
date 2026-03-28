from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from config import DAYS_SHORT


def main_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📅 Сегодня")
    builder.button(text="📅 Завтра")
    builder.button(text="📚 Сейчас")
    builder.button(text="⏭ След. пара")
    builder.button(text="📋 Неделя")
    builder.button(text="🔔 Звонки")
    builder.adjust(2, 2, 2)
    return builder.as_markup(resize_keyboard=True)


def weekday_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    days = [
        ("Monday", "Пн"), ("Tuesday", "Вт"), ("Wednesday", "Ср"),
        ("Thursday", "Чт"), ("Friday", "Пт"),
    ]
    for eng, short in days:
        builder.button(text=short, callback_data=f"day:{eng}")
    builder.adjust(5)
    return builder.as_markup()
