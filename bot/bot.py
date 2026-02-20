import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from app.config import settings


dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    await message.answer(
        "Привет! Это MVP магазина. API и админ-панель подключаются отдельно."
    )


async def main() -> None:
    if settings.bot_token == "replace_me":
        raise RuntimeError("Set BOT_TOKEN in .env before running the bot")
    bot = Bot(token=settings.bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
