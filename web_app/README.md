# LLM Attack Analysis System - Web Application

Веб-інтерфейс для системи аналізу атак з використанням LLM моделей.

## 🚀 Швидкий старт

### 1. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 2. Налаштування змінних середовища

Створіть файл `.env` в кореневій папці проекту:

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SECRET_KEY=your_secret_key_here
```

### 3. Запуск додатку

```bash
# Запуск в продакшн режимі
python run_web_app.py

# Запуск в режимі налагодження
python run_web_app.py --debug

# Запуск на конкретному порті
python run_web_app.py --port 8080
```

### 4. Відкриття в браузері

Перейдіть на `http://localhost:5000`

## 🌐 Структура веб-додатку

```
web_app/
├── app.py                 # Основний Flask додаток
├── run_web_app.py        # Скрипт запуску
├── requirements.txt       # Залежності Python
├── templates/            # HTML шаблони
│   ├── base.html        # Базовий шаблон
│   ├── index.html       # Головна сторінка
│   ├── dashboard.html   # Панель керування
│   ├── attack.html      # Генерація атак
│   ├── defense.html     # Аналіз захисту
│   ├── simulation.html  # Симуляція атак
│   ├── network.html     # Аналіз мережі
│   └── logs.html        # Логи системи
├── static/              # Статичні файли
│   ├── css/            # Стилі
│   ├── js/             # JavaScript
│   └── images/         # Зображення
└── logs/               # Логи веб-додатку
```

## 🔧 API Endpoints

### Основні сторінки

- `GET /` - Головна сторінка
- `GET /dashboard` - Панель керування
- `GET /attack` - Генерація атак
- `GET /defense` - Аналіз захисту
- `GET /simulation` - Симуляція атак
- `GET /network` - Аналіз мережі
- `GET /logs` - Логи системи

### API Endpoints

- `POST /api/generate_attack` - Генерація атаки
- `POST /api/analyze_defense` - Аналіз захисту
- `POST /api/start_simulation` - Запуск симуляції
- `POST /api/stop_simulation` - Зупинка симуляції
- `GET /api/simulation_status/<id>` - Статус симуляції
- `GET /api/simulation_summary/<id>` - Зведення симуляції
- `GET /api/system_statistics` - Статистика системи
- `GET /health` - Перевірка здоров'я

### WebSocket Events

- `connect` - Підключення
- `disconnect` - Відключення
- `simulation_update` - Оновлення симуляції
- `request_simulation_update` - Запит на оновлення

## 🎨 UI Компоненти

### Базовий шаблон (`base.html`)

- Навігаційна панель
- Бічна панель з меню
- Контейнер для сповіщень
- Підвал

### Стилі

- Bootstrap 5
- Кастомні CSS змінні
- Адаптивний дизайн
- Анімації та переходи

### JavaScript функціональність

- Socket.IO з'єднання
- AJAX запити до API
- Динамічне оновлення контенту
- Обробка форм

## 🛡️ Безпека

### Аутентифікація

- Секретний ключ Flask
- Валідація вхідних даних
- Захист від CSRF атак

### API Безпека

- Валідація JSON
- Обмеження розміру запитів
- Логування всіх запитів

### Веб-безпека

- HTTPS (в продакшні)
- Безпечні заголовки
- Захист від XSS

## 📊 Моніторинг

### Логування

- Структуровані логи
- Різні рівні важливості
- Ротація логів

### Метрики

- Час відповіді API
- Кількість запитів
- Помилки та винятки

### Здоров'я системи

- Перевірка компонентів
- Статус LLM провайдерів
- Доступність сервісів

## 🧪 Тестування

### Unit тести

```bash
python -m pytest tests/test_web_app.py -v
```

### Інтеграційні тести

```bash
python -m pytest tests/test_integration.py -v
```

### Тести безпеки

```bash
python -m pytest tests/test_security.py -v
```

### Покриття коду

```bash
python -m pytest --cov=web_app --cov-report=html
```

## 🚀 Розгортання

### Розробка

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Продакшн

```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (планується)

```bash
docker build -t llm-attack-system .
docker run -p 5000:5000 llm-attack-system
```

## 🔧 Налаштування

### Конфігурація Flask

```python
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('DEBUG', 'false').lower() == 'true'
```

### Налаштування Socket.IO

```python
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading'
)
```

### Налаштування логування

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 📝 Логування

### Рівні логування

- `DEBUG` - Детальна інформація для розробки
- `INFO` - Загальна інформація
- `WARNING` - Попередження
- `ERROR` - Помилки
- `CRITICAL` - Критичні помилки

### Типи подій

- API запити
- WebSocket з'єднання
- Помилки та винятки
- Дії користувачів

## 🐛 Відлагодження

### Режим налагодження

```bash
python run_web_app.py --debug
```

### Логи в реальному часі

```bash
tail -f logs/web_app.log
```

### Профілювання

```bash
python -m cProfile -o profile.prof app.py
```

## 📚 Документація

### API Документація

- Swagger/OpenAPI (планується)
- Postman колекції
- Приклади запитів

### Користувацька документація

- Інструкції користувача
- Відео туториали
- FAQ

### Розробницька документація

- Архітектура системи
- API референс
- Приклади коду

## 🤝 Внесок

### Як внести свій внесок

1. Форкніть репозиторій
2. Створіть гілку для нової функції
3. Внесіть зміни
4. Додайте тести
5. Створіть Pull Request

### Стандарти коду

- Python: PEP 8, type hints
- JavaScript: ES6+, JSDoc
- HTML: HTML5, семантична розмітка
- CSS: CSS3, BEM методологія

## 📄 Ліцензія

Цей проект розповсюджується під ліцензією MIT.

## 📞 Підтримка

- **GitHub Issues**: [Створити issue](https://github.com/username/repo/issues)
- **Email**: support@example.com
- **Документація**: [Wiki](https://github.com/username/repo/wiki)

---

**© 2024 LLM Attack Analysis System. Всі права захищено.**
