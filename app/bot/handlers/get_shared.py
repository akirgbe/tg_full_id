from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import Message

from app.bot.keyboards.kbd import get_persistent_keyboard

router = Router()


@router.message(F.chat_shared)
async def handle_chat_shared(message: Message):
    chat_id = message.chat_shared.chat_id
    request_id = message.chat_shared.request_id

    if request_id == 1:  # Канал
        await message.answer(
            f"✅ Выбран канал с ID: <code>{chat_id}</code>",
            reply_markup=get_persistent_keyboard()
        )
    elif request_id == 2:  # Группа/супергруппа
        await message.answer(
            f"✅ Выбрана группа с ID: <code>{chat_id}</code>",
            reply_markup=get_persistent_keyboard()
        )


@router.message(F.user_shared)
async def handle_user_shared(message: Message):
    user_id = message.user_shared.user_id
    request_id = message.user_shared.request_id

    if request_id == 3:  # Пользователь
        await message.answer(
            f"✅ Выбран пользователь с ID: <code>{user_id}</code>",
            reply_markup=get_persistent_keyboard()
        )
    elif request_id == 4:  # Бот
        await message.answer(
            f"✅ Выбран бот с ID: <code>{user_id}</code>",
            reply_markup=get_persistent_keyboard()
        )


@router.message(F.forward_from | F.forward_from_chat | F.forward_origin)
async def handle_forwarded(message: Message):
    if message.forward_from:
        await message.answer(
            f"🔁 <b>Переслано от пользователя:</b>\n"
            f"ID: <code>{message.forward_from.id}</code>\n"
            f"Имя: {message.forward_from.full_name}\n"
            f"Username: @{message.forward_from.username or '—'}\n"
            f"Бот: {'Да' if message.forward_from.is_bot else 'Нет'}",
            reply_markup=get_persistent_keyboard()
        )
    elif message.forward_from_chat:
        chat = message.forward_from_chat
        chat_type = "канала" if chat.type == ChatType.CHANNEL else "группы"
        await message.answer(
            f"🔁 <b>Переслано из {chat_type}:</b>\n"
            f"ID: <code>{chat.id}</code>\n"
            f"Тип: <code>{chat.type}</code>\n"
            f"Название: {chat.title or 'Нет данных'}\n"
            f"Username: @{chat.username or 'Нет данных'}",
            reply_markup=get_persistent_keyboard()
        )
    elif message.forward_origin:
        origin = message.forward_origin
        if origin.type == "user":
            await message.answer(
                f"🔁 <b>Переслано от пользователя:</b>\n"
                f"ID: <code>{origin.sender_user.id}</code>\n"
                f"Имя: {origin.sender_user.full_name}\n"
                f"Username: @{origin.sender_user.username or 'Нет данных'}",
                reply_markup=get_persistent_keyboard()
            )
        elif origin.type == "chat":
            chat_type = "канала" if origin.sender_chat.type == ChatType.CHANNEL else "группы"
            await message.answer(
                f"🔁 <b>Переслано из {chat_type}:</b>\n"
                f"ID: <code>{origin.sender_chat.id}</code>\n"
                f"Тип: <code>{origin.sender_chat.type}</code>\n"
                f"Название: {origin.sender_chat.title or 'Нет данных'}",
                reply_markup=get_persistent_keyboard()
            )
        elif origin.type == "hidden_user":
            await message.answer(
                f"🔁 <b>Переслано от скрытого пользователя:</b> {origin.sender_user_name}",
                reply_markup=get_persistent_keyboard()
            )
