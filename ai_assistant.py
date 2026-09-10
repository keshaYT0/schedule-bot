import json
import logging
from collections import defaultdict, deque
from config import GROQ_API_KEY, BELLS, DAYS_RU
from scheduler import SCHEDULE, now_almaty

logger = logging.getLogger(__name__)

# In-memory dialog history: user_id -> deque of messages
dialog_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=6))


def build_system_prompt() -> str:
    now = now_almaty()
    cur_time = now.strftime("%H:%M")
    cur_date = now.strftime("%d.%m.%Y")
    cur_day_en = now.strftime("%A")
    cur_day_ru = DAYS_RU.get(cur_day_en, cur_day_en)

    bells_text = "\n".join([f"- {name}: {start} – {end}" for name, start, end in BELLS])
    schedule_text = json.dumps(SCHEDULE, ensure_ascii=False, indent=2)

    return f"""Ты — свой чувак, одногруппник и помощник для студентов 4 курса IT-специальности (колледж).
Ты общаешься в Telegram в личке или группе.

ГЛАВНЫЕ ПРАВИЛА ОБЩЕНИЯ:
1. Забудь про тон корпоративной техподдержки, банковского робота и официоз. НИКАКИХ «Чем я могу вам помочь?», «Вот список того, что я умею: * пункт 1 * пункт 2». Это звучит кринжово и как душный робот.
2. Общайся просто, живо, на «ты», как нормальный студент в переписке (можно легкий студенческий сленг: «пары», «чилим», «препод», «шарага», «домашка»).
3. На простые приветствия («привет», «ку», «че как», «здарова») отвечай КОРОТКО и по-человечески, буквально в 1-2 предложения (например: «Здарова! Че как сам? Пары уже закончились, чилим 🏖», «Ку! Че подсказать по парам или коду?»). Не вываливай простыни текста!
4. Если спрашивают про расписание — отвечай быстро, четко и по делу, с юмором (например: «Завтра 4 пары, начинаем в 8:00 у Маликова. Будет жарко 💀»).
5. Если просят помочь с кодом/MySQL/учебой — объясняй просто, без академической духоты, на пальцах.
6. Не спамь эмодзи на каждое слово — 1-2 штуки по делу максимум.

Данные для контекста (Алматы, UTC+5):
- Сейчас: {cur_day_ru}, {cur_date}, {cur_time}

Звонки:
{bells_text}

Расписание группы:
{schedule_text}
"""



async def ask_ai(user_id: int, user_prompt: str) -> str:
    """Send user query to Groq Llama-3.3-70b with conversation history."""
    if not GROQ_API_KEY:
        return "⚠️ ИИ-помощник не настроен: не задан <code>GROQ_API_KEY</code> в переменных окружения."

    try:
        from groq import AsyncGroq
    except ImportError:
        return "⚠️ Библиотека <code>groq</code> не установлена."

    client = AsyncGroq(api_key=GROQ_API_KEY)
    system_prompt = build_system_prompt()

    history = dialog_history[user_id]
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(list(history))
    messages.append({"role": "user", "content": user_prompt})

    # Primary models available on Groq
    models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b", "groq/compound"]
    last_error = None

    import re

    for model in models:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            raw_answer = response.choices[0].message.content or ""
            # Strip any internal <think>...</think> reasoning blocks
            answer = re.sub(r"<think>.*?</think>", "", raw_answer, flags=re.DOTALL).strip()

            if not answer:
                answer = raw_answer.strip()

            # Save in history
            history.append({"role": "user", "content": user_prompt})
            history.append({"role": "assistant", "content": answer})

            return answer
        except Exception as e:
            logger.warning("Groq model %s failed: %s", model, e)
            last_error = e

    return f"⚠️ Ошибка обращения к ИИ: {last_error}"



def clear_user_history(user_id: int) -> None:
    """Clear dialogue history for a given user."""
    if user_id in dialog_history:
        dialog_history[user_id].clear()
