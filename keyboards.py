from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Сегодня")
    builder.button(text="Завтра")
    builder.button(text="Сейчас")
    builder.button(text="Звонки")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)
