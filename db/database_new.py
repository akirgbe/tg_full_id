import os

from loguru import logger
from sqlalchemy import create_engine, Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    description = Column(String(500))
    accounts = relationship("Account", back_populates="person", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    messenger_type = Column(String(50), nullable=False)
    telegram_id = Column(BigInteger)
    telegram_tag = Column(String(100))
    phone_number = Column(String(20))
    whatsapp_id = Column(String(100))
    email = Column(String(100))
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    person = relationship("Person", back_populates="accounts")


class Database:
    def __init__(self, db_name='accounts.db'):
        # Абсолютный путь к базе в папке data/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'data', db_name)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        # Используем синхронный create_engine вместо create_async_engine
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        # Создаем таблицы
        Base.metadata.create_all(self.engine)
        # Создаем синхронную сессию
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info(f"База данных подключена: {self.db_path}")

    def add_person(self, last_name, first_name, middle_name=None, description=None):
        try:
            person = Person(last_name=last_name, first_name=first_name, middle_name=middle_name,
                            description=description)
            self.session.add(person)
            self.session.commit()
            logger.info(f"Добавлен человек: {last_name} {first_name}")
            return person.id
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при добавлении человека: {e}")
            return None

    def add_account(self, person_id, messenger_type, telegram_id=None, telegram_tag=None,
                    phone_number=None, whatsapp_id=None, email=None):
        try:
            person = self.session.query(Person).filter_by(id=person_id).first()
            if not person:
                logger.error(f"Человек с ID {person_id} не найден")
                return False
            account = Account(
                messenger_type=messenger_type,
                telegram_id=telegram_id,
                telegram_tag=telegram_tag,
                phone_number=phone_number,
                whatsapp_id=whatsapp_id,
                email=email,
                person_id=person_id
            )
            self.session.add(account)
            self.session.commit()
            logger.info(f"Добавлен аккаунт: {messenger_type} для person_id={person_id}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при добавлении аккаунта: {e}")
            return False

    def find_by_phone_number(self, phone_number):
        try:
            accounts = self.session.query(Account).filter_by(phone_number=phone_number).all()
            result = {"accounts": [], "persons": []}
            for account in accounts:
                person = self.session.query(Person).filter_by(id=account.person_id).first()
                result["accounts"].append({
                    "messenger_type": account.messenger_type,
                    "telegram_id": account.telegram_id,
                    "telegram_tag": account.telegram_tag,
                    "phone_number": account.phone_number,
                    "whatsapp_id": account.whatsapp_id,
                    "email": account.email,
                    "person_id": account.person_id
                })
                result["persons"].append({
                    "id": person.id,
                    "last_name": person.last_name,
                    "first_name": person.first_name,
                    "middle_name": person.middle_name,
                    "description": person.description
                })
            logger.info(f"Найдено {len(accounts)} аккаунтов для номера {phone_number}")
            return result
        except Exception as e:
            logger.error(f"Ошибка при поиске по номеру телефона {phone_number}: {e}")
            return {"accounts": [], "persons": []}

    def delete_person(self, person_id):
        try:
            person = self.session.query(Person).filter_by(id=person_id).first()
            if not person:
                logger.error(f"Человек с ID {person_id} не найден")
                return False
            self.session.delete(person)
            self.session.commit()
            logger.info(f"Удален человек: {person_id}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при удалении человека: {e}")
            return False

    def delete_account(self, account_id):
        try:
            account = self.session.query(Account).filter_by(id=account_id).first()
            if not account:
                logger.error(f"Аккаунт с ID {account_id} не найден")
                return False
            self.session.delete(account)
            self.session.commit()
            logger.info(f"Удален аккаунт: {account_id}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при удалении аккаунта: {e}")
            return False

    def get_all_persons(self):
        try:
            return self.session.query(Person).all()
        except Exception as e:
            logger.error(f"Ошибка при получении списка людей: {e}")
            return []

    def get_all_accounts(self):
        try:
            return self.session.query(Account).all()
        except Exception as e:
            logger.error(f"Ошибка при получении списка аккаунтов: {e}")
            return []

    def close(self):
        """Закрыть соединение с базой данных"""
        self.session.close()


# Создаем экземпляр базы данных
new_db_instance = Database()
