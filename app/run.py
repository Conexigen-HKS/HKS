from common.auth import hash_existing_user_passwords
from data.database import get_db

db = next(get_db())

hash_existing_user_passwords(db)

#ФУНКЦИЯ ЗА ХЕШИРАНЕ НА ПАРОЛИ НА СЪЗДАДЕНИ ЮЗЪРИ КАТО АДМИН.