from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .config import Config
from .services import BusinessError, ShopService


def _main_menu(config: Config, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Профиль", callback_data="menu:profile")
    builder.button(text="🛍 Каталог", callback_data="menu:catalog")
    builder.button(text="⭐ Пополнить", callback_data="menu:topup")
    builder.button(text="🎟 Чеки", callback_data="menu:checks")
    builder.button(text="📜 История", callback_data="menu:history")
    builder.button(text="🏆 Топ", callback_data="menu:top")
    if user_id in config.admin_ids:
        builder.button(text="🛠 Admin stats", callback_data="menu:admin")
    builder.adjust(2)
    return builder.as_markup()


def _back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:home")]])


def create_dispatcher(service: ShopService, config: Config) -> Dispatcher:
    dp = Dispatcher()

    @dp.message(Command("start", "menu"))
    async def start(message: Message) -> None:
        service.profile(message.from_user.id, message.from_user.username)
        await message.answer("Добро пожаловать! Выберите действие:", reply_markup=_main_menu(config, message.from_user.id))

    @dp.callback_query(F.data == "menu:home")
    async def menu_home(callback: CallbackQuery) -> None:
        await callback.message.edit_text("Главное меню:", reply_markup=_main_menu(config, callback.from_user.id))
        await callback.answer()

    @dp.callback_query(F.data == "menu:profile")
    async def menu_profile(callback: CallbackQuery) -> None:
        u = service.profile(callback.from_user.id, callback.from_user.username)
        await callback.message.edit_text(
            f"Профиль\n"
            f"ID: {u.user_id}\n"
            f"Username: @{u.username or '-'}\n"
            f"Баланс: {u.stars_balance}⭐\n"
            f"Заказов: {u.orders_count}\n"
            f"Сумма покупок: {u.purchases_total}⭐",
            reply_markup=_back_button(),
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu:catalog")
    async def menu_catalog(callback: CallbackQuery) -> None:
        builder = InlineKeyboardBuilder()
        for p in service.store.products.values():
            builder.button(text=f"{p.name} — {p.price_stars}⭐", callback_data=f"buy:{p.sku}:1")
        builder.button(text="⬅️ В меню", callback_data="menu:home")
        builder.adjust(1)
        await callback.message.edit_text("Каталог (нажмите для покупки 1 шт):", reply_markup=builder.as_markup())
        await callback.answer()

    @dp.callback_query(F.data.startswith("buy:"))
    async def buy(callback: CallbackQuery) -> None:
        _, sku, qty_raw = callback.data.split(":", 2)
        qty = int(qty_raw)
        user, product, total = service.buy(callback.from_user.id, callback.from_user.username, sku, qty)
        await callback.message.edit_text(
            f"✅ Оплата успешна\n"
            f"Товар: {product.name}\n"
            f"Списано: {total}⭐\n"
            f"Остаток: {user.stars_balance}⭐",
            reply_markup=_back_button(),
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu:topup")
    async def menu_topup(callback: CallbackQuery) -> None:
        builder = InlineKeyboardBuilder()
        for amount in (100, 300, 500, 1000):
            builder.button(text=f"+{amount}⭐", callback_data=f"topup:{amount}")
        builder.button(text="⬅️ В меню", callback_data="menu:home")
        builder.adjust(2)
        await callback.message.edit_text("Выберите сумму пополнения:", reply_markup=builder.as_markup())
        await callback.answer()

    @dp.callback_query(F.data.startswith("topup:"))
    async def topup(callback: CallbackQuery) -> None:
        amount = int(callback.data.split(":", 1)[1])
        user = service.top_up_stars(callback.from_user.id, callback.from_user.username, amount)
        await callback.message.edit_text(
            f"Баланс пополнен на {amount}⭐\nТекущий баланс: {user.stars_balance}⭐",
            reply_markup=_back_button(),
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu:checks")
    async def menu_checks(callback: CallbackQuery) -> None:
        builder = InlineKeyboardBuilder()
        for amount in (100, 250, 500):
            builder.button(text=f"Создать чек {amount}⭐", callback_data=f"check:create:{amount}")

        available = [c for c in service.store.checks.values() if not c.is_activated and c.owner_user_id != callback.from_user.id]
        for check in available[:5]:
            builder.button(text=f"Активировать {check.code} ({check.amount}⭐)", callback_data=f"check:redeem:{check.code}")

        builder.button(text="⬅️ В меню", callback_data="menu:home")
        builder.adjust(1)
        await callback.message.edit_text("Раздел чеков:", reply_markup=builder.as_markup())
        await callback.answer()

    @dp.callback_query(F.data.startswith("check:create:"))
    async def check_create(callback: CallbackQuery) -> None:
        amount = int(callback.data.split(":", 2)[2])
        check = service.create_check(callback.from_user.id, callback.from_user.username, amount)
        await callback.message.edit_text(
            f"Чек создан: {check.code}\nСумма: {check.amount}⭐",
            reply_markup=_back_button(),
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("check:redeem:"))
    async def check_redeem(callback: CallbackQuery) -> None:
        code = callback.data.split(":", 2)[2]
        check = service.redeem_check(callback.from_user.id, callback.from_user.username, code)
        await callback.message.edit_text(
            f"Чек {check.code} активирован\nНачислено: {check.amount}⭐",
            reply_markup=_back_button(),
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu:history")
    async def menu_history(callback: CallbackQuery) -> None:
        user = service.profile(callback.from_user.id, callback.from_user.username)
        if not user.operations:
            text = "История операций пуста"
        else:
            lines = ["Последние операции:"]
            for op in user.operations[-10:]:
                lines.append(f"- {op.at:%Y-%m-%d %H:%M} | {op.op_type} | {op.amount}⭐ | {op.reason}")
            text = "\n".join(lines)
        await callback.message.edit_text(text, reply_markup=_back_button())
        await callback.answer()

    @dp.callback_query(F.data == "menu:top")
    async def menu_top(callback: CallbackQuery) -> None:
        leaders = service.leaderboard()
        if not leaders:
            text = "Нет данных для рейтинга."
        else:
            lines = ["Топ пользователей:"]
            for idx, user in enumerate(leaders, start=1):
                lines.append(f"{idx}. ID {user.user_id} (@{user.username or '-'}) — {user.purchases_total}⭐")
            text = "\n".join(lines)
        await callback.message.edit_text(text, reply_markup=_back_button())
        await callback.answer()

    @dp.callback_query(F.data == "menu:admin")
    async def menu_admin(callback: CallbackQuery) -> None:
        if callback.from_user.id not in config.admin_ids:
            await callback.answer("Недостаточно прав", show_alert=True)
            return
        total_revenue = sum(u.purchases_total for u in service.store.users.values())
        total_users = len(service.store.users)
        total_checks = len(service.store.checks)
        activated = sum(1 for c in service.store.checks.values() if c.is_activated)
        await callback.message.edit_text(
            f"Admin stats\n"
            f"Пользователей: {total_users}\n"
            f"Оборот: {total_revenue}⭐\n"
            f"Чеков: {total_checks} (активировано {activated})",
            reply_markup=_back_button(),
        )
        await callback.answer()

    @dp.errors()
    async def err_handler(event) -> bool:
        if isinstance(event.exception, BusinessError):
            if event.update.callback_query:
                await event.update.callback_query.answer(f"Ошибка: {event.exception}", show_alert=True)
            elif event.update.message:
                await event.update.message.answer(f"Ошибка: {event.exception}")
            return True
        logging.exception("Unhandled error", exc_info=event.exception)
        return False

    return dp


async def run_bot() -> None:
    logging.basicConfig(level=logging.INFO)
    config = Config()
    config.validate()

    from .store import InMemoryStore

    store = InMemoryStore()
    service = ShopService(store)
    service.seed_catalog()

    bot = Bot(token=config.bot_token)
    dp = create_dispatcher(service, config)
    await dp.start_polling(bot)
