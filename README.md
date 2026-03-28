# 📅 Schedule Bot

Telegram-бот расписания пар для студенческой группы.

## Возможности

- 📅 **Сегодня / Завтра** — расписание пар на день
- 📚 **Сейчас** — текущая пара с прогресс-баром
- ⏭ **След. пара** — следующая пара с обратным отсчётом
- 📋 **Неделя** — расписание на всю неделю + inline-навигация по дням
- 🔔 **Звонки** — расписание звонков (таблица)
- 🔔 **Авто-напоминания** — за 10 мин. до каждой пары
- ☀️ **Утренняя сводка** — автоотправка расписания в 12:00

## Установка

```bash
git clone https://github.com/keshaYT0/schedule-bot.git
cd schedule-bot
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env`:

```env
BOT_TOKEN=ваш_токен_от_BotFather
CHAT_ID=id_чата_для_уведомлений
```

## Запуск

```bash
python main.py
```

## Деплой на Render

1. Подключите репозиторий к Render
2. В Environment добавьте `BOT_TOKEN` и `CHAT_ID`
3. Start Command: `python main.py`

## Расписание

Расписание хранится в `schedule.json`. Формат:

```json
{
  "Monday": [
    {"start": "13:30", "end": "15:00", "name": "ООП", "teacher": "...", "room": "301 к1"}
  ]
}
```

## Технологии

- Python 3.11+
- aiogram 3.7
- aiohttp (health-check endpoint для Render)
