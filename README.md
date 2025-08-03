# FinancePlanner

FinancePlanner — це веб-додаток для планування та аналізу особистих фінансів.

## Основні можливості
- Ведення доходів та витрат
- Категоризація транзакцій
- Статистика та графіки
- Аутентифікація користувачів
- Управління категоріями

## Технології
- Python, FastAPI
- SQLAlchemy, Alembic
- PostgreSQL
- Jinja2
- JavaScript (frontend)

## Запуск проекту
1. Створіть та активуйте віртуальне середовище:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # або .venv\Scripts\activate для Windows
   ```
2. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустіть сервер:
   ```bash
   uvicorn app.main:app --reload
   ```

## Міграції бази даних
```bash
alembic upgrade head
```

## Структура проекту
- `app/` — основний код бекенду
- `app/static/` — статичні файли (JS, CSS)
- `app/templates/` — HTML-шаблони
- `alembic/` — міграції

## Ліцензія
MIT
