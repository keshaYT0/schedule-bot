from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import DAYS_SHORT, WEBAPP_URL



def web_app_inline_kb() -> InlineKeyboardMarkup:
    if WEBAPP_URL.startswith("https://"):
        button = InlineKeyboardButton(text="📱 Открыть расписание (App)", web_app=WebAppInfo(url=WEBAPP_URL))
    else:
        button = InlineKeyboardButton(text="🌐 Открыть веб-версию", url=WEBAPP_URL)
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


def main_kb():
    builder = ReplyKeyboardBuilder()
    if WEBAPP_URL.startswith("https://"):
        builder.button(text="📱 Mini App", web_app=WebAppInfo(url=WEBAPP_URL))
    builder.button(text="📅 Сегодня")
    builder.button(text="📅 Завтра")
    builder.button(text="📚 Сейчас")
    builder.button(text="⏭ След. пара")
    builder.button(text="📋 Неделя")
    builder.button(text="🔔 Звонки")
    if WEBAPP_URL.startswith("https://"):
        builder.adjust(1, 2, 2, 2)
    else:
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
