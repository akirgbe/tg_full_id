from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.kbd import get_persistent_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"👋 Привет, <b>{message.from_user.full_name}</b>!\n"
        f"Я бот для отображения Telegram ID.\n\n"
        f"📌 Используй команды:\n"
        f"/id - показать твой ID и ID текущего чата\n"
        f"/help - справка по боту\n\n"
        f"Можешь переслать сообщение и получить информацию\n"
        f"Или выбери, что показать через встроенную клавиатуру",
        reply_markup=get_persistent_keyboard()
    )
