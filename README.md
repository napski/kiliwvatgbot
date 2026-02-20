# KiliwvatgBot

Базовая реализация ТЗ: backend для Telegram-магазина, админ-панели, Stars-чеков и аналитики.

## Что реализовано

- API магазина: заказы (Stars, NFT аренда, виртуальные номера, Telegram Premium), тикеты.
- API админ-панели: пользователи, блокировка/разблокировка, включение/отключение платежек.
- Платежные провайдеры: Pally, Platega, CryptoBot, FreeKassa (как переключаемые провайдеры).
- Stars система: внутренний баланс пользователя + генерация Stars-чеков.
- Аналитика: топ пользователей по Stars-покупкам, расчет прибыли.
- Telegram bot scaffold на `aiogram`.

## Быстрый запуск (локально)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

## Запуск через Docker

```bash
docker compose up -d
```

## Веб-эндпоинты

- `GET /` — health/info
- `POST /admin/users`
- `GET /admin/users`
- `POST /admin/users/{id}/block`
- `POST /admin/users/{id}/unblock`
- `PUT /admin/payments/{provider}`
- `POST /store/orders`
- `GET /store/orders`
- `POST /store/tickets`
- `GET /store/tickets`
- `POST /stars/checks`
- `GET /analytics/stars-top`
- `GET /analytics/profit`

## Импорт на ваш сервер (пошагово)

### 1) Подготовьте сервер

Для Ubuntu/Debian можно использовать готовый bootstrap:

```bash
scp scripts/remote_bootstrap.sh user@server:/tmp/remote_bootstrap.sh
ssh user@server 'bash /tmp/remote_bootstrap.sh'
```

### 2) Загрузите проект

Минимально:

```bash
./scripts/import_to_server.sh user@server /opt/kiliwvatgbot
```

С загрузкой конкретного env-файла сразу на сервер:

```bash
./scripts/import_to_server.sh user@server /opt/kiliwvatgbot --env-file .env
```

### 3) Запустите контейнеры на сервере

```bash
ssh user@server
cd /opt/kiliwvatgbot
cp -n .env.example .env
# заполнить TELEGRAM_BOT_TOKEN и при необходимости DATABASE_URL
sudo docker compose up -d --build
sudo docker compose ps
```

### 4) Проверка после запуска

```bash
curl http://SERVER_IP:8000/
```

Должен вернуться JSON с полем `features`.

---

Если хотите, следующим шагом могу добавить:
- полноценную web admin UI
- Telegram Web App (frontend)
- реальные SDK интеграции с Pally/Platega/CryptoBot/FreeKassa
- Alembic миграции, RBAC, JWT auth, CI/CD.
