import os
import sys

# Добавляем путь к проекту
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from db.database import Database


def clear_and_fill_database():
    """Очистить базу и заполнить новыми пользователями"""
    db = Database()

    print(f"📁 Работаем с базой: {db.db_path}")
    print("=" * 50)

    # 1. Показываем текущих пользователей
    current_users = db.get_all_users()
    print(f"📋 Текущие пользователи в базе ({len(current_users)}):")
    for user in current_users:
        print(f"   👤 ID: {user.user_id} | Username: {user.username or 'N/A'}")

    # 2. Спрашиваем подтверждение на очистку
    if current_users:
        print("\n⚠️  ВНИМАНИЕ: Это удалит всех текущих пользователей!")
        response = input("   Продолжить? (y/N): ")
        if response.lower() != 'y':
            print("❌ Отменено пользователем")
            db.close()
            return
    else:
        print("✅ База пуста, можно заполнять")

    # 3. Очищаем базу (удаляем всех пользователей)
    if current_users:
        print("\n🧹 Очищаем базу...")
        for user in current_users:
            db.remove_user(user.user_id)
        print(f"✅ Удалено {len(current_users)} пользователей")

    # 4. Добавляем новых пользователей
    new_users = [
        439716429,
    ]

    print(f"\n📥 Добавляем {len(new_users)} новых пользователей:")
    added_count = 0
    for user_id in new_users:
        if db.add_user(user_id):
            print(f"   ✅ Добавлен: {user_id}")
            added_count += 1
        else:
            print(f"   ❌ Ошибка с: {user_id}")

    # 5. Показываем итог
    final_users = db.get_all_users()
    print("\n" + "=" * 50)
    print(f"🎉 ИТОГ: В базе {len(final_users)} пользователей:")
    for user in final_users:
        print(f"   👤 ID: {user.user_id}")

    db.close()
    print("\n✅ Заполнение завершено!")


def add_users_without_clear():
    """Добавить пользователей без очистки базы"""
    db = Database()

    print(f"📁 База: {db.db_path}")

    # Показываем текущих пользователей
    current_users = db.get_all_users()
    print(f"📋 Текущие пользователи ({len(current_users)}):")
    for user in current_users:
        print(f"   👤 ID: {user.user_id}")

    # Добавляем новых пользователей
    new_users = [
        439716429,  # ЗАМЕНИТЕ НА РЕАЛЬНЫЕ ID
    ]

    print(f"\n📥 Добавляем {len(new_users)} пользователей:")
    added_count = 0
    for user_id in new_users:
        if db.add_user(user_id):
            print(f"   ✅ Добавлен: {user_id}")
            added_count += 1
        else:
            print(f"   ⚠️  Уже существует: {user_id}")

    # Итог
    final_users = db.get_all_users()
    print(f"\n🎉 ИТОГ: Всего {len(final_users)} пользователей")
    db.close()


def show_current_users():
    """Просто показать текущих пользователей"""
    db = Database()

    users = db.get_all_users()
    print(f"📋 Пользователи в базе ({len(users)}):")

    if users:
        for i, user in enumerate(users, 1):
            print(f"{i:2d}. ID: {user.user_id} | Username: {user.username or 'N/A'}")
    else:
        print("📭 База пуста")

    db.close()


if __name__ == '__main__':
    while True:
        print("🤖 Менеджер базы данных белого списка")
        print("=" * 40)
        print("1. Очистить и заполнить заново")
        print("2. Добавить пользователей (без очистки)")
        print("3. Показать текущих пользователей")
        print("4. Выход")

        choice = input("\nВыберите действие (1-4): ")

        if choice == '1':
            clear_and_fill_database()
        elif choice == '2':
            add_users_without_clear()
        elif choice == '3':
            show_current_users()
        elif choice == '4':
            print("👋 Выход")
            break
        else:
            print("❌ Неверный выбор")
