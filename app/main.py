import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault

# Добавляем корень проекта в sys.path для корректного импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.bot.handlers import start, help, id, get_shared, any_message, database_command, find
from app.bot.middlewares.white_list import WhitelistMiddleware
from app.config import settings
from db import db

from loguru import logger

# Удаляем все существующие обработчики перед добавлением
logger.remove()

# Также выводим логи в консоль с цветами
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
    colorize=True
)


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
        BotCommand(command="find_phone", description="Найти по номеру телефона"),
        BotCommand(command="list_persons", description="Показать список людей"),
        BotCommand(command="list_accounts", description="Показать список аккаунтов"),
        BotCommand(command="add_person", description="Добавить человека"),
        BotCommand(command="add_account", description="Добавить аккаунт"),
        BotCommand(command="delete_person", description="Удалить человека"),
        BotCommand(command="delete_account", description="Удалить аккаунт"),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    logger.success("Команды бота установлены")


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
        find.router,
        any_message.router
    )

    # ----------------- Логирование при старте -----------------
    logger.info("🚀 Бот успешно запущен")
    logger.info("=" * 50)
    logger.info(f"🤖 BOT_TOKEN: {'*' * 10 + settings.BOT_TOKEN[-5:]}")
    logger.info(f"⭐ SUPER_ADMIN_ID: {settings.SUPER_ADMIN_ID}")

    all_users = db.get_all_users()
    logger.info(f"📋 Пользователей в белом списке: {len(all_users)}")

    if all_users:
        logger.info("Первые пользователи в базе:")
        for user in all_users[:10]:
            username_display = user.username or 'N/A'
            logger.info(f"   👤 {user.user_id} | {username_display}")
        if len(all_users) > 10:
            logger.info(f"   ... и ещё {len(all_users) - 10} пользователей")

    logger.info(f"⚙️  Parse mode: {ParseMode.HTML}")
    logger.info("=" * 50)

    # Удаляем старый вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    logger.debug("Старый вебхук удален")

    try:
        logger.info("Начинаем поллинг...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
        raise
    finally:
        await bot.session.close()
        logger.info("Сессия бота закрыта")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
