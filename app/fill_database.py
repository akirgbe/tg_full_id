import os
import sys

from loguru import logger

from db.database import Database

# Добавляем путь к проекту (можно убрать, если используются относительные импорты)
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def clear_and_fill_database():
    """Очистить базу и заполнить новыми пользователями"""
    db = Database()
    logger.info(f"Работаем с базой: {db.db_path}")
    logger.info("=" * 50)

    # Показываем текущих пользователей
    current_users = db.get_all_users()
    logger.info(f"Текущие пользователи в базе ({len(current_users)}):")
    for user in current_users:
        logger.info(f"   👤 ID: {user.user_id} | Username: {user.username or 'N/A'}")

    # Спрашиваем подтверждение на очистку
    if current_users:
        logger.warning("ВНИМАНИЕ: Это удалит всех текущих пользователей!")
        response = input("   Продолжить? (y/N): ")
        if response.lower() != 'y':
            logger.info("Отменено пользователем")
            db.close()
            return
    else:
        logger.info("База пуста, можно заполнять")

    # Очищаем базу
    if current_users:
        logger.info("Очищаем базу...")
        for user in current_users:
            db.remove_user(user.user_id)
        logger.info(f"Удалено {len(current_users)} пользователей")

    # Добавляем новых пользователей
    new_users = [439716429]
    logger.info(f"Добавляем {len(new_users)} новых пользователей:")
    added_count = 0
    for user_id in new_users:
        if db.add_user(user_id):
            logger.info(f"   Добавлен: {user_id}")
            added_count += 1
        else:
            logger.error(f"   Ошибка с: {user_id}")

    # Показываем итог
    final_users = db.get_all_users()
    logger.info("=" * 50)
    logger.info(f"ИТОГ: В базе {len(final_users)} пользователей:")
    for user in final_users:
        logger.info(f"   👤 ID: {user.user_id}")
    db.close()
    logger.info("Заполнение завершено!")


def add_users_without_clear():
    """Добавить пользователей без очистки базы"""
    db = Database()
    logger.info(f"База: {db.db_path}")

    # Показываем текущих пользователей
    current_users = db.get_all_users()
    logger.info(f"Текущие пользователи ({len(current_users)}):")
    for user in current_users:
        logger.info(f"   👤 ID: {user.user_id}")

    # Добавляем новых пользователей
    new_users = [439716429]
    logger.info(f"Добавляем {len(new_users)} пользователей:")
    added_count = 0
    for user_id in new_users:
        if db.add_user(user_id):
            logger.info(f"   Добавлен: {user_id}")
            added_count += 1
        else:
            logger.warning(f"   Уже существует: {user_id}")

    # Итог
    final_users = db.get_all_users()
    logger.info(f"ИТОГ: Всего {len(final_users)} пользователей")
    db.close()


def show_current_users():
    """Просто показать текущих пользователей"""
    db = Database()
    users = db.get_all_users()
    logger.info(f"Пользователи в базе ({len(users)}):")
    if users:
        for i, user in enumerate(users, 1):
            logger.info(f"{i:2d}. ID: {user.user_id} | Username: {user.username or 'N/A'}")
    else:
        logger.info("База пуста")
    db.close()


if __name__ == '__main__':
    while True:
        logger.info("Менеджер базы данных белого списка")
        logger.info("=" * 40)
        logger.info("1. Очистить и заполнить заново")
        logger.info("2. Добавить пользователей (без очистки)")
        logger.info("3. Показать текущих пользователей")
        logger.info("4. Выход")
        choice = input("Выберите действие (1-4): ")
        if choice == '1':
            clear_and_fill_database()
        elif choice == '2':
            add_users_without_clear()
        elif choice == '3':
            show_current_users()
        elif choice == '4':
            logger.info("Выход")
            break
        else:
            logger.error("Неверный выбор")
