import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.company_model import Base



load_dotenv()

username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
address = os.getenv('DB_ADDRESS')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')

database_url = f"postgresql+psycopg2://{username}:{password}@{address}:{port}/{database}"

engine = create_engine(database_url, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
