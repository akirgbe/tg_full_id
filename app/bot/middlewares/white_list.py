from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger

from app.config import settings
from db import db


class WhitelistMiddleware(BaseMiddleware):
    """Мидлварь: доступ только для whitelisted + суперадмин всегда имеет доступ"""

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return

        if user.id == settings.SUPER_ADMIN_ID:
            return await handler(event, data)

        if not db.is_user_whitelisted(user.id):
            logger.warning(f"Доступ запрещен: user_id={user.id}")
            return

        return await handler(event, data)
