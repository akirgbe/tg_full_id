import os

from loguru import logger
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class WhitelistUser(Base):
    __tablename__ = 'whitelist_users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))


class Database:
    def __init__(self, db_name='whitelist.db'):
        # Абсолютный путь к базе в папке data/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'data', db_name)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info(f"База данных подключена: {self.db_path}")

    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Добавить пользователя в белый список"""
        try:
            existing_user = self.session.query(WhitelistUser).filter_by(user_id=user_id).first()
            if existing_user:
                logger.warning(f"Пользователь {user_id} уже существует")
                return False
            user = WhitelistUser(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            self.session.add(user)
            self.session.commit()
            logger.info(f"Добавлен пользователь: {user_id}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
            return False

    def remove_user(self, user_id):
        """Удалить пользователя из белого списка"""
        try:
            user = self.session.query(WhitelistUser).filter_by(user_id=user_id).first()
            if user:
                self.session.delete(user)
                self.session.commit()
                logger.info(f"Удален пользователь: {user_id}")
                return True
            logger.error(f"Пользователь {user_id} не найден")
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при удалении пользователя {user_id}: {e}")
            return False

    def is_user_whitelisted(self, user_id):
        """Проверить, есть ли пользователь в белом списке"""
        user = self.session.query(WhitelistUser).filter_by(user_id=user_id).first()
        return user is not None

    def get_all_users(self):
        """Получить всех пользователей из белого списка"""
        return self.session.query(WhitelistUser).all()

    def get_whitelist_set(self):
        """Получить белый список как set"""
        users = self.get_all_users()
        return {user.user_id for user in users}

    def close(self):
        """Закрыть соединение с базой данных"""
        self.session.close()


# Создаем экземпляр базы данных
db_instance = Database()
