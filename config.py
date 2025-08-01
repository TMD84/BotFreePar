# 🔍 Ключевые слова для фильтрации проектов по теме
# KEYWORDS = ['ексель', 'эксель', 'excel', 'vba']
# KEYWORDS = ['SmartMoney']
KEYWORDS = []

# 🌟 Избранные заказчики, задания которых интересны независимо от содержания
# FAVORITE_CLIENTS = ['Anton_Murat']
FAVORITE_CLIENTS = []

# 🌐 Ссылка на страницу со всеми проектами (будет использоваться для парсинга)
FREELANCEHUNT_URL = 'https://freelancehunt.com/projects'

# 🔐 Путь к файлу .env, где будем хранить конфиденциальные данные (логин, токены)
# ENV_PATH = '.env'

# 🖨️ Отладочный вывод ключевых настроек
print("[CONFIG] Загружены настройки:")
print(f" → Ключевые слова: {KEYWORDS}")
print(f" → Любимые заказчики: {FAVORITE_CLIENTS}")
print(f" → Ссылка для парсинга: {FREELANCEHUNT_URL}")
# print(f" → .env путь: {ENV_PATH}")