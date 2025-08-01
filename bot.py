import os
import subprocess
import logging
from datetime import datetime, timedelta
import glob
from typing import Optional

from anyio import sleep
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from ai import generate_reply

from db import (
    get_sorted_unprocessed_projects,
    update_project_description,
    fetch_full_description,
    get_projects_by_status,
    get_projects_excluding_status,
    get_all_projects,
    update_project_keywords,
    update_project_clients,
    keyword_matches_project,
    get_projects_by_is_processed,
    mark_project_as_declined,
    is_project_favorite,
    get_favorite_projects,
    mark_project_as_favorite,
    remove_project_from_favorite,
    # save_reply_text,
    # get_reply_text,
    proverka_db
)

from parser import fetch_new_projects, fetch_new_projects_fast

import os

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# # Загружаем токен из .env
# load_dotenv()
# TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден.")

# Настраиваем логирование ошибок
error_log_file = "bot-errors.log"
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
error_handler.setFormatter(log_formatter)
error_handler.setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING, handlers=[error_handler])

# Удаление старых логов
def cleanup_logs(days: int = 5):
    cutoff = datetime.now() - timedelta(days=days)
    for log_file in glob.glob("bot-*.log"):
        try:
            date_part = log_file.split("-")[1].split(".")[0]
            file_date = datetime.strptime(date_part, "%Y-%m-%d")
            if file_date < cutoff:
                os.remove(log_file)
        except Exception as e:
            logging.warning(f"Не удалось удалить {log_file}: {e}")

# Функция запуска test.py
def extract_description(project_id: int, url: str) -> str:
    print(f"[EXTRACT] ⚙️ Запуск test.py для проекта {project_id} по ссылке: {url}")
    try:
        result = subprocess.run(
            ['python', 'test.py', str(project_id), url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            timeout=20
        )

        print(f"[EXTRACT] 📥 stdout:\n{result.stdout[:500]}")  # покажем первые 500 символов
        print(f"[EXTRACT] 📥 stderr:\n{result.stderr.strip() or 'Нет ошибок'}")

        lines = result.stdout.splitlines()
        description_started = False
        description = []

        for line in lines:
            if "📤 Описание извлечено" in line:
                description_started = True
                print(f"[EXTRACT] 🟢 Найден маркер начала описания")
                continue
            if description_started:
                print(f"[EXTRACT] ➕ Добавлена строка: {line.strip()}")
                description.append(line.strip())

        output = "\n".join(description).strip()
        if output:
            print(f"[EXTRACT] ✅ Описание извлечено: {repr(output[:200])}...")
        else:
            print(f"[EXTRACT] ⚠️ Описание оказалось пустым.")

        return output or "❌ Описание пустое."
    except subprocess.TimeoutExpired:
        print(f"[EXTRACT] ⏱️ Время ожидания subprocess.run превысило лимит.")
        return "⏱️ Превышен лимит времени."
    except Exception as e:
        print(f"[EXTRACT] 🔥 Ошибка запуска test.py: {e}")
        return f"🔥 Ошибка запуска test.py: {e}"
# def extract_description(project_id: int, url: str) -> str:
#     try:
#         result = subprocess.run(
#             ['python', 'test.py', str(project_id), url],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             encoding='utf-8',
#             timeout=20
#         )
#         lines = result.stdout.splitlines()
#         description_started = False
#         description = []
#         for line in lines:
#             if "📤 Описание извлечено" in line:
#                 description_started = True
#                 continue
#             if description_started:
#                 description.append(line.strip())
#         output = "\n".join(description).strip()
#         return output or "❌ Описание пустое."
#     except subprocess.TimeoutExpired:
#         return "⏱️ Превышен лимит времени."
#     except Exception as e:
#         return f"🔥 Ошибка запуска test.py: {e}"

# Храним последовательность для каждого user_id
project_sequence = {}

# 👋 Команда /start — показывает начальное меню
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Найти проекты", callback_data="find_project")],
        [InlineKeyboardButton("📂 Показать проекты", callback_data="show_projects")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Привет! Выбери действие:", reply_markup=markup)

# 📥 Команда /desc <url> — извлекает описание по ссылке
async def desc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    message_text = update.message.text.strip()
    url = args[0] if args else message_text.split(maxsplit=1)[1] if len(message_text.split()) > 1 else None
    if not url:
        await update.message.reply_text("ℹ️ Используй: /desc <ссылка>")
        return
    await update.message.reply_text("🔍 Извлекаю описание...")
    description = extract_description(0, url)
    await update.message.reply_text(description)

# 📊 Команда /status — считает необработанные проекты
# async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         count = len(get_sorted_unprocessed_projects())
#         await update.message.reply_text(f"🔢 Необработанных проектов: {count}")
#     except Exception as e:
#         logging.warning(f"Ошибка в /status: {e}")
#         await update.message.reply_text("⚠️ Ошибка получения данных.")
async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = len(get_sorted_unprocessed_projects())
        await update.message.reply_text(f"🔢 Необработанных проектов: {count}")

        reply_count=proverka_db()
        await update.message.reply_text(f"📋 Сохранённых откликов: {reply_count}")
    except Exception as e:
        logging.warning(f"Ошибка в /status: {e}")
        await update.message.reply_text("⚠️ Ошибка получения данных.")

# 📤 Отправка одного проекта (по user_id и текущему индексу)
async def send_project(query, user_id):
    seq = project_sequence.get(user_id)

    if not seq or seq["index"] >= len(seq["list"]):
        keyboard = [
            [InlineKeyboardButton("🔍 Найти проекты", callback_data="find_projects")],
            [InlineKeyboardButton("📋 Показать проекты", callback_data="show_projects")]
        ]
        await query.message.reply_text(
            "📭 Больше проектов нет. Что дальше?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    pid, link = seq["list"][seq["index"]]
    keyboard = [
        [InlineKeyboardButton("📄 Описание", callback_data=f"desc_{pid}")],
        [InlineKeyboardButton("📨 Отклик", callback_data=f"reply_{pid}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{pid}")],
        [InlineKeyboardButton("➡️ Следующий", callback_data="next_project")],
        [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]  # 🔙 Новая кнопка
    ]

    is_fav = is_project_favorite(pid)

    if is_fav:
        keyboard.append([InlineKeyboardButton("🗑️ Убрать из избранного", callback_data=f"unfavorite_{pid}")])
    else:
        keyboard.append([InlineKeyboardButton("⭐ В избранное", callback_data=f"favorite_{pid}")])

    await query.message.reply_text(
        f"📌 Проект ID {pid}\n🔗 {link}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_projects_list(update, context, projects):
    if not projects:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📭 Нет проектов по выбранному фильтру."
        )
        return

    for pid, link in projects:
        keyboard = [
            [InlineKeyboardButton("📄 Описание", callback_data=f"desc_{pid}")],
            [InlineKeyboardButton("📨 Отклик", callback_data=f"reply_{pid}")],
            [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{pid}")],
            [InlineKeyboardButton("➡️ Следующий", callback_data="next_project")]
        ]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📌 Проект ID {pid}\n🔗 {link}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "find_project":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Быстрый поиск проектов", callback_data="find_fast_project")],
            [InlineKeyboardButton("Поиск по ключевым словам", callback_data="find_key_project")],
            [InlineKeyboardButton("Поиск всех проектов", callback_data="find_all_project")],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]  # 🚪 Кнопка возврата
        ])
        await query.edit_message_text("📂 Выберите фильтр поиска проектов:", reply_markup=keyboard)

    elif data == "find_all_project":
        # await query.delete_message()
        msg = await query.edit_message_text("⏳ Загрузка проектов... 0%")
        # from parser import fetch_new_projects
        await fetch_new_projects(progress_msg=msg)


    elif data == "find_fast_project":
        # await query.delete_message()
        msg = await query.message.reply_text("⚡ Быстрый поиск: запускаем парсер...")
        # from parser import fetch_new_projects_fast
        await fetch_new_projects_fast(progress_msg=msg)

    elif data == "find_key_project":
        print("по ключевым словам поиск проектов")

    elif data == "show_projects":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ Избранные", callback_data="show_favorite")],
            [InlineKeyboardButton("🔍 По ключевым словам", callback_data="show_by_keywords")],
            [InlineKeyboardButton("✅ Обработанный", callback_data="show_not_declined")],
            [InlineKeyboardButton("❌ Отклонённые", callback_data="show_declined")],
            [InlineKeyboardButton("📋 Все проекты", callback_data="show_all")],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]  # 🚪 Кнопка возврата
        ])
        await query.edit_message_text("📂 Выберите фильтр проектов:", reply_markup=keyboard)

    elif data == "show_favorite":
        projects = get_favorite_projects()
        project_sequence[user_id] = {"list": projects, "index": 0}
        await query.delete_message()
        await send_project(query, user_id)

    elif data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🔍 Найти проекты", callback_data="find_project")],
            [InlineKeyboardButton("📂 Показать проекты", callback_data="show_projects")]
        ]
        await query.edit_message_text("🏠 Главное меню:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "show_declined":
        projects = get_projects_by_is_processed(1)
        project_sequence[user_id] = {"list": projects, "index": 0}
        await query.delete_message()
        await send_project(query, user_id)

    elif data == "show_not_declined":
        projects = get_projects_by_is_processed(2)
        project_sequence[user_id] = {"list": projects, "index": 0}
        await query.delete_message()
        await send_project(query, user_id)

    elif data == "show_all":
        projects = get_all_projects()
        project_sequence[user_id] = {"list": projects, "index": 0}
        await query.delete_message()
        await send_project(query, user_id)

    elif data == "show_by_keywords":
        context.user_data["keyword_mode"] = True
        await query.edit_message_text("🔍 Введите ключевые слова для фильтрации:")

    elif data == "next_project":
        seq = project_sequence.get(user_id)
        if seq:
            seq["index"] += 1
            await query.delete_message()
            await send_project(query, user_id)


    elif data.startswith("desc_"):
        pid = int(data.split("_")[1])
        link = find_project_by_id(pid)  # 🔍 Теперь ищем везде
        if not link:
            await query.message.reply_text("❓ Ссылка на проект не найдена.")
            return
        extract_description(pid, link)
        description = fetch_full_description(pid)
        await query.edit_message_reply_markup(reply_markup=None)
        seq = project_sequence.get(user_id)
        if seq:
            seq["index"] += 1
        keyboard = [
            [InlineKeyboardButton("📨 Отклик", callback_data=f"reply_{pid}")],
            [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{pid}")],
            [InlineKeyboardButton("➡️ Следующий", callback_data="next_project")],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]  # 👍 Навигация
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.delete_message()
        await query.message.reply_text(description or "❌ Описание не найдено.", reply_markup=markup)

    elif data.startswith("reject_"):
        pid = int(data.split("_")[1])
        mark_project_as_declined(pid)  # Просто вызываем функцию
        await query.answer("🚫 Отклонён.")
        seq = project_sequence.get(user_id)
        if seq:
            seq["index"] += 1
        await query.delete_message()
        await send_project(query, user_id)

    elif data.startswith("favorite_"):
        pid = int(data.split("_")[1])
        mark_project_as_favorite(pid)
        await query.answer("⭐ Добавлено в избранное")
        await query.delete_message()
        await send_project(query, user_id)

    elif data.startswith("unfavorite_"):
        pid = int(data.split("_")[1])
        remove_project_from_favorite(pid)
        await query.answer("🗑️ Удалено из избранного")
        await query.delete_message()
        await send_project(query, user_id)

    elif data.startswith("kopi_text"):
        print("📋 Обработчик копирования текста активирован.")
        # 🔍 Получаем текущий ID проекта из context.user_data
        pid = context.user_data.get("current_project_id")
        print("🆔 Полученный project_id:", pid)
        if not pid:
            print("❌ Project ID не найден в user_data.")
            await query.edit_message_text("⚠️ Ошибка: Не удалось определить ID проекта.")
            return
        # 🔄 Получаем reply_text из базы данных
        import db
        reply_text = db.get_reply_text(pid)
        # reply_text = get_reply_text(pid)
        print("📦 Получен reply_text из БД:", repr(reply_text))
        if not reply_text:
            print("⚠️ reply_text отсутствует или пуст.")
            await query.edit_message_text("⚠️ Нет отклика для копирования.")
            return
        # 🔗 Получаем ссылку на проект
        link = find_project_by_id(pid)
        print("🔗 Сгенерирована ссылка на проект:", link)
        # 📋 Формируем кнопку и сообщение
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📂 Открыть проект", url=link)],
            [InlineKeyboardButton("⬅️ Назад", callback_data=f"reply_{pid}")]
        ])
        print("🧾 Отправляем текст отклика в чат...")
        await query.edit_message_text(
            f"📋 Отклик для копирования:\n\n<pre>{reply_text}</pre>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        print("✅ Отклик успешно отправлен в чат.")

    elif data.startswith("edit_text"):
        print("✏️ Редактируем отклик")
        pid = context.user_data.get("current_project_id")
        import db
        reply_text = db.get_reply_text(pid)
        # reply_text = get_reply_text(pid)
        if not reply_text:
            await query.edit_message_text("⚠️ Отклик не найден.")
            return
        context.user_data["editing_state"] = "editing_reply"
        context.user_data["current_project_id"] = pid
        await query.edit_message_text("✏️ Отправь отредактированный отклик ниже.")
        await query.message.reply_text(reply_text)

    # elif data.startswith("reply_"):
    #     pid = int(data.split("_")[1])
    #     print(f"pid {pid}")
    #
    #     description = fetch_full_description(pid)
    #     if not description:
    #         link = find_project_by_id(pid)
    #         print(f"link {link}")
    #         if link:
    #             extract_description(pid, link)
    #             description = fetch_full_description(pid)
    #
    #     if not description:
    #         await query.edit_message_text("❌ Не удалось получить описание проекта.")
    #         return
    #
    #     await query.edit_message_text("🤖 Генерирую отклик...")
    #
    #     reply_text = await generate_reply(description, pid)
    #     if reply_text:
    #         from db import save_reply_text
    #         save_reply_text(pid, reply_text)
    #
    #     # if reply_text:
    #         keyboard = InlineKeyboardMarkup([
    #             [InlineKeyboardButton("Копировать", callback_data="kopi_text")],
    #             [InlineKeyboardButton("Изменить", callback_data="edit_text")],
    #             [InlineKeyboardButton("Следующий", callback_data="next_project")],
    #             [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
    #         ])
    #         await query.edit_message_text(reply_text, reply_markup=keyboard)
    #     else:
    #         retry_keyboard = InlineKeyboardMarkup([
    #             [InlineKeyboardButton("🔁 Повторить", callback_data=f"retry_reply_{pid}")]
    #         ])
    #         await query.edit_message_text("⚠️ Не удалось сгенерировать отклик.", reply_markup=retry_keyboard)

    # elif data.startswith("reply_"):
    #     pid = int(data.split("_")[1])
    #     context.user_data["current_project_id"] = pid  # 👈 сохраняем ID
    #     print("📝 Установлен current_project_id:", pid)
    #
    #     print(f"[BOT] ▶️ Начата генерация отклика для проекта {pid}")
    #
    #     description = fetch_full_description(pid)
    #     print(f"[BOT] 📄 Описание из БД: {description[:100]}")  # покажем первые 100 символов
    #
    #     if not description:
    #         print(f"[BOT] ⚠️ Нет описания, пробуем fetch по ссылке…")
    #         link = find_project_by_id(pid)
    #         print(f"[BOT] 🔗 Ссылка: {link}")
    #         if link:
    #             extract_description(pid, link)
    #             description = fetch_full_description(pid)
    #             print(f"[BOT] 📄 После fetch: {description[:100]}")
    #
    #     if not description:
    #         await query.edit_message_text("❌ Не удалось получить описание проекта.")
    #         print(f"[BOT] ❌ Описание так и не найдено")
    #         return
    #
    #     await query.edit_message_text("🤖 Генерирую отклик...")
    #     print(f"[BOT] 🧠 Отправлен текст 'Генерирую отклик…'")
    #
    #     reply_text = await generate_reply(description, pid)
    #     print(f"[BOT] 🤖 Сгенерирован отклик:\n{reply_text}")
    #
    #     if reply_text:
    #         from db import save_reply_text
    #         print(f"[BOT] 💾 Пытаемся вызвать save_reply_text…")
    #         save_reply_text(pid, reply_text)
    #         print(f"[BOT] ✅ Отклик успешно сохранён")
    #
    #         keyboard = InlineKeyboardMarkup([
    #             [InlineKeyboardButton("Копировать", callback_data="kopi_text")],
    #             [InlineKeyboardButton("Изменить", callback_data="edit_text")],
    #             [InlineKeyboardButton("Следующий", callback_data="next_project")],
    #             [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
    #         ])
    #         print(f"[BOT] 🧾 Отправляем отклик в чате…")
    #         await query.edit_message_text(reply_text, reply_markup=keyboard)
    #     else:
    #         print(f"[BOT] ⚠️ Отклик не получен — показываем кнопку повтор")
    #         retry_keyboard = InlineKeyboardMarkup([
    #             [InlineKeyboardButton("🔁 Повторить", callback_data=f"retry_reply_{pid}")]
    #         ])
    #         await query.edit_message_text("⚠️ Не удалось сгенерировать отклик.", reply_markup=retry_keyboard)

    elif data.startswith("reply_"):
        pid = int(data.split("_")[1])
        context.user_data["current_project_id"] = pid
        print("📝 Установлен current_project_id:", pid)

        from db import get_reply_text, save_reply_text

        print(f"[BOT] ▶️ Запрошен отклик для проекта {pid}")

        # 💬 Сначала пробуем взять отклик из БД
        cached_reply = get_reply_text(pid)
        print(f"[DB] 🔍 Проверка reply_text в БД: {repr(cached_reply)}")

        if cached_reply:
            print(f"[BOT] ✅ Найден готовый отклик — используем без генерации.")
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Копировать", callback_data="kopi_text")],
                [InlineKeyboardButton("Изменить", callback_data="edit_text")],
                [InlineKeyboardButton("Следующий", callback_data="next_project")],
                [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
            ])
            await query.edit_message_text(cached_reply, reply_markup=keyboard)
            return  # ⛔ Прерываем дальнейшую генерацию

        # 📦 Иначе начинаем процесс генерации
        print(f"[BOT] 🔄 Генерация отклика…")
        description = fetch_full_description(pid)
        print(f"[DEBUG] raw description: {repr(description)}")
        # print(f"[BOT] 📄 Описание из БД: {description[:100]}")
        # print(f"[DEBUG] Описание перед проверкой: {repr(description)}")

        if not description:
        # if description is None:
            print(f"[BOT] ⚠️ Нет описания — пробуем fetch по ссылке")
            link = find_project_by_id(pid)
            print(f"[BOT] 🔗 Ссылка: {link}")
            if link:
                extract_description(pid, link)
                description = fetch_full_description(pid)
                print(f"[BOT] 📄 После fetch: {description[:100]}")

        if not description:
            print(f"[BOT] ❌ Описание так и не найдено")
            await query.edit_message_text("❌ Не удалось получить описание проекта.")
            return

        await query.edit_message_text("🤖 Генерирую отклик...")
        reply_text = await generate_reply(description, pid)
        print(f"[BOT] 🤖 Сгенерированный отклик:\n{reply_text}")

        if reply_text:
            print(f"[BOT] 💾 Сохраняем отклик в БД…")
            save_reply_text(pid, reply_text)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Копировать", callback_data="kopi_text")],
                [InlineKeyboardButton("Изменить", callback_data="edit_text")],
                [InlineKeyboardButton("Следующий", callback_data="next_project")],
                [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
            ])
            print(f"[BOT] ✅ Отклик сохранён и отправлен в чат")
            await query.edit_message_text(reply_text, reply_markup=keyboard)
        else:
            print(f"[BOT] ⚠️ Отклик не получен — отображаем кнопку повторной попытки")
            retry_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Повторить", callback_data=f"retry_reply_{pid}")]
            ])
            await query.edit_message_text("⚠️ Не удалось сгенерировать отклик.", reply_markup=retry_keyboard)

    elif data.startswith("retry_reply_"):
        pid = int(data.split("_")[2])
        print(f"[RETRY] 🔄 Повтор генерации для проекта {pid}")
        description = fetch_full_description(pid)
        if not description:
            link = find_project_by_id(pid)
            print(f"link {link}")
            if link:
                extract_description(pid, link)
                description = fetch_full_description(pid)
        if not description:
            await query.edit_message_text("❌ Описание проекта не найдено.")
            return
        await query.edit_message_text("🔄 Повторная генерация отклика...")
        reply_text = await generate_reply(description, pid)
        if reply_text:
            from db import save_reply_text
            print(f"[BOT] 💾 Пытаемся вызвать save_reply_text…")
            save_reply_text(pid, reply_text)
            print(f"[BOT] ✅ Отклик успешно сохранён")
        # if reply_text:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Копировать", callback_data="kopi_text")],
                [InlineKeyboardButton("Изменить", callback_data="edit_text")],
                [InlineKeyboardButton("Следующий", callback_data="next_project")],
                [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
            ])
            await query.edit_message_text(reply_text, reply_markup=keyboard)
        else:
            retry_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Ещё попытка", callback_data=f"retry_reply_{pid}")]
            ])
            await query.edit_message_text("❌ Сбой при повторной попытке.", reply_markup=retry_keyboard)

    # elif data.startswith("reply_"):
    #     pid = int(data.split("_")[1])
    #     print(f"pid {pid}")
    #     description = fetch_full_description(pid)
    #     if not description:
    #         link = find_project_by_id(pid)
    #         print(f"link {link}")
    #         if link:
    #             extract_description(pid, link)
    #             description = fetch_full_description(pid)
    #
    #     if not description:
    #         await query.message.reply_text("❌ Не удалось получить описание проекта.")
    #         return
    #
    #     # await query.message.reply_text("🤖 Генерирую отклик...")
    #     await query.edit_message_text("🤖 Генерирую отклик...")
    #     reply_text = await generate_reply(description, pid)
    #     keyboard = InlineKeyboardMarkup([
    #         [InlineKeyboardButton("Копировать", callback_data="kopi_text")],
    #         [InlineKeyboardButton("Изменить", callback_data="edit_text")],
    #         [InlineKeyboardButton("Следующий", callback_data="next_project")],
    #         [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]  # 🚪 Кнопка возврата
    #     ])
    #     await query.edit_message_text(reply_text, reply_markup=keyboard)
    #
    #     # await query.message.reply_text(reply_text)

# async def handle_text_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     text = update.message.text
#
#     if context.user_data.get("editing_state") == "editing_reply":
#         new_text = text
#         pid = context.user_data.get("current_project_id")
#         save_reply_text(pid, new_text)
#         context.user_data["editing_state"] = None
#
#         keyboard = InlineKeyboardMarkup([
#             [InlineKeyboardButton("Копировать", callback_data="kopi_text")],
#             [InlineKeyboardButton("Изменить", callback_data="edit_text")],
#             [InlineKeyboardButton("Следующий", callback_data="next_project")],
#             [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
#         ])
#         await update.message.reply_text(f"✅ Отклик сохранён:\n\n{new_text}", reply_markup=keyboard)

async def handle_text_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    print(f"[MSG] ✉️ Получено текстовое сообщение от пользователя {user_id}: {text}")

    if context.user_data.get("editing_state") == "editing_reply":
        pid = context.user_data.get("current_project_id")
        print(f"[EDIT] 🛠️ Редактируем отклик для проекта {pid}")

        if not pid:
            await update.message.reply_text("❌ Ошибка: не найден ID проекта.")
            return

        from db import save_reply_text
        save_reply_text(pid, text)
        print(f"[EDIT] ✅ Отклик сохранён в БД:\n{text}")

        context.user_data["editing_state"] = None  # сбрасываем состояние

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Копировать", callback_data="kopi_text")],
            [InlineKeyboardButton("Изменить", callback_data="edit_text")],
            [InlineKeyboardButton("Следующий", callback_data="next_project")],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
        ])
        await update.message.reply_text(f"✅ Отклик сохранён:\n\n{text}", reply_markup=keyboard)


# 💬 Роутер для обычных текстовых сообщений
async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # ✏️ Проверка состояния редактирования отклика
    if context.user_data.get("editing_state") == "editing_reply":
        pid = context.user_data.get("current_project_id")
        new_text = update.message.text

        print(f"[EDIT] 💾 Сохраняем отклик для проекта {pid}")

        if not pid:
            await update.message.reply_text("❌ Ошибка: не найден ID проекта.")
            return

        from db import save_reply_text
        save_reply_text(pid, new_text)

        context.user_data["editing_state"] = None  # сбрасываем флаг

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Копировать", callback_data="kopi_text")],
            [InlineKeyboardButton("Изменить", callback_data="edit_text")],
            [InlineKeyboardButton("Следующий", callback_data="next_project")],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
        ])
        await update.message.reply_text("✅ Отклик обновлён!", reply_markup=keyboard)
        return

    # 🔍 Проверка режима keyword_mode
    if context.user_data.get("keyword_mode"):
        context.user_data["keyword_mode"] = False  # Выключаем режим после ввода

        # 🔎 Получаем ключевые слова
        keywords = [k.strip().lower() for k in text.split(",")]

        # 🔍 Фильтруем проекты по keyword_found
        all_projects = get_sorted_unprocessed_projects()  # [(pid, link)]
        matched_projects = [
            (pid, link) for pid, link in all_projects
            if keyword_matches_project(pid, keywords)
        ]

        user_id = update.effective_user.id
        if matched_projects:
            project_sequence[user_id] = {"list": matched_projects, "index": 0}
            await send_project(update, user_id)
        else:
            keyboard = [
                [InlineKeyboardButton("🔍 Найти проекты", callback_data="find_projects")],
                [InlineKeyboardButton("📋 Показать проекты", callback_data="show_projects")]
            ]
            await update.message.reply_text(
                "❌ Ничего не найдено по этим ключевым словам. Что дальше?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return

    # 👇 Обычные команды или fallback
    if text.startswith("/desc "):
        await desc_handler(update, context)

# async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text = update.message.text.strip()
#
#     if context.user_data.get("keyword_mode"):
#         context.user_data["keyword_mode"] = False  # Выключаем режим после ввода
#
#         # 🔎 Получаем ключевые слова
#         keywords = [k.strip().lower() for k in text.split(",")]
#
#         # 🔍 Фильтруем проекты по keyword_found
#         all_projects = get_sorted_unprocessed_projects()  # [(pid, link)]
#         matched_projects = [
#             (pid, link) for pid, link in all_projects
#             if keyword_matches_project(pid, keywords)
#         ]
#
#         user_id = update.effective_user.id
#         if matched_projects:
#             project_sequence[user_id] = {"list": matched_projects, "index": 0}
#             await send_project(update, user_id)
#         else:
#             # await update.message.reply_text("❌ Ничего не найдено по этим ключевым словам.")
#             keyboard = [
#                 [InlineKeyboardButton("🔍 Найти проекты", callback_data="find_projects")],
#                 [InlineKeyboardButton("📋 Показать проекты", callback_data="show_projects")]
#             ]
#             await update.message.reply_text(
#                 "❌ Ничего не найдено по этим ключевым словам. Что дальше?",
#                 reply_markup=InlineKeyboardMarkup(keyboard)
#             )
#         return
#
#     # 👇 Обычные команды или fallback
#     if text.startswith("/desc "):
#         await desc_handler(update, context)

# 🔁 Фоновая задача — обрабатывает очередь из файла queue.txt
async def monitor_queue_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        if os.path.exists("queue.txt"):
            with open("queue.txt", "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
            if urls:
                for url in urls:
                    description = extract_description(0, url)
                    await context.bot.send_message(chat_id=CHAT_ID, text=description)
                with open("queue.txt", "w", encoding="utf-8") as f:
                    f.write("")
    except Exception as e:
        logging.warning(f"Очередь: {e}")

# Универсальная обёртка для поиска проекта по id
def find_project_by_id(pid: int) -> Optional[str]:
    sources = [
        get_sorted_unprocessed_projects(),      # Новый (is_processed = 0)
        get_projects_by_is_processed(1),        # Отклонённый (is_processed = 1)
        get_projects_by_is_processed(2),        # Обработанный (is_processed = 2)
    ]

    for source in sources:
        for i, link in source:
            if i == pid:
                return link
    return None

# 🚀 Финальная функция запуска бота
def main():
    cleanup_logs()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("desc", desc_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_re/ply))
    app.add_handler(CallbackQueryHandler(callback_handler))

    app.job_queue.run_repeating(monitor_queue_job, interval=5, first=5)

    print("🧠 Бот готов.")
    app.run_polling()

if __name__ == "__main__":
    main()