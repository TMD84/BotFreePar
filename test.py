# # from selenium import webdriver
# # from selenium.webdriver.chrome.service import Service
# # from webdriver_manager.chrome import ChromeDriverManager
# # from bs4 import BeautifulSoup
# # import time
# #
# # URL = "https://freelancehunt.com/project/treba-napisati-tekst-dlya-prezentatsiyi/1536218.html"
# #
# # # 🔧 Настройка браузера
# # options = webdriver.ChromeOptions()
# # options.add_argument("--start-maximized")
# # options.add_argument("--disable-blink-features=AutomationControlled")
# #
# # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# # driver.get(URL)
# # time.sleep(3)  # ⏳ Подождём рендеринг
# #
# # # 📄 Получение HTML
# # html = driver.page_source
# # driver.quit()
# #
# # # 💾 Сохраняем
# # with open("selenium_debug.html", "w", encoding="utf-8") as f:
# #     f.write(html)
# #
# # soup = BeautifulSoup(html, "html.parser")
# # block = soup.select_one("span[data-freelancehunt-selector='description']")
# # if block:
# #     print("📄 Описание:\n")
# #     print(block.get_text(separator="\n", strip=True))
# # else:
# #     print("❌ Описание не найдено.")
#
# # import sys
# # import time
# # from selenium import webdriver
# # from selenium.webdriver.chrome.service import Service
# # from webdriver_manager.chrome import ChromeDriverManager
# # from bs4 import BeautifulSoup
# #
# # print("📂 Запуск test.py...")
# #
# # # 📨 Получение аргумента
# # args = sys.argv
# # print(f"📨 Аргументы командной строки: {args}")
# # if len(args) < 2:
# #     print("❌ Не передана ссылка!")
# #     exit(1)
# #
# # URL = args[1]
# # print(f"🔗 Целевая ссылка: {URL}")
# #
# # # 🔧 Настройка браузера
# # print("🔧 Инициализируем Chrome через selenium...")
# # options = webdriver.ChromeOptions()
# # options.add_argument("--start-maximized")
# # options.add_argument("--disable-blink-features=AutomationControlled")
# #
# # try:
# #     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# #     print("✅ Chrome запущен")
# #
# #     print("🌐 Загружаем страницу проекта...")
# #     driver.get(URL)
# #     time.sleep(3)
# #     print("⏳ Страница должна быть загружена")
# #
# #     html = driver.page_source
# #     driver.quit()
# #     print("💾 HTML получен и браузер закрыт")
# #
# #     # ⛏️ Сохраняем HTML для отладки
# #     with open("selenium_debug.html", "w", encoding="utf-8") as f:
# #         f.write(html)
# #     print("🧩 HTML сохранён в файл selenium_debug.html")
# #
# #     # 📄 Парсинг описания
# #     soup = BeautifulSoup(html, "html.parser")
# #     print("🔍 Ищем описание внутри HTML...")
# #
# #     block = soup.select_one("span[data-freelancehunt-selector='description']")
# #     if block:
# #         description = block.get_text(separator="\n", strip=True)
# #         print("📤 Описание найдено, возвращаем...\n")
# #         print(description)
# #     else:
# #         print("❌ Описание не найдено в HTML")
# #         exit(1)
# #
# # except Exception as e:
# #     print(f"⚠️ Ошибка во время выполнения: {e}")
# #     exit(1)
#
# import sys
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
#
# # 🔠 Обеспечиваем корректный вывод текста
# sys.stdout.reconfigure(encoding="utf-8")
#
# print("📂 Запуск test.py...")
#
# # 📨 Получение аргументов
# args = sys.argv
# print(f"📨 Аргументы командной строки: {args}")
#
# if len(args) < 2:
#     print("❌ Ссылка не передана")
#     sys.exit(1)
#
# URL = args[1]
# print(f"🔗 Целевая ссылка: {URL}")
#
# # 🔧 Настройка браузера
# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
# options.add_argument("--disable-blink-features=AutomationControlled")
#
# try:
#     print("🚀 Запускаем Chrome через webdriver...")
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#
#     print("🌐 Загружаем страницу проекта...")
#     driver.get(URL)
#
#     # ⏳ Ожидаем появления блока описания
#     print("⏳ Ожидаем появления описания...")
#     WebDriverWait(driver, 1).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-freelancehunt-selector='description']"))
#     )
#
#     print("💾 Получаем исходный HTML")
#     html = driver.page_source
#     driver.quit()
#     print("✅ Браузер закрыт")
#
#     # 🧪 Парсинг HTML
#     soup = BeautifulSoup(html, "html.parser")
#     block = soup.find("span", {"data-freelancehunt-selector": "description"})
#
#     if block:
#         description = block.get_text(separator="\n", strip=True)
#         print("📤 Описание извлечено:\n")
#         print(description)
#     else:
#         print("❌ Описание не найдено.")
#         sys.exit(1)
#
# except Exception as e:
#     print(f"⚠️ Ошибка при выполнении: {e}")
#     try:
#         driver.quit()
#         print("🧹 Браузер закрыт после ошибки")
#     except:
#         pass
#     sys.exit(1)


# test.py
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from db import update_project_description, get_unprocessed_projects, get_all_projects

def save_description_to_db(project_id: int, description: str):
    print(f"📥 Сохраняем описание в БД для ID {project_id}")
    try:
        update_project_description(project_id, description)
        print(f"✅ Описание сохранено для проекта ID {project_id}")
    except Exception as e:
        print(f"❌ Ошибка при сохранении описания в БД: {e}")

sys.stdout.reconfigure(encoding="utf-8")
print("📂 Запуск test.py...")

args = sys.argv
print(f"🧪 Аргументы командной строки: {args}")

# Проверка количества аргументов
if len(args) < 2:
    print("❌ Не передан аргумент: ID или ссылка.")
    sys.exit(1)

# Парсинг аргументов
project_id = None
URL = None

try:
    # Первый аргумент — возможно ID
    arg1 = args[1]
    print(f"🔍 Аргумент #1: {arg1}")

    if arg1.isdigit():
        project_id = int(arg1)
        print(f"📨 Распознан ID: {project_id}")

        # Получаем ссылку из БД
        found = False
        # for db_id, link in get_unprocessed_projects():
        for db_id, link in get_all_projects():
            # print(f"🔎 Проверка: db_id={db_id}, link={link}")
            if db_id == project_id:
                URL = link
                found = True
                print(f"✅ Ссылка найдена: {URL}")
                break

        if not found:
            print(f"❌ Ссылка по ID {project_id} не найдена в БД.")
            sys.exit(1)

        # Если передан второй аргумент — переписываем URL
        if len(args) >= 3:
            override_url = args[2]
            print(f"🔄 Переопределяем ссылку: {override_url}")
            URL = override_url

    else:
        URL = arg1
        print(f"🔗 Распознан аргумент как ссылка: {URL}")

        # Пробуем извлечь ID из ссылки
        try:
            project_id = int(URL.strip("/").split("/")[-1].split(".")[0])
            print(f"📨 Извлечённый ID из ссылки: {project_id}")
        except Exception as e:
            print(f"⚠️ Не удалось извлечь ID из ссылки: {e}")
            project_id = None

except Exception as e:
    print(f"💥 Ошибка при обработке аргументов: {e}")
    sys.exit(1)

if not URL:
    print("❌ Ссылка не определена.")
    sys.exit(1)

print(f"📌 Финальные данные: ID={project_id}, URL={URL}")

# 🧭 Запуск браузера
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

try:
    print("🚀 Запускаем браузер...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print(f"🌐 Открываем URL: {URL}")
    driver.get(URL)

    print("⏳ Ожидаем загрузки описания...")
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-freelancehunt-selector='description']"))
    )

    print("📄 Получаем HTML...")
    html = driver.page_source
    driver.quit()
    print("🛑 Браузер закрыт.")

    soup = BeautifulSoup(html, "html.parser")
    block = soup.find("span", {"data-freelancehunt-selector": "description"})

    if block:
        description = block.get_text(separator="\n", strip=True)
        print(f"📦 Описание извлечено:\n{description}")
        if project_id:
            save_description_to_db(project_id, description)
        else:
            print("⚠️ ID не указан — не сохраняем в БД.")
    else:
        print("❌ Описание не найдено на странице.")

except Exception as e:
    print(f"💣 Ошибка при парсинге: {e}")
    try:
        driver.quit()
        print("🛑 Браузер принудительно закрыт после ошибки.")
    except:
        print("⚠️ Ошибка при закрытии браузера.")
    sys.exit(1)