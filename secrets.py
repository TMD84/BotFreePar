# 🛠️ Импортируем dotenv и os
from dotenv import load_dotenv
import os
from config import ENV_PATH  # подключаем путь к .env из config.py

# 📥 Загружаем .env
load_dotenv(dotenv_path=ENV_PATH)

# 🔐 Получаем переменные окружения
# TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# FREELANCEHUNT_EMAIL = os.getenv("FREELANCEHUNT_EMAIL")
# FREELANCEHUNT_PASSWORD = os.getenv("FREELANCEHUNT_PASSWORD")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
FREELANCEHUNT_EMAIL = os.environ.get("FREELANCEHUNT_EMAIL")
FREELANCEHUNT_PASSWORD = os.environ.get("FREELANCEHUNT_PASSWORD")

# 🖨️ Отладка: убедимся, что данные загружены
print("[SECRETS] Телеграм токен: тут токен")
print("[SECRETS] Email: тут емейл")
print("[SECRETS] Пароль: тут пароль")