import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault

# Добавляем корень проекта в sys.path для корректного импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.bot.handlers import start, help, id, get_shared, any_message, database_command
from app.bot.middlewares.wihite_list import WhitelistMiddleware
from app.config import settings
from db import db


async def set_bot_commands(bot: Bot):
    """Установка команд меню бота"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="id", description="Получить ID"),
        BotCommand(command="add", description="Добавить в белый список"),
        BotCommand(command="remove", description="Удалить из белого списка"),
        BotCommand(command="list", description="Показать белый список"),
        BotCommand(command="check", description="Проверить доступ"),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    print("✅ Команды бота установлены")


async def main():
    # Настройка бота
    bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Устанавливаем команды меню
    await set_bot_commands(bot)

    # Инициализируем мидлварь
    whitelist_middleware = WhitelistMiddleware()
    dp.message.middleware(whitelist_middleware)
    dp.callback_query.middleware(whitelist_middleware)
    dp.edited_message.middleware(whitelist_middleware)

    # Подключаем роутеры
    dp.include_routers(
        database_command.router,  # должен быть первым
        start.router,
        help.router,
        id.router,
        get_shared.router,
        any_message.router
    )

    # ----------------- Логирование при старте -----------------
    print("🚀 Бот успешно запущен")
    print("=" * 50)
    print(f"🤖 BOT_TOKEN: {'*' * 10 + settings.BOT_TOKEN[-5:]}")
    print(f"⭐ SUPER_ADMIN_ID: {settings.SUPER_ADMIN_ID}")

    all_users = db.get_all_users()
    print(f"📋 Пользователей в белом списке: {len(all_users)}")
    if all_users:
        print("   Первые пользователи в базе:")
        for user in all_users[:10]:
            print(f"   👤 {user.user_id} | {user.username or 'N/A'}")
        if len(all_users) > 10:
            print(f"   ... и ещё {len(all_users) - 10} пользователей")

    print(f"⚙️  Parse mode: {ParseMode.HTML}")
    print("=" * 50)

    # Удаляем старый вебхук
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
