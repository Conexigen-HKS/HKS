import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.data.databaseScript.database import create_postgresql_file
from app.data.databaseScript.database import Base, UsersBase
from dotenv import load_dotenv



load_dotenv()
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
address = os.getenv('DB_ADDRESS')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')

database_url = f"postgresql://{username}:{password}@{address}:{port}/{database}"
engine = create_engine(database_url, echo=True)
create_postgresql_file()

# bind engine to Base
Base.metadata.bind = engine
# create tables in the database, based on the classes that inherit from Base
Base.metadata.create_all(engine)
# create a session maker bound to the engine
Session = sessionmaker(bind=engine)

new_user = UsersBase(
    user_username='FirstCompanyUser',
    user_hashed_password='1234',
    user_is_admin=1,
    user_role='Company',
)
new_user2 = UsersBase(
    user_username='2CompanyUser',
    user_hashed_password='1234',
    user_is_admin=0,
    user_role='Company',
)


with Session() as s:
    s.add(new_user)
    s.add(new_user2)
    s.commit()
