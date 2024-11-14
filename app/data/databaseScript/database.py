import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.data.databaseScript.models import Base, UsersBase, CompaniesBase, CompanyOffersBase, CompanyRequirementsBase, \
    Message

load_dotenv()
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
address = os.getenv('DB_ADDRESS')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')

database_url = f"postgresql://{username}:{password}@{address}:{port}/{database}"
engine = create_engine(database_url, echo=True)


def create_postgresql_file():
    UsersBase()
    CompaniesBase()
    CompanyOffersBase()
    CompanyRequirementsBase()
    Message()


def run_base():

    # bind engine to Base
    Base.metadata.bind = engine
    # create tables in the database, based on the classes that inherit from Base
    Base.metadata.create_all(engine)
    # create a session maker bound to the engine
    Session = sessionmaker(bind=engine)
