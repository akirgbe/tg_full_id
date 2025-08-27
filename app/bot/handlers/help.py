from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.kbd import get_persistent_keyboard

router = Router()


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def help_handler(message: Message):
    await message.answer(
        "📖 <b>Справка по боту</b>\n\n"
        "Я показываю ID:\n"
        "✔️ Твой Telegram ID (/id)\n"
        "✔️ ID чата (группы, канала)\n"
        "✔️ ID пользователя или бота\n\n"
        "Как использовать:\n"
        "1. Нажми /id чтобы увидеть свой ID\n"
        "2. Перешли мне сообщение\n"
        "3. Используй кнопки ниже",
        reply_markup=get_persistent_keyboard()
    )
