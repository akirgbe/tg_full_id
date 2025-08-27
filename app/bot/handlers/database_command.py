from aiogram import Router, types
from aiogram.filters import Command

from app.config import settings
from db import db

router = Router()


@router.message(Command("add"))
async def add_user(message: types.Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return await message.answer("❌ Укажите ID: /add <user_id>")

    user_id = int(args[1])

    if user_id == settings.SUPER_ADMIN_ID:
        return await message.answer("🚫 Суперадмин всегда имеет доступ, добавлять не нужно.")

    if db.add_user(user_id):
        await message.answer(f"✅ Пользователь {user_id} добавлен в whitelist")
    else:
        await message.answer(f"⚠️ Пользователь {user_id} уже в whitelist")


@router.message(Command('remove'))
async def remove_user(message: types.Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return await message.answer("❌ Укажите ID: /remove <user_id>")

    user_id = int(args[1])

    # Защита: нельзя удалить самого себя
    if user_id == message.from_user.id:
        return await message.answer("⚠️ Нельзя удалить самого себя!")

    # Защита: суперадмина вообще нельзя удалить
    if user_id == settings.SUPER_ADMIN_ID:
        return await message.answer("🚫 Нельзя удалить суперадмина!")

    if db.remove_user(user_id):
        await message.answer(f"🗑 Пользователь {user_id} удалён")
    else:
        await message.answer(f"⚠️ Пользователь {user_id} не найден")


@router.message(Command("list"))
async def show_whitelist(message: types.Message):
    """Показать всех пользователей в белом списке"""
    users = db.get_all_users()
    if not users:
        await message.answer("📝 Белый список пуст.")
        return

    user_list = "📋 Пользователи в белом списке:\n\n"
    for user in users:
        user_info = f"ID: {user.user_id}"
        if user.username:
            user_info += f" | @{user.username}"
        user_list += f"• {user_info}\n"

    await message.answer(user_list)


@router.message(Command("check"))
async def check_access(message: types.Message):
    """Проверить, есть ли пользователь в белом списке"""
    user_id = message.from_user.id
    if db.is_user_whitelisted(user_id):
        await message.answer("✅ Вы в белом списке!")
    else:
        await message.answer("❌ Вас нет в белом списке.")
