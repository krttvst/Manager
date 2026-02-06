# Manager TG (MVP)

MVP веб‑приложения для управления несколькими Telegram‑каналами: генерация постов, согласование, планирование публикаций и базовая статистика.

## Стек
- Backend: FastAPI + SQLAlchemy + Alembic
- DB: PostgreSQL
- Queue/Scheduler: Celery + Redis
- Frontend: React + Vite

## Быстрый старт
1) Скопируйте `.env.example` в `.env` и заполните секреты:
```bash
cp .env.example .env
```
Обязательно задайте `ADMIN_PASSWORD` и `TELEGRAM_BOT_TOKEN` в `.env`.
2) Запуск через Docker:
```bash
docker-compose up --build
```
3) Примените миграции (в отдельном окне):
```bash
docker-compose exec backend alembic upgrade head
```
4) Создайте администратора:
```bash
docker-compose exec backend python -m app.scripts.create_admin
```
5) Backend будет доступен на `http://localhost:8000` (документация OpenAPI: `/docs`).
6) Frontend будет доступен на `http://localhost:5173`.

## Telegram
- Создайте бота через @BotFather и получите `TELEGRAM_BOT_TOKEN`.
- Добавьте бота в канал и дайте права на публикацию.
- Укажите `telegram_channel_identifier` в канале (например `@my_channel`).

## Метрики
MVP предусматривает graceful degradation: при недоступности просмотров через Bot API метрики будут показываться как недоступные. Флаг: `TELEGRAM_FEATURE_VIEWS`.

## N8N / Предложения
Для загрузки предложений из n8n используйте API key и эндпоинт:
- `POST /v1/channels/{channel_id}/suggestions`
- Заголовок: `X-API-Key: <N8N_API_KEY>`

## AI генерация (MVP)
Сейчас используется упрощённая генерация: парсинг текста по URL и короткое резюме. Интеграцию с LLM можно добавить позже через `OPENAI_API_KEY`.

## Роли
- admin, author, editor, viewer

## Статусы постов
Draft → Pending approval → Approved → Scheduled → Published
Pending approval → Rejected → Draft (после правок)

## План разработки
См. `docs/` (будет добавлено).
