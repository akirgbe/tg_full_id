from .database import db_instance, Database, WhitelistUser

# Делаем основные объекты доступными при импорте модуля db
db = db_instance
