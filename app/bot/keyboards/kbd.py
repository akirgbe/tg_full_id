from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestChat, KeyboardButtonRequestUser


def get_persistent_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📢 Получить ID канала", request_chat=KeyboardButtonRequestChat(
                    request_id=1, chat_is_channel=True)),
                KeyboardButton(text="👥 Получить ID группы", request_chat=KeyboardButtonRequestChat(
                    request_id=2, chat_is_channel=False))
            ],
            [
                KeyboardButton(text="👤 Получить ID пользователя", request_user=KeyboardButtonRequestUser(
                    request_id=3)),
                KeyboardButton(text="🤖 Получить ID бота", request_user=KeyboardButtonRequestUser(
                    request_id=4, user_is_bot=True))
            ],
            [
                KeyboardButton(text="🆔 Мой ID"),
                KeyboardButton(text="ℹ️ Помощь")
            ]
        ],
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False
    )
