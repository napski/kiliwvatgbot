# KiliwvatgBot MVP

MVP-основа для Telegram-бота магазина цифровых товаров и услуг:

- Telegram Stars
- Аренда NFT
- Аренда виртуальных номеров
- Telegram Premium подписки

Также включены:

- API для админ-панели (тикеты, пользователи, заказы, платежные провайдеры)
- Управление 4 платежками: `Pally`, `Platega`, `CryptoBot`, `FreeKassa`
- Stars-баланс и генерация Stars-чеков
- Базовая аналитика (топ пользователей по Stars и калькулятор прибыли)

## Запуск локально

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Бот отдельно:

```bash
python -m bot.bot
```

## Запуск через Docker (рекомендуется для сервера)

```bash
cp .env.example .env
# обязательно укажите BOT_TOKEN
docker compose up -d --build
```

API будет доступно на `http://<server-ip>:8000`.

## Что реализовано в API

- `POST /users` — создать пользователя
- `PATCH /users/{id}/block` — блокировка пользователя
- `POST /orders` и `GET /orders` — история заказов
- `POST /tickets` и `GET /tickets` — тикет-система
- `GET /payments/providers` и `PATCH /payments/providers/{provider}/toggle` — управление платежками
- `POST /users/{id}/stars/topup` — пополнение Stars-баланса
- `POST /users/{id}/stars/checks` — генерация Stars-чека
- `GET /analytics/top-users` — топ пользователей по Stars
- `GET /analytics/profit-calculator` — расчет прибыли

## Развертывание на свой сервер

1. Установите Docker + Docker Compose.
2. Залейте проект на сервер (`git clone ...`).
3. Создайте `.env` из примера и заполните секреты.
4. Запустите `docker compose up -d --build`.
5. Для reverse proxy используйте Nginx/Caddy и проксируйте на `127.0.0.1:8000`.
6. Для продакшна подключите PostgreSQL/Redis, HTTPS и мониторинг.

## Дальнейшие шаги

- Подключить реальные SDK платежных провайдеров.
- Добавить полноценную Web Admin/UI и Telegram Web App фронтенд.
- Внедрить RBAC, audit logs, rate limiting, алерты.
- Добавить тесты и CI/CD pipeline.
