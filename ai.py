# # # # import os
# # # # from dotenv import load_dotenv
# # # # import aiohttp
# # # #
# # # # # Загружаем ключи из .env
# # # # load_dotenv()
# # # # OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
# # # #
# # # # async def generate_dual_reply(description: str, project_id: int) -> str:
# # # #     prompt = f"""
# # # # Ты опытный фрилансер. Сгенерируй персонализированный отклик на проект ID {project_id}.
# # # # Описание задачи:\n{description}\n
# # # # Отклик должен быть дружелюбным, профессиональным и показать, как ты решишь задачу клиента.
# # # # """
# # # #
# # # #     async with aiohttp.ClientSession() as session:
# # # #         headers = {
# # # #             "Authorization": f"Bearer {OPENROUTER_KEY}",
# # # #             "Content-Type": "application/json"
# # # #         }
# # # #
# # # #         async def fetch_model_reply(model_name: str) -> str:
# # # #             response = await session.post(
# # # #                 "https://openrouter.ai/api/v1/chat/completions",
# # # #                 headers=headers,
# # # #                 json={
# # # #                     "model": model_name,
# # # #                     "messages": [{"role": "user", "content": prompt}]
# # # #                 }
# # # #             )
# # # #             data = await response.json()
# # # #             return data["choices"][0]["message"]["content"].strip()
# # # #
# # # #         # Получаем отклики от двух моделей
# # # #         try:
# # # #             claude_reply = await fetch_model_reply("anthropic/claude-3-sonnet")
# # # #             deepseek_reply = await fetch_model_reply("deepseek-chat")
# # # #         except Exception as e:
# # # #             return f"⚠️ Ошибка при генерации откликов: {e}"
# # # #
# # # #         return (
# # # #             f"🟦 Отклик от Claude 3.5 Sonnet:\n\n{claude_reply}\n\n"
# # # #             f"🟨 Отклик от DeepSeek R1:\n\n{deepseek_reply}"
# # # #         )
# # #
# # # import os
# # # import aiohttp
# # # from dotenv import load_dotenv
# # #
# # # # Загружаем ключи
# # # load_dotenv()
# # # OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
# # #
# # # async def generate_dual_reply(description: str, project_id: int) -> str:
# # #     print(f"[FUNC] 🚀 Старт генерации dual-reply для проекта {project_id}")
# # #     print(f"[FUNC] 📄 Описание:\n{description}")
# # #
# # #     prompt = (
# # #         f"Ты профессиональный фрилансер. Сгенерируй персонализированный отклик на проект ID {project_id}.\n"
# # #         f"Описание задачи:\n{description}\n\n"
# # #         f"Отклик должен быть дружелюбным, уверенным и объяснять, как ты решишь задачу."
# # #     )
# # #
# # #     async with aiohttp.ClientSession() as session:
# # #         headers = {
# # #             "Authorization": f"Bearer {OPENROUTER_KEY}",
# # #             "Content-Type": "application/json"
# # #         }
# # #
# # #         async def fetch_reply(model_name: str) -> str:
# # #             print(f"[FETCH] 🔄 Отправка запроса к модели: {model_name}")
# # #             try:
# # #                 response = await session.post(
# # #                     "https://openrouter.ai/api/v1/chat/completions",
# # #                     headers=headers,
# # #                     json={
# # #                         "model": model_name,
# # #                         "messages": [{"role": "user", "content": prompt}]
# # #                     }
# # #                 )
# # #
# # #                 print(f"[FETCH] 📡 Статус ответа от {model_name}: {response.status}")
# # #                 data = await response.json()
# # #                 print(f"[FETCH] 📦 Ответ JSON от {model_name}:\n{data}")
# # #
# # #                 if "choices" not in data or not data["choices"]:
# # #                     print(f"[ERROR] ❌ Модель {model_name} не вернула choices.")
# # #                     return f"⚠️ Модель {model_name} не вернула результат."
# # #
# # #                 reply = data["choices"][0]["message"]["content"].strip()
# # #                 print(f"[FETCH] ✅ Успешный отклик от {model_name}")
# # #                 return reply
# # #
# # #             except Exception as e:
# # #                 print(f"[ERROR] ❌ Ошибка при обращении к {model_name}: {e}")
# # #                 return f"⚠️ Ошибка от модели {model_name}: {str(e)}"
# # #
# # #         # Получаем отклики от двух моделей
# # #         claude_text = await fetch_reply("command-r-plus")
# # #         deepseek_text = await fetch_reply("deepseek/deepseek-chat-v3-0324:free")
# # #
# # #         final_reply = (
# # #             f"🟦 Отклик от Claude 3.5 Sonnet:\n\n{claude_text}\n\n"
# # #             f"🟨 Отклик от DeepSeek R1:\n\n{deepseek_text}"
# # #         )
# # #
# # #         print(f"[FUNC] 📨 Финальный dual-reply:\n{final_reply}")
# # #         return final_reply
# #
# # import os
# # import aiohttp
# # from dotenv import load_dotenv
# #
# # # Загружаем .env переменные
# # load_dotenv()
# # OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
# #
# # async def generate_reply(description: str, project_id: int) -> str:
# #     print(f"[FUNC] 🚀 Генерация отклика для проекта {project_id}")
# #     print(f"[FUNC] 📄 Описание:\n{description}")
# #
# #     prompt = (
# #         # f"Ты фрилансер, специалист по визуальному брендингу и digital-продуктам.\n"
# #         f"Ты специалист фрилансер.\n"
# #         f"На основе описания проекта ID {project_id} ниже:\n\n{description}\n\n"
# #         f"Сгенерируй отклик в дружелюбной и уверенной форме. Расскажи, как ты можешь помочь клиенту, "
# #         f"упоминая релевантные навыки, опыт и подход. Текст должен звучать профессионально и привлекательно. "
# #         f"Но постарайся сделать отклик не более 200-500 символов, если это возможно. "
# #         f"Но если нужно что-то более детально, символов можно больше. "
# #         f"Не нужно писать разные заголовки в начале, например ***Отклик на проект*** или Ваш проект... "
# #         f"Также много спец символов это лишнее. Например если идет какой-то перечень, лучше использовать "-" или нумерацию. "
# #         f"В конце можешь добавить С уважением Дмитрий. "
# #     )
# #
# #     async with aiohttp.ClientSession() as session:
# #         url = "https://openrouter.ai/api/v1/chat/completions"
# #         headers = {
# #             "Authorization": f"Bearer {OPENROUTER_KEY}",
# #             "Content-Type": "application/json"
# #         }
# #         payload = {
# #             "model": "deepseek/deepseek-chat-v3-0324:free",
# #             "messages": [{"role": "user", "content": prompt}]
# #         }
# #
# #         try:
# #             print(f"[FETCH] 📤 Payload:\n{payload}")
# #             print(f"[FETCH] 🔄 Отправка запроса в DeepSeek...")
# #             response = await session.post(url, headers=headers, json=payload)
# #             print(f"[FETCH] 📡 Статус: {response.status}")
# #             data = await response.json()
# #             print(f"[FETCH] 📦 Ответ:\n{data}")
# #
# #             if "choices" not in data or not data["choices"]:
# #                 return "⚠️ Модель не вернула отклик. Попробуй позже."
# #
# #             reply = data["choices"][0]["message"]["content"].strip()
# #             print(f"[FUNC] ✅ Успешно сгенерировано:\n{reply}")
# #             return reply
# #
# #         except Exception as e:
# #             print(f"[ERROR] ❌ Ошибка генерации: {e}")
# #             return f"⚠️ Не удалось получить отклик: {str(e)}"
#
#
# # import os
# # import aiohttp
# # import asyncio
# # from dotenv import load_dotenv
# #
# # # 🔐 Загружаем переменные из .env
# # load_dotenv()
# # OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
#
# # async def generate_reply(description: str, project_id: int) -> str:
# #     print(f"[FUNC] 🚀 Генерация отклика для проекта {project_id}")
# #     print(f"[FUNC] 📄 Описание:\n{description}")
# #
# #     # Проверка наличия ключа
# #     if not OPENROUTER_KEY:
# #         print("[ERROR] 🛑 Ключ OPENROUTER_API_KEY не найден в .env!")
# #         return "🚫 Ошибка: ключ API не задан."
# #
# #     prompt = (
# #         f"Ты специалист фрилансер.\n"
# #         f"На основе описания проекта ID {project_id} ниже:\n\n{description}\n\n"
# #         f"Сгенерируй отклик в дружелюбной и уверенной форме. Расскажи, как ты можешь помочь клиенту, "
# #         f"упоминая релевантные навыки, опыт и подход. Текст должен звучать профессионально и привлекательно. "
# #         f"Но постарайся сделать отклик не более 200-500 символов, если это возможно. "
# #         f"Если нужно — можешь больше. Без заголовков типа 'Отклик на проект', без лишней символики. "
# #         f"Если указываешь цену, то она обязательно должна быть или в украинской гривне или долларах США. "
# #         f"Если нужен список, используй '-' или нумерацию. В конце добавь 'С уважением Дмитрий'."
# #     )
# #
# #     url = "https://openrouter.ai/api/v1/chat/completions"
# #     headers = {
# #         "Authorization": f"Bearer {OPENROUTER_KEY}",
# #         "Content-Type": "application/json"
# #     }
# #     payload = {
# #         "model": "deepseek/deepseek-chat-v3-0324:free",
# #         "messages": [{"role": "user", "content": prompt}]
# #     }
# #
# #     timeout = aiohttp.ClientTimeout(total=25)  # ⏱️ таймаут запроса
# #     try:
# #         print(f"[FETCH] 📤 Payload:\n{payload}")
# #         print(f"[FETCH] 🔄 Отправка запроса в DeepSeek...")
# #
# #         async with aiohttp.ClientSession(timeout=timeout) as session:
# #             try:
# #                 response = await session.post(url, headers=headers, json=payload)
# #             except Exception as post_error:
# #                 print(f"[ERROR] 🧨 Ошибка при POST-запросе: {post_error}")
# #                 return "🚫 Сбой при соединении с OpenRouter."
# #
# #             print(f"[FETCH] 📡 Статус: {response.status}")
# #
# #             if response.status != 200:
# #                 error_text = await response.text()
# #                 print(f"[ERROR] 📄 Ответ от API:\n{error_text}")
# #                 return f"❌ Ошибка API: {response.status}"
# #
# #             data = await response.json()
# #             print(f"[FETCH] 📦 Ответ:\n{data}")
# #
# #             if "choices" not in data or not data["choices"]:
# #                 return "⚠️ Модель не вернула отклик. Попробуй позже."
# #
# #             reply = data["choices"][0]["message"]["content"].strip()
# #             print(f"[FUNC] ✅ Успешно сгенерировано:\n{reply}")
# #             return reply
# #
# #     except asyncio.TimeoutError:
# #         print("[ERROR] ⏳ Таймаут запроса.")
# #         return "⚠️ Сервер слишком долго отвечает. Попробуй позже."
# #
# #     except Exception as e:
# #         print(f"[ERROR] ❌ Ошибка генерации: {e}")
# #         return "🚫 Внутренняя ошибка при получении отклика."
#
# import os
# import aiohttp
# import asyncio
# from dotenv import load_dotenv
#
# # 🔐 Загружаем переменные из .env
# load_dotenv()
# OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
#
# async def generate_reply(description: str, project_id: int) -> str:
#     print(f"[FUNC] 🚀 Генерация отклика для проекта {project_id}")
#     print(f"[FUNC] 📄 Описание:\n{description}")
#
#     # Проверка наличия ключа
#     if not OPENROUTER_KEY:
#         print("[ERROR] 🛑 Ключ OPENROUTER_API_KEY не найден в .env!")
#         return "🚫 Ошибка: ключ API не задан."
#
#     prompt = (
#         f"Ты крутой специалист фрилансер.\n"
#         f"На основе описания проекта ID {project_id} ниже:\n\n{description}\n\n"
#         f"Сгенерируй отклик в дружелюбной и уверенной форме. Расскажи, как ты можешь помочь клиенту, "
#         f"упоминая релевантные навыки, опыт и подход. Текст должен звучать профессионально и привлекательно. "
#         f"Но постарайся сделать отклик не более 200-500 символов, если это возможно. "
#         f"Если нужно — можешь больше. Без заголовков типа 'Отклик на проект', без лишней символики. "
#         f"Если указываешь цену, то она обязательно должна быть или в украинской гривне или долларах США. "
#         f"Если нужен список, используй '-' или нумерацию. В конце добавь 'С уважением Дмитрий'."
#     )
#
#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_KEY}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "model": "deepseek/deepseek-chat-v3-0324:free",
#         "messages": [{"role": "user", "content": prompt}]
#     }
#
#     timeout = aiohttp.ClientTimeout(total=25)  # ⏱️ таймаут запроса
#     try:
#         print(f"[FETCH] 📤 Payload:\n{payload}")
#         print(f"[FETCH] 🔄 Отправка запроса в DeepSeek...")
#
#         async with aiohttp.ClientSession(timeout=timeout) as session:
#             try:
#                 response = await session.post(url, headers=headers, json=payload)
#             except Exception as post_error:
#                 print(f"[ERROR] 🧨 Ошибка при POST-запросе: {post_error}")
#                 return "🚫 Сбой при соединении с OpenRouter."
#
#             print(f"[FETCH] 📡 Статус: {response.status}")
#
#             if response.status != 200:
#                 error_text = await response.text()
#                 print(f"[ERROR] 📄 Ответ от API:\n{error_text}")
#                 return f"❌ Ошибка API: {response.status}"
#
#             data = await response.json()
#             print(f"[FETCH] 📦 Ответ:\n{data}")
#
#             if "choices" not in data or not data["choices"]:
#                 return "⚠️ Модель не вернула отклик. Попробуй позже."
#
#             reply = data["choices"][0]["message"]["content"].strip()
#             print(f"[FUNC] ✅ Успешно сгенерировано:\n{reply}")
#             return reply
#
#     except asyncio.TimeoutError:
#         print("[ERROR] ⏳ Таймаут запроса.")
#         return "⚠️ Сервер слишком долго отвечает. Попробуй позже."
#
#     except Exception as e:
#         print(f"[ERROR] ❌ Ошибка генерации: {e}")
#         return "🚫 Внутренняя ошибка при получении отклика."

import os
import aiohttp
import asyncio
# from dotenv import load_dotenv
#
# load_dotenv()
# OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

async def generate_reply(description: str, project_id: int) -> str | None:
    print(f"[FUNC] 🚀 Генерация отклика для проекта {project_id}")
    print(f"[FUNC] 📄 Описание:\n{description}")

    if not OPENROUTER_KEY:
        print("[ERROR] 🔑 Ключ OPENROUTER_API_KEY не найден!")
        return None

    prompt = (
        f"Ты крутой специалист фрилансер.\n"
        f"На основе описания проекта ID {project_id} ниже:\n\n{description}\n\n"
        f"Сгенерируй отклик в дружелюбной и уверенной форме. Расскажи, как ты можешь помочь клиенту, "
        f"упоминая релевантные навыки, опыт и подход. Текст должен звучать профессионально и привлекательно. "
        f"Но постарайся сделать отклик не более 200-500 символов, если это возможно. "
        f"Если нужно — можешь больше. Без заголовков типа 'Отклик на проект', без лишней символики. "
        f"Если указываешь цену, то она обязательно должна быть или в украинской гривне или долларах США. "
        f"Если нужен список, используй '-' или нумерацию. В конце добавь 'С уважением Дмитрий'."
    )

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    timeout = aiohttp.ClientTimeout(total=25)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            response = await session.post(url, headers=headers, json=payload)
            print(f"[FETCH] 📡 Статус: {response.status}")

            if response.status != 200:
                error_text = await response.text()
                print(f"[ERROR] ❌ API ошибка:\n{error_text}")
                return None

            data = await response.json()
            print(f"[FETCH] 📦 Ответ:\n{data}")

            if "choices" not in data or not data["choices"]:
                print("[ERROR] ⚠️ Пустой список choices.")
                return None

            reply = data["choices"][0]["message"]["content"].strip()
            print(f"[FUNC] ✅ Успешно сгенерировано:\n{reply}")
            return reply

    except asyncio.TimeoutError:
        print("[ERROR] ⏳ Таймаут запроса.")
        return None

    except Exception as e:
        print(f"[ERROR] ❌ Внутренняя ошибка:\n{e}")
        return None