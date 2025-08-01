# parser.py
import requests
import os
import re
import unicodedata
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from config import KEYWORDS, FAVORITE_CLIENTS, ENV_PATH
from db import initialize_db, insert_project, update_project_keywords, update_project_clients, get_project_keywords, get_project_clients
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

import httpx
import asyncio
from db import (
    insert_project,
    # has_filters,
    # is_relevant,
    # get_matched_keywords,
    # get_matched_clients,
    get_project_keywords,
    get_project_clients,
    update_project_keywords,
    update_project_clients
)
from slugify import slugify

# 🔠 Генерация slug для URL
def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text).lower()
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-") or "project"

def has_filters():
    return bool(KEYWORDS or FAVORITE_CLIENTS)

def is_relevant(title, description, employer_login):
    content = f"{title} {description}".lower()
    keyword_match = any(k.lower() in content for k in KEYWORDS)
    author_match = employer_login and any(c.lower() == employer_login.lower() for c in FAVORITE_CLIENTS)
    return keyword_match or author_match

# 🔐 API конфигурация
# load_dotenv(dotenv_path=ENV_PATH)
# API_TOKEN = os.getenv("FREELANCEHUNT_API_TOKEN")
API_TOKEN = os.environ.get("FREELANCEHUNT_API_TOKEN")
API_URL = os.environ.get("https://api.freelancehunt.com/v2/projects")
# API_URL = "https://api.freelancehunt.com/v2/projects"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

# --- Импорты в начале файла ---
from config import KEYWORDS, FAVORITE_CLIENTS

def get_matched_keywords(title: str, description: str) -> list:
    text = f"{title} {description}".lower()
    return [kw for kw in KEYWORDS if kw.lower() in text]

def get_matched_clients(login: str) -> list:
    if login and login.lower() in [client.lower() for client in FAVORITE_CLIENTS]:
        return [login]
    return []

async def fetch_new_projects(progress_msg=None):
    results = []
    page = 1
    max_pages = 150

    total_pages = 0
    projects_uploaded = 0
    projects_failed = 0

    progress_percent = 0
    progress_step = 1

    async with httpx.AsyncClient() as client:
        while True:
            url = f"{API_URL}?page[number]={page}"
            try:
                response = await client.get(url, headers=headers)
            except Exception as e:
                print(f"[ERROR] Не удалось получить страницу {page}: {e}")
                break

            if response.status_code != 200:
                print(f"[ERROR] Страница {page} завершилась с кодом: {response.status_code}")
                break

            data = response.json()
            projects = data.get("data", [])
            print(f"[API] Страница {page}, проектов: {len(projects)}")
            total_pages += 1

            if not projects:
                break

            for project in projects:
                try:
                    project_id = int(project.get("id"))
                    attrs = project.get("attributes", {})

                    title = attrs.get("name", "Без названия")
                    description = attrs.get("description", "")
                    published_at = attrs.get("published_at", "")
                    budget = attrs.get("budget") or {}
                    budget_amount = budget.get("amount")
                    budget_currency = budget.get("currency")
                    skills = [s.get("name") for s in attrs.get("skills", []) if s.get("name")]
                    is_premium = attrs.get("is_premium", False)

                    employer = attrs.get("employer", {}) or {}
                    employer_login = employer.get("login")
                    employer_name = employer.get("first_name", "")
                    employer_surname = employer.get("last_name", "")

                    links = project.get("links", {}) or {}
                    api_link = links.get("self", {}).get("api")
                    pid = api_link.split("/")[-1] if isinstance(api_link, str) else None
                    slug = slugify(title)
                    web_link = f"https://freelancehunt.com/project/{slug}/{pid}.html" if slug and pid else "#"

                    if not has_filters() or is_relevant(title, description, employer_login):
                        project_data = {
                            "id": project_id,
                            "title": title,
                            "link": web_link,
                            "description": description,
                            "budget_amount": budget_amount,
                            "budget_currency": budget_currency,
                            "employer_login": employer_login,
                            "employer_name": employer_name,
                            "employer_surname": employer_surname,
                            "is_premium": is_premium,
                            "skills": skills,
                            "published_at": published_at
                        }

                        was_inserted = insert_project(project_data)
                        status = "🟢 Добавлен" if was_inserted else "⚪️ Уже был"
                        print(f"→ {title[:50]}... {status}")

                        found_keywords = get_matched_keywords(title, description)
                        matched_clients = get_matched_clients(employer_login)

                        existing_keywords = get_project_keywords(project_id)
                        existing_clients = get_project_clients(project_id)

                        if set(found_keywords) != set(existing_keywords.split(", ")) or \
                           set(matched_clients) != set(existing_clients.split(", ")):
                            update_project_keywords(project_id, ", ".join(found_keywords))
                            update_project_clients(project_id, ", ".join(matched_clients))

                        if was_inserted:
                            projects_uploaded += 1
                except Exception as e:
                    projects_failed += 1
                    print(f"❌ Ошибка при обработке проекта ID {project.get('id')}: {e}")

            # Обновление прогресса
            percent_now = int((page / max_pages) * 100)
            if percent_now >= progress_percent + progress_step and progress_msg:
                progress_percent += progress_step
                try:
                    await progress_msg.edit_text(f"⏳ Загрузка проектов... {progress_percent}%")
                    await asyncio.sleep(0.5)
                except Exception:
                    pass

            page += 1
            if page > max_pages:
                break

    # Финальное сообщение
    keyboard = [
        [InlineKeyboardButton("🔍 Найти проекты", callback_data="find_project")],
        [InlineKeyboardButton("📂 Показать проекты", callback_data="show_projects")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if progress_msg:
        await progress_msg.edit_text(
            f"✅ Загрузка завершена!\n🔹 Просмотрено страниц: {total_pages}\n✅ Добавлено: {projects_uploaded}\n⚠️ Ошибок: {projects_failed}\nЧто дальше?", reply_markup=markup
        )

    return results

async def fetch_new_projects_fast(progress_msg=None):
    results = []
    page = 1
    max_pages = 150
    duplicate_streak = 0
    duplicate_limit = 4  # 👈 после 4 подряд страниц с дубликатами остановимся

    total_pages = 0
    projects_uploaded = 0
    projects_failed = 0

    progress_percent = 0
    progress_step = 1

    async with httpx.AsyncClient() as client:
        while page <= max_pages:
            url = f"{API_URL}?page[number]={page}"
            try:
                response = await client.get(url, headers=headers)
            except Exception as e:
                print(f"[ERROR] Не удалось получить страницу {page}: {e}")
                break

            if response.status_code != 200:
                print(f"[ERROR] Страница {page} завершилась с кодом: {response.status_code}")
                break

            data = response.json()
            projects = data.get("data", [])
            print(f"[FAST] Страница {page}, проектов: {len(projects)}")
            total_pages += 1

            if not projects:
                break

            page_had_new = False

            for project in projects:
                try:
                    project_id = int(project.get("id"))
                    attrs = project.get("attributes", {})

                    title = attrs.get("name", "Без названия")
                    description = attrs.get("description", "")
                    published_at = attrs.get("published_at", "")
                    budget = attrs.get("budget") or {}
                    budget_amount = budget.get("amount")
                    budget_currency = budget.get("currency")
                    skills = [s.get("name") for s in attrs.get("skills", []) if s.get("name")]
                    is_premium = attrs.get("is_premium", False)

                    employer = attrs.get("employer", {}) or {}
                    employer_login = employer.get("login")
                    employer_name = employer.get("first_name", "")
                    employer_surname = employer.get("last_name", "")

                    links = project.get("links", {}) or {}
                    api_link = links.get("self", {}).get("api")
                    pid = api_link.split("/")[-1] if isinstance(api_link, str) else None
                    slug = slugify(title)
                    web_link = f"https://freelancehunt.com/project/{slug}/{pid}.html" if slug and pid else "#"

                    if not has_filters() or is_relevant(title, description, employer_login):
                        project_data = {
                            "id": project_id,
                            "title": title,
                            "link": web_link,
                            "description": description,
                            "budget_amount": budget_amount,
                            "budget_currency": budget_currency,
                            "employer_login": employer_login,
                            "employer_name": employer_name,
                            "employer_surname": employer_surname,
                            "is_premium": is_premium,
                            "skills": skills,
                            "published_at": published_at
                        }

                        was_inserted = insert_project(project_data)
                        status = "🟢 Добавлен" if was_inserted else "⚪️ Уже был"
                        print(f"[FAST] → {title[:50]}... {status}")

                        found_keywords = get_matched_keywords(title, description)
                        matched_clients = get_matched_clients(employer_login)

                        existing_keywords = get_project_keywords(project_id)
                        existing_clients = get_project_clients(project_id)

                        if set(found_keywords) != set(existing_keywords.split(", ")) or \
                           set(matched_clients) != set(existing_clients.split(", ")):
                            update_project_keywords(project_id, ", ".join(found_keywords))
                            update_project_clients(project_id, ", ".join(matched_clients))

                        if was_inserted:
                            projects_uploaded += 1
                            page_had_new = True
                except Exception as e:
                    projects_failed += 1
                    print(f"❌ Ошибка при обработке проекта ID {project.get('id')}: {e}")

            # 🔁 Проверка дубликатной полосы
            if page_had_new:
                duplicate_streak = 0
            else:
                duplicate_streak += 1
                print(f"[FAST] ⚪️ Все проекты уже есть в БД — streak: {duplicate_streak}")
                if duplicate_streak >= duplicate_limit:
                    print(f"[FAST] 🛑 Остановка: {duplicate_streak} подряд страниц с дубликатами.")
                    break

            # Обновление прогресса
            percent_now = int((page / max_pages) * 100)
            if percent_now >= progress_percent + progress_step and progress_msg:
                progress_percent += progress_step
                try:
                    await progress_msg.edit_text(f"⚡ Быстрый парсинг... {progress_percent}%")
                    await asyncio.sleep(0.3)
                except Exception:
                    pass

            page += 1

    # Финальное сообщение
    keyboard = [
        [InlineKeyboardButton("🔍 Найти проекты", callback_data="find_project")],
        [InlineKeyboardButton("📂 Показать проекты", callback_data="show_projects")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if progress_msg:
        await progress_msg.edit_text(
            f"✅ Быстрый парсинг завершён!\n🔹 Просмотрено страниц: {total_pages}\n✅ Добавлено: {projects_uploaded}\n⚠️ Ошибок: {projects_failed}",
            reply_markup=markup
        )

    return results

# 🚀 Главный запуск
if __name__ == "__main__":
    print("[INIT] Инициализация базы данных...")
    initialize_db()

    print("[START] Парсинг проектов...\n")
    fetch_new_projects()
    print("\n✅ Парсинг завершён.")