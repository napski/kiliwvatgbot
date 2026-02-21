# Telegram Digital Services Shop Bot

MVP-бот магазина цифровых услуг по вашему ТЗ:
- Telegram Stars
- аренда NFT
- виртуальные номера
- Telegram Premium
- система чеков (создание/активация)
- базовая аналитика и лидерборд

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env` переменными `BOT_TOKEN` и `ADMIN_IDS`, затем запустите:

```bash
set -a && source .env && set +a
python -m src.main
```

## Команды бота

- `/start`
- `/catalog`
- `/profile`
- `/topup <amount>`
- `/buy <sku> <qty>`
- `/create_check <amount>`
- `/redeem <code>`
- `/history`
- `/top`
- `/admin_stats` (только для ADMIN_IDS)

## Примечания

- Текущее хранилище in-memory (для production нужно вынести в БД).
- Платежки, WebApp, webhook-подписи и админ-панель можно добавить следующим этапом поверх `ShopService`.
