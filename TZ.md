# ТЗ / Техническая Спецификация: Manager TG (MVP)

Дата актуализации: 2026-02-09

Цель документа: зафиксировать, что это за проект, как он устроен, какие фичи считаются “сделанными”, и какие договоренности/ограничения действуют. Документ написан так, чтобы по нему можно было быстро восстановить контекст после длительного перерыва.

## 1. Описание продукта
Manager TG это MVP веб-приложения для управления несколькими Telegram-каналами:
- создание/редактирование постов
- согласование (approval workflow)
- планирование публикаций и авто-публикация по расписанию
- базовая статистика (просмотры, если доступно)
- прием “предложений” (suggestions) извне (например из n8n) и превращение их в посты

## 2. Роли и права (RBAC)
Роли: `admin`, `author`, `editor`, `viewer`.

Текущая модель доступа на API (как должно работать):
- Любой авторизованный пользователь может читать данные (каналы/посты/настройки/статы), если не указано иначе.
- `admin`:
  - создание пользователей (`POST /v1/users/`)
  - создание/удаление каналов (`POST /v1/channels`, `DELETE /v1/channels/{id}`)
  - удаление постов (`DELETE /v1/posts/{id}`)
- `author|editor|admin`:
  - создание постов, редактирование постов, отправка на согласование
    - `POST /v1/channels/{channel_id}/posts`
    - `PUT /v1/posts/{post_id}`
    - `POST /v1/posts/{post_id}/submit-approval`
- `editor|admin`:
  - approve/reject/schedule/publish-now, а также accept/reject suggestions

Примечание: если понадобятся более жесткие ограничения (например “author может редактировать только свои посты”), это должно быть отдельно уточнено и добавлено на уровне usecase/repo.

## 3. Основные пользовательские сценарии
### 3.1 Логин
1. Пользователь логинится по email/паролю.
2. Frontend сохраняет `access_token` и передает его как `Authorization: Bearer <token>`.

### 3.2 Управление каналами
1. Админ создает канал.
2. Пользователи видят список каналов и могут работать с постами в канале.
3. Дополнительно есть `/v1/channels/lookup?identifier=...` для поиска/проверки.

### 3.3 Жизненный цикл поста (workflow)
Статусы: Draft → Pending approval → Approved → Scheduled → Published.
Также: Pending approval → Rejected → Draft (после правок).

Ожидаемая логика:
- `author` создает/редактирует пост в draft
- `author` отправляет на согласование
- `editor` approve/reject
- `editor` может запланировать публикацию или опубликовать сразу

### 3.4 Автопубликация по расписанию
1. Celery beat запускает задачу публикации раз в минуту.
2. Worker выбирает “scheduled” посты с `scheduled_at <= now` и пытается опубликовать.

### 3.5 Suggestions (интеграция с n8n)
1. Внешняя система отправляет suggestion на
   - `POST /v1/channels/{channel_id}/suggestions`
   - с заголовком `X-API-Key: <N8N_API_KEY>`
2. В UI пользователь (editor/admin) может принять предложение (создается пост) или отклонить.

### 3.6 Media upload
1. Авторизованный пользователь загружает картинку на `/v1/media/upload` (multipart).
2. Backend конвертирует в JPEG, делает preview, сохраняет в `MEDIA_DIR`, отдает URL-ы:
   - `/media/<uuid>.jpg`
   - `/media/previews/<uuid>.jpg`

### 3.7 Комментарии к постам (обсуждение/ревью)
1. Любой авторизованный пользователь может читать комментарии к посту и оставлять комментарии.
2. При отклонении поста редактором (`reject`) причина сохраняется как `editor_comment` и дополнительно записывается в ленту комментариев (kind=`reject`).

## 4. Архитектура
### 4.1 Backend
- FastAPI
- SQLAlchemy 2.x + Alembic
- PostgreSQL
- Redis (broker/result backend для Celery; также rate limiting)
- Celery worker + Celery beat

Ключевые модули:
- API роутер: `backend/app/api/router.py` (`/v1/*`)
- Auth/RBAC deps: `backend/app/api/deps.py`
- Настройки: `backend/app/core/config.py`
- JWT/пароли: `backend/app/core/security.py`
- Use-cases: `backend/app/usecases/*`
- Repositories (DB операции): `backend/app/repositories/*`
- Celery: `backend/app/workers/*`

### 4.2 Frontend
- React + Vite
- Взаимодействие с API через `/v1/*`
- Токен хранится в `localStorage` (`frontend/src/state/tokenStorage.js`).

## 5. API (высокоуровнево)
Префикс: `/v1`

Auth:
- `POST /v1/auth/login` → `{access_token}`

Users:
- `GET /v1/users/me`
- `POST /v1/users/` (admin)
- `GET /v1/users` (admin)
- `PATCH /v1/users/{user_id}/role` (admin)
- `PATCH /v1/users/{user_id}/password` (admin)
- `PATCH /v1/users/{user_id}/active` (admin)
- `POST /v1/users/{user_id}/reset-password` (admin)

Channels:
- `GET /v1/channels`
- `GET /v1/channels/lookup?identifier=...`
- `POST /v1/channels` (admin)
- `GET /v1/channels/{id}`
- `DELETE /v1/channels/{id}` (admin)

Agent settings:
- `GET /v1/channels/{channel_id}/agent-settings` (auth)
- `PUT /v1/channels/{channel_id}/agent-settings` (editor/admin)

Posts:
- `POST /v1/channels/{channel_id}/posts` (author/editor/admin)
- `GET /v1/channels/{channel_id}/posts`
- `GET /v1/posts/{post_id}`
- `PUT /v1/posts/{post_id}` (author/editor/admin)
- `POST /v1/posts/{post_id}/submit-approval` (author/editor/admin)
- `POST /v1/posts/{post_id}/approve` (editor/admin)
- `POST /v1/posts/{post_id}/reject` (editor/admin)
- `POST /v1/posts/{post_id}/schedule` (editor/admin)
- `POST /v1/posts/{post_id}/publish-now` (editor/admin)
- `DELETE /v1/posts/{post_id}` (admin)

Comments:
- `GET /v1/posts/{post_id}/comments` (auth)
- `POST /v1/posts/{post_id}/comments` (auth)

Suggestions:
- `POST /v1/channels/{channel_id}/suggestions` (X-API-Key)
- `GET /v1/channels/{channel_id}/suggestions` (auth)
- `POST /v1/channels/{channel_id}/suggestions/{id}/accept` (editor/admin)
- `DELETE /v1/channels/{channel_id}/suggestions/{id}` (editor/admin)

Inbox:
- `GET /v1/inbox/suggestions` (editor/admin)

Schedule:
- `GET /v1/schedule` (auth)
- `POST /v1/schedule/posts/{post_id}/requeue` (editor/admin)

Media:
- `POST /v1/media/upload` (auth)
- Static: `/media/*`

Stats:
- `GET /v1/channels/{channel_id}/stats` (auth)

Dashboard:
- `GET /v1/dashboard/overview` (auth)

Audit:
- `GET /v1/audit-logs` (admin)
- `GET /v1/audit-logs/{audit_id}` (admin)

Telegram:
- `POST /v1/telegram/webhook` (опционально защищен `TELEGRAM_WEBHOOK_SECRET`)

## 6. Конфигурация (env)
Главные переменные (см. `.env.example`):
- `APP_ENV`: `development|production|test`
- `APP_SECRET`: секрет подписи JWT (в production обязателен)
- `DATABASE_URL`
- `ADMIN_EMAIL`, `ADMIN_PASSWORD` (для `python -m app.scripts.create_admin`)
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_FEATURE_VIEWS`, `TELEGRAM_WEBHOOK_SECRET`
- `N8N_API_KEY`
- `RATE_LIMIT_ENABLED`, `RATE_LIMIT_REDIS_URL` (опционально)
- `METRICS_ENABLED`
- `METRICS_TOKEN` (если задан в production, доступ к `/metrics` только с `X-Metrics-Token`)
- `DOCS_ENABLED` (по умолчанию: true вне production, false в production)
- `MEDIA_DIR`, `MEDIA_MAX_BYTES`, `MEDIA_MAX_PIXELS`

## 7. Наблюдаемость и безопасность
- Логи JSON: `backend/app/core/logging.py`
- Middleware добавляет `X-Request-ID` и логирует время ответа: `backend/app/main.py`
- `/health` всегда доступен
- `/metrics`:
  - выключается `METRICS_ENABLED=false`
  - в production скрыт, пока не задан `METRICS_TOKEN` (и не передан как `X-Metrics-Token`)
- Rate limiting:
  - best-effort: если Redis/инициализация fastapi-limiter недоступны, API продолжает работать без лимитов (без 500)
  - реализация: `backend/app/api/rate_limit.py`

## 8. Запуск и деплой
Dev (локально):
- `docker-compose up --build`
- миграции: `docker-compose exec backend alembic upgrade head`
- админ: `docker-compose exec backend python -m app.scripts.create_admin`

Prod:
- `docker-compose.prod.yml` (Caddy, HTTPS)
- `docker-compose.nginx.prod.yml` (если есть host Nginx; сервисы слушают только `127.0.0.1`)
Подробности: `DEPLOY.md`

## 9. Текущее состояние и ключевые договоренности
- Backend и Frontend запускаются и взаимодействуют через `/v1/*`.
- JWT токен хранится на фронте в `localStorage` и передается как Bearer.
- Celery beat/worker публикуют scheduled посты.
- Suggestions принимаются по API key и дедуплицируются по `source_hash`.
- Принцип деградации rate limiting: лучше “без лимита”, чем “500 на логин”.

## 10. Что считать “готово” для MVP
- Возможность создать канал (admin), создать пост (author), отправить на согласование, одобрить (editor), запланировать, и увидеть что Celery публикует.
- Возможность загрузить media и прикрепить к посту.
- Возможность принять suggestion извне и превратить в пост.
- Минимальная статистика по просмотрам (если `TELEGRAM_FEATURE_VIEWS=true` и Telegram дает данные).
