from aiogram import Router
from aiogram.types import Message

from app.bot.keyboards.kbd import get_persistent_keyboard

router = Router()


@router.message()
async def other_messages(message: Message):
    if message.text and not message.text.startswith('/'):
        await message.answer(
            "ℹ️ Для получения ID используйте:\n"
            "• Команду /id\n"
            "• Перешлите сообщение\n"
            "• Выберите варианты через кнопки ниже",
            reply_markup=get_persistent_keyboard()
        )
