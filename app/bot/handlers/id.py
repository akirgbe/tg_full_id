from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.kbd import get_persistent_keyboard

router = Router()


@router.message(Command("id"))
@router.message(F.text == "🆔 Мой ID")
async def id_command(message: Message):
    await message.answer(
        f"👤 <b>Ваш ID:</b> <code>{message.from_user.id}</code>\n"
        f"💬 <b>Текущий чат:</b> <code>{message.chat.id}</code>\n"
        f"Тип: {message.chat.type}",
        reply_markup=get_persistent_keyboard()
    )
