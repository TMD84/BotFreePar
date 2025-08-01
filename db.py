# # import json
# # import os
# #
# # DB_FILE = "projects.json"
# # SCAN_FILE = "last_scan.json"
# #
# # class ProjectDatabase:
# #     def __init__(self):
# #         self.projects = {}
# #         if os.path.exists(DB_FILE):
# #             with open(DB_FILE, "r", encoding="utf-8") as f:
# #                 self.projects = json.load(f)
# #
# #     def project_exists(self, project_id):
# #         return str(project_id) in self.projects
# #
# #     def add_project(self, project):
# #         self.projects[str(project["id"])] = project
# #         with open(DB_FILE, "w", encoding="utf-8") as f:
# #             json.dump(self.projects, f, ensure_ascii=False, indent=2)
# #
# #     def get_last_scan_time(self):
# #         if os.path.exists(SCAN_FILE):
# #             with open(SCAN_FILE, "r", encoding="utf-8") as f:
# #                 return json.load(f).get("last_scan")
# #         return None
# #
# #     def update_last_scan_time(self):
# #         from datetime import datetime
# #         with open(SCAN_FILE, "w", encoding="utf-8") as f:
# #             json.dump({"last_scan": datetime.utcnow().isoformat()}, f)
# #
# #     def close(self):
# #         pass
#
# import json
# import os
# from datetime import datetime
#
# DB_FILE = "projects.json"
# SCAN_FILE = "last_scan.json"
#
# class ProjectDatabase:
#     def __init__(self):
#         self.projects = {}
#         if os.path.exists(DB_FILE):
#             with open(DB_FILE, "r", encoding="utf-8") as f:
#                 self.projects = json.load(f)
#
#     def project_exists(self, project_id):
#         return str(project_id) in self.projects
#
#     def add_project(self, project):
#         self.projects[str(project["id"])] = project
#         with open(DB_FILE, "w", encoding="utf-8") as f:
#             json.dump(self.projects, f, ensure_ascii=False, indent=2)
#
#     def get_last_scan_time(self):
#         if os.path.exists(SCAN_FILE):
#             with open(SCAN_FILE, "r", encoding="utf-8") as f:
#                 date_str = json.load(f).get("last_scan")
#                 if date_str:
#                     try:
#                         return datetime.fromisoformat(date_str)
#                     except ValueError:
#                         print("⚠️ Невозможно преобразовать дату:", date_str)
#         return None
#
#     def update_last_scan_time(self):
#         with open(SCAN_FILE, "w", encoding="utf-8") as f:
#             json.dump({"last_scan": datetime.utcnow().isoformat()}, f)
#
#     def close(self):
#         pass

# db.py
# db.py
import sqlite3
from typing import Optional, List, Tuple
from datetime import datetime

DB_PATH = "projects.db"

# 🏗️ Инициализация базы
def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 👤 Заказчики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE,
            name TEXT,
            surname TEXT
        )
    ''')

    # 👁️ Состояние просмотра пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_view_state (
    user_id INTEGER PRIMARY KEY,
    view_mode TEXT,
    current_index INTEGER,
    extra_filters TEXT,
    timestamp TEXT
    )
    ''')

    # 📦 Проекты
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            title TEXT,
            link TEXT,
            short_description TEXT,
            full_description TEXT,
            budget_amount REAL,
            budget_currency TEXT,
            is_premium INTEGER,
            skills TEXT,
            published_at TEXT,
            employer_id INTEGER,
            is_processed INTEGER DEFAULT 0,
            FOREIGN KEY (employer_id) REFERENCES employers(id)
        )
    ''')

    # 🎯 Добавляем недостающие столбцы, если они ещё не существуют
    # SQLite не имеет стандартного IF NOT EXISTS для столбцов, поэтому оборачиваем в try
    try:
        cursor.execute("ALTER TABLE projects ADD COLUMN keywords_found TEXT;")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE projects ADD COLUMN clients_matched TEXT;")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE projects ADD COLUMN is_favorite INTEGER DEFAULT 0;")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE projects ADD COLUMN reply_text TEXT;")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print("✅ База и таблицы инициализированы.")

# 👤 Заказчик: получить или создать
def get_or_create_employer(login: str, name: Optional[str], surname: Optional[str]) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM employers WHERE login = ?", (login,))
    result = cursor.fetchone()
    if result:
        conn.close()
        return result[0]

    cursor.execute(
        "INSERT INTO employers (login, name, surname) VALUES (?, ?, ?)",
        (login, name or "", surname or "")
    )
    conn.commit()
    eid = cursor.lastrowid
    conn.close()
    return eid

# 📥 Добавление проекта
def insert_project(project: dict) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM projects WHERE id = ?", (project["id"],))
    if cursor.fetchone():
        conn.close()
        return False

    eid = get_or_create_employer(
        project.get("employer_login"),
        project.get("employer_name"),
        project.get("employer_surname")
    )

    skills_str = ", ".join(project.get("skills", [])) if isinstance(project.get("skills"), list) else ""

    cursor.execute('''
        INSERT INTO projects (
            id, title, link, short_description,
            budget_amount, budget_currency, is_premium, skills,
            published_at, employer_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        project["id"],
        project.get("title"),
        project.get("link"),
        project.get("description"),
        project.get("budget_amount"),
        project.get("budget_currency"),
        int(bool(project.get("is_premium"))),
        skills_str,
        project.get("published_at"),
        eid
    ))

    conn.commit()
    conn.close()
    return True

# 🔎 Необработанные проекты
def get_unprocessed_projects() -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, link FROM projects WHERE is_processed = 0")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Функция получения проектов с сортировкой
def get_sorted_unprocessed_projects():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, link FROM projects
        WHERE is_processed = 0
        ORDER BY published_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# 🔐 Получение состояния просмотра
def get_user_view_state(user_id: int) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT view_mode, current_index, extra_filters, timestamp FROM user_view_state WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "view_mode": row[0],
            "current_index": row[1],
            "extra_filters": row[2],
            "timestamp": row[3]
        }
    return None

# 💾 Сохранение состояния просмотра
def save_user_view_state(user_id: int, view_mode: str, index: int, extra_filters: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO user_view_state (user_id, view_mode, current_index, extra_filters, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            view_mode = excluded.view_mode,
            current_index = excluded.current_index,
            extra_filters = excluded.extra_filters,
            timestamp = excluded.timestamp
    ''', (user_id, view_mode, index, extra_filters, now))
    conn.commit()
    conn.close()

# Чтение полного описания из БД
def fetch_full_description(project_id: int) -> str | None:
    print(f"[FUNC] 🔍 Получение полного описания проекта {project_id}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Покажем финальный SQL-запрос
        print(f"[FUNC] ▶️ Выполняем SQL: SELECT full_description FROM projects WHERE id = {project_id}")
        cursor.execute("SELECT full_description FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()

        conn.close()

        if not row:
            print(f"[FUNC] ⚠️ Нет строки с таким project_id ({project_id}) в БД.")
            return None

        description = row[0]

        # 🔍 Проверка на пустые и служебные значения
        invalid_descriptions = ["", "❌ Описание пустое.", "⏱️ Превышен лимит времени."]
        if not description or description.strip() in invalid_descriptions:
            print(f"[FUNC] ⚠️ Описание отсутствует или содержит заглушку: {repr(description)}")
            return None

        print(f"[FUNC] ✅ Описание найдено: {repr(description[:100])}...")
        return description

    except Exception as e:
        print(f"[FUNC] ❌ Ошибка при чтении описания из БД: {e}")
        return None
# def fetch_full_description(project_id: int) -> str | None:
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("SELECT full_description FROM projects WHERE id = ?", (project_id,))
#     row = cursor.fetchone()
#     conn.close()
#     return row[0] if row and row[0] else None

# 📝 Обновление описания
def update_project_description(project_id: int, full_description: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE projects
        SET full_description = ?, is_processed = 2
        WHERE id = ?
    """, (full_description, project_id))
    conn.commit()
    conn.close()
    print(f"✏️ Проект {project_id} обновлён.")

def update_project_keywords(project_id: int, keywords: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects
        SET keywords_found = ?
        WHERE id = ?
    ''', (keywords, project_id))
    conn.commit()
    conn.close()
    print(f"🔑 Ключевые слова обновлены для проекта {project_id}.")

def update_project_clients(project_id: int, clients: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects
        SET clients_matched = ?
        WHERE id = ?
    ''', (clients, project_id))
    conn.commit()
    conn.close()
    print(f"🧾 Заказчики обновлены для проекта {project_id}.")

def get_projects_by_status(status: str) -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, link FROM projects
        WHERE full_description = ?
        ORDER BY published_at DESC
    """, (status,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_projects_excluding_status(excluded_status: str) -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, link FROM projects
        WHERE full_description != ?
        ORDER BY published_at DESC
    """, (excluded_status,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_projects() -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, link FROM projects
        ORDER BY published_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_project_keywords(project_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT keywords_found FROM projects WHERE id = ?
    """, (project_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else ""

def get_project_clients(project_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT clients_matched FROM projects WHERE id = ?
    """, (project_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else ""

def keyword_matches_project(pid: int, keywords: list[str]) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT keywords_found FROM projects WHERE id = ?", (pid,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return False

    keywords_text = row[0].lower()
    return any(keyword in keywords_text for keyword in keywords)

# Настроить фильтры:
# | Статус | is_processed | Где использовать |
# | Новый | 0 | get_sorted_unprocessed_projects() |
# | Отклонённый | 1 | get_projects_by_status(1) |
# | Обработанный | 2 | get_projects_by_status(2) |
def get_projects_by_is_processed(status: int) -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, link FROM projects
        WHERE is_processed = ?
        ORDER BY published_at DESC
    """, (status,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_project_as_declined(project_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE projects
        SET is_processed = 1
        WHERE id = ?
    """, (project_id,))
    conn.commit()
    conn.close()
    print(f"🚫 Проект {project_id} помечен как отклонённый.")

def mark_project_as_favorite(project_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE projects
        SET is_favorite = 1
        WHERE id = ?
    """, (project_id,))
    conn.commit()
    conn.close()
    print(f"⭐ Проект {project_id} добавлен в избранное.")

def remove_project_from_favorite(project_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE projects
        SET is_favorite = 0
        WHERE id = ?
    """, (project_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Проект {project_id} удалён из избранного.")

def get_favorite_projects() -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, link FROM projects
        WHERE is_favorite = 1
        ORDER BY published_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def is_project_favorite(project_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT is_favorite FROM projects WHERE id = ?", (project_id,))
    result = cursor.fetchone()
    conn.close()
    return bool(result and result[0] == 1)

def save_reply_text(project_id: int, reply: str):
    print(f"[DB] 💾 Сохраняем reply_text в БД для проекта {project_id}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE projects SET reply_text = ? WHERE id = ?", (reply, project_id))
    print(f"[DB] 🎯 Статус обновления: {cursor.rowcount}")  # Добавим это
    conn.commit()
    conn.close()
    print(f"[DB] ✅ Отклик сохранён для проекта {project_id}")

def get_reply_text(project_id: int) -> str | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT reply_text FROM projects WHERE id = ?
    """, (project_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else None

def proverka_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM projects WHERE reply_text IS NOT NULL")
    reply_count = cursor.fetchone()[0]
    conn.close()
    return reply_count

