Вот идеальная структура бота aiogram с учетом масштабируемости и будущих расширений:

## Структура проекта

```
my_bot/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── models.py
│   │   ├── crud.py
│   │   └── session.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── common.py
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── panel.py
│   │   │   └── stats.py
│   │   ├── user/
│   │   │   ├── __init__.py
│   │   │   ├── profile.py
│   │   │   └── settings.py
│   │   └── callback/
│   │       ├── __init__.py
│   │       ├── main_menu.py
│   │       └── settings.py
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── builders.py
│   │   ├── inline.py
│   │   └── reply.py
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── throttling.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── payment.py
│   │   ├── notifications.py
│   │   └── external_api.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── states.py
│   │   ├── misc.py
│   │   └── logging.py
│   └── filters/
│       ├── __init__.py
│       ├── admin.py
│       └── user.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_handlers/
│   └── test_services/
├── .env
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Ключевые файлы

### 1. app/main.py

```python
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from app.config import load_config
from app.database.session import async_session
from app.middlewares.database import DatabaseMiddleware
from app.handlers import register_handlers
from app.utils.logging import setup_logging


async def main():
    # Настройка логирования
    setup_logging()

    # Загрузка конфигурации
    config = load_config()

    # Инициализация бота и диспетчера
    storage = RedisStorage.from_url(config.redis.dsn)
    bot = Bot(token=config.bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)

    # Подключение middleware
    dp.update.middleware(DatabaseMiddleware(async_session))
    dp.message.middleware(DatabaseMiddleware(async_session))
    dp.callback_query.middleware(DatabaseMiddleware(async_session))

    # Регистрация обработчиков
    register_handlers(dp)

    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
```

### 2. app/config.py

```python
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    dsn: str


@dataclass
class RedisConfig:
    dsn: str


@dataclass
class BotConfig:
    token: str
    admin_ids: list[int]


@dataclass
class Config:
    bot: BotConfig
    database: DatabaseConfig
    redis: RedisConfig


def load_config() -> Config:
    return Config(
        bot=BotConfig(
            token=os.getenv('BOT_TOKEN'),
            admin_ids=list(map(int, os.getenv('ADMIN_IDS', '').split(',')))
        ),
        database=DatabaseConfig(
            dsn=os.getenv('DATABASE_URL')
        ),
        redis=RedisConfig(
            dsn=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        )
    )
```

### 3. app/database/models.py

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    language_code = Column(String(10))
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 4. app/handlers/__init__.py

```python
from aiogram import Dispatcher

from .start import router as start_router
from .common import router as common_router
from .admin import router as admin_router
from .user import router as user_router
from .callback import router as callback_router


def register_handlers(dp: Dispatcher):
    routers = [
        start_router,
        common_router,
        admin_router,
        user_router,
        callback_router
    ]

    for router in routers:
        dp.include_router(router)
```

### 5. app/handlers/start.py

```python
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from app.keyboards.inline import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! 🎉",
        reply_markup=main_menu_keyboard()
    )
```

### 6. app/middlewares/database.py

```python
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool):
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)
```

### 7. app/utils/states.py

```python
from aiogram.fsm.state import State, StatesGroup


class UserProfile(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_bio = State()


class Payment(StatesGroup):
    waiting_for_amount = State()
    waiting_for_confirmation = State()
```

## Дополнительные рекомендации

### 1. Docker конфигурация

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/bot/middlewares .

CMD ["python", "-m", "app.main"]
```

### 2. docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    env_file:
      - .env
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 3. .env.example

```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321

DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/dbname
REDIS_URL=redis://redis:6379/0

# Дополнительные настройки
DEBUG=True
```

## Преимущества такой структуры:

1. **Модульность** - каждый компонент в отдельном модуле
2. **Масштабируемость** - легко добавлять новые функции
3. **Тестируемость** - изолированные компоненты для тестов
4. **Поддержка БД** - асинхронная работа с базой данных
5. **Кэширование** - Redis для FSM и кэша
6. **Конфигурация** - централизованное управление настройками
7. **Логирование** - структурированное логирование
8. **Docker** - готовность к деплою

Эта структура обеспечивает чистоту кода, легкую поддержку и возможность масштабирования бота на тысячи пользователей.