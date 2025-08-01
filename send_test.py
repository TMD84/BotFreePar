# # import os
# # import requests
# # from dotenv import load_dotenv
# #
# # load_dotenv(".env")
# #
# # chat_id = os.getenv("TELEGRAM_CHAT_ID")
# # token = os.getenv("TELEGRAM_BOT_TOKEN")
# # text = "🔔 Тестовая отправка из parser.py"
# #
# # resp = requests.post(
# #     f"https://api.telegram.org/bot{token}/sendMessage",
# #     data={"chat_id": chat_id, "text": text}
# # )
# #
# # print("Статус:", resp.status_code)
# # print("Ответ:", resp.text)
#
# import sqlite3
#
# DB_PATH = "projects.db"  # Укажи путь к базе, если он другой
#
# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()
#
# # Добавляем столбцы в таблицу projects
# cursor.execute("ALTER TABLE projects ADD COLUMN keywords_found TEXT;")
# cursor.execute("ALTER TABLE projects ADD COLUMN clients_matched TEXT;")
# cursor.execute("ALTER TABLE projects ADD COLUMN is_favorite INTEGER DEFAULT 0;")
#
# # Создаём таблицу user_view_state, если её нет
# # cursor.execute("""
# # CREATE TABLE IF NOT EXISTS user_view_state (
# #     user_id BIGINT PRIMARY KEY,
# #     view_mode TEXT NOT NULL DEFAULT 'unknown',
# #     current_index INTEGER NOT NULL DEFAULT 0
# # );
# # """)
#
# conn.commit()
# conn.close()
#
# print("✅ Миграция завершена — таблица и столбцы добавлены.")
#
# import sqlite3
#
# DB_PATH = "projects.db"
# conn = sqlite3.connect(DB_PATH)  # Укажи путь к своей базе
# cursor = conn.cursor()
#
# cursor.execute("SELECT COUNT(*) FROM projects;")
# total = cursor.fetchone()[0]
#
# cursor.execute("SELECT COUNT(*) FROM projects WHERE is_processed = 0;")
# unprocessed = cursor.fetchone()[0]
#
# conn.close()
#
# print(f"🔢 Всего проектов: {total}")
# print(f"🚧 Не обработано: {unprocessed}")

import sqlite3
import os

DB_PATH = "projects.db"  # Укажи путь, если база лежит в другом месте

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 🔍 Проверим и добавим недостающие столбцы
columns_to_add = [
    ("reply_text", "TEXT")  # 👈 тот самый столбец
]

for column_name, column_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE projects ADD COLUMN {column_name} {column_type};")
        print(f"✅ Столбец {column_name} добавлен.")
    except sqlite3.OperationalError:
        print(f"ℹ️ Столбец {column_name} уже существует — пропускаем.")

conn.commit()
conn.close()
print("🏗️ Миграция завершена.")