import json
import logging
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent / "settings.json"
logger = logging.getLogger(__name__)

def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return {"reminders_enabled": True}
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Ошибка при чтении settings.json: %s", e)
        return {"reminders_enabled": True}

def save_settings(settings: dict) -> None:
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Ошибка при сохранении settings.json: %s", e)

def are_reminders_enabled() -> bool:
    return load_settings().get("reminders_enabled", True)

def set_reminders_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["reminders_enabled"] = enabled
    save_settings(settings)
